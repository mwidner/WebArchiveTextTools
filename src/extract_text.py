'''
Extract text content from each website

Websites all have different structure
so we have to customize each one

But output should be same format

Mike Widner <mikewidner@stanford.edu>
'''

import os
import csv
import sys
import hashlib
import argparse
import string
from bs4 import BeautifulSoup

# Re-usable map to strip out punctuation from a string
# Convert all punctuation to underscores
remove_punct_map = dict.fromkeys(map(ord, string.punctuation.replace('_', '') + '’'))

def get_settings():
  parser = argparse.ArgumentParser(description='Write individual HTML files from HTML files')
  parser.add_argument('-i', dest='input_dir', required=True, help='Input directory where site crawls exist')
  parser.add_argument('-s', '--sites', dest='site_info', required=True, help='A CSV file of crawled sites, metadata, and DOM structure for extraction')
  parser.add_argument('-o', dest='output_dir', required=True,
                   help='Output directory for results')
  parser.add_argument('-w', '--words', dest='word_count', required=False, help='Minimum word count to save. Texts below this threshold will be ignored.')
  return parser.parse_args()

def get_site_info(csvfile):
  site_info = list()
  with open(csvfile) as f:
    reader = csv.DictReader(f, delimiter=',', quotechar="'")
    for row in reader:
      site_info.append(row)
  return site_info

def find_files(walkdir, paths_to_parse):
  '''
  Find files from which to extract text
  '''
  files_to_parse = list()

  for root, subdirs, files in os.walk(walkdir):
    # grab just the path(s) we want to parse
    # if none defined, get all
    # if not len(paths_to_parse) or root.replace(walkdir,'') in paths_to_parse or subdirs in paths_to_parse:
    for filename in files:
      files_to_parse.append(os.path.join(root, filename))
  return files_to_parse

def generate_unique_filename(corpus_dir, filename, title):
  # create a unique output filename based on doc title and input file
  filename = os.path.basename(filename)
  unique = title[:100].lower().translate(remove_punct_map).strip().replace(' ', '_')
  unique += '_'
  unique += hashlib.md5(filename.encode('utf-8')).hexdigest()
  return os.path.join(corpus_dir, unique)

def clean_string(string):
  # Clean up a string of newlines, etc.
  return string.replace('\n', '')

def extract_text(site_info, input_file, corpus_dir, word_count=0):
  '''
  Extract the actual text from the HTML
  Write out file with text content
  Return extracted metadata about text
  '''
  results = dict()
  try:
    soup = BeautifulSoup(open(input_file, encoding="utf-8"), 'html.parser')
  except UnicodeDecodeError as err:
    # print(input_file + ' is not UTF8', err)
    return

  if soup is None:
    return

  # Fields in CSV with BeautifulSoup select() options
  for item in ['title','date','author','content']:
    results[item] = ''
    if (not len(site_info[item])):
      continue
    contents = soup.select(site_info[item])
    if contents is not None and len(contents):
      # Assume only the first result is relevant
      # BS4 returns a list of results even if only 1 found
      results[item] = clean_string(contents[0].getText())

  results['word_count'] = len(results['content'].split())
  results['filename'] = generate_unique_filename(corpus_dir, input_file, results['title'])
  if os.path.isfile(results['filename']):
    return

  if (len(results['title']) and results['word_count'] >= int(word_count)):
    with open(results['filename'], 'w') as content:
      content.write(str(results['content']))
    return results
  return None

def get_filenames(input_dir, site_info, corpus_dir):
  '''
  Find matching directories that have HTML to parse
  Get a list of files from them
  '''
  text = list()
  # warcat extracts to subdirs by site URL
  walkdir = os.path.join(os.path.abspath(input_dir), site_info['url'])
  # NB: paths in CSV should not have a trailing slash
  paths_to_parse = site_info['paths'].split(',')
  files_to_parse = find_files(walkdir, paths_to_parse)
  return files_to_parse

def get_metadata_filename(path):
  filename = os.path.join(path, 'metadata.csv')
  if (not os.path.isfile(filename)):
    with open(filename, 'w') as csvfile:
      metadata = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_ALL)
      metadata.writerow(['site', 'title', 'date', 'author', 'filename', 'word_count'])
  return filename

def write_metadata(path, results):
  metadata_filename = get_metadata_filename(path)
  # map to remove all punctuation from filenames
  with open(metadata_filename, 'a') as csvfile:
    metadata = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_ALL)
    try:
      metadata.writerow([results['site'], results['title'], results['date'], results['author'], results['filename'], results['word_count']])
    except KeyError as err:
      print('Could not write row. Missing data: ', results, err)

def main():
  settings = get_settings()
  site_info = get_site_info(settings.site_info)

  # Set up the output directories
  corpus_dir = os.path.join(settings.output_dir, 'text')
  if (not os.path.isdir(corpus_dir)):
    os.makedirs(corpus_dir)

  for site in site_info:
    count = 0
    # NB: Will clobber existing results if multiple site definitions
    print("Processing {}".format(site['name']))
    files = get_filenames(settings.input_dir, site, corpus_dir)
    for filename in files:
      results = extract_text(site, filename, corpus_dir, settings.word_count)
      if (results is not None):
        count += 1
        results['site'] = site['name']
        write_metadata(settings.output_dir, results)
    print("{} total files. {} processed.".format(len(files), count))


if __name__ == '__main__':
  if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(-1)
  main()
