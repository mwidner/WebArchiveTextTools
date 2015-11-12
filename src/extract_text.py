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
remove_punct_map = dict.fromkeys(map('_', string.punctuation + '’'))

def get_settings():
  parser = argparse.ArgumentParser(description='Write individual HTML files from HTML files')
  parser.add_argument('-i', dest='input_dir', required=True, help='Input directory where site crawls exist')
  parser.add_argument('-s', '--sites', dest='site_info', required=True, help='A CSV file of crawled sites, metadata, and DOM structure for extraction')
  parser.add_argument('-o', dest='output_dir', required=True,
                   help='Output directory for results')
  return parser.parse_args()

def get_site_info(csvfile):
  site_info = list()
  with open(csvfile) as f:
    reader = csv.DictReader(f, delimiter=',', quotechar="'")
    for row in reader:
      site_info.append(row)
  return site_info

def find_files(root, subdirs, files):
  '''
  Find files to parse
  '''
  files_to_parse = list()
  for subdir in subdirs:
    # Get all files in the sub directories, too
    path = os.path.join(root, subdir)
    files.extend([os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
  for filename in files:
    files_to_parse.append(os.path.join(root,filename))
  return files_to_parse

def generate_unique_filename(filename, title):
  # create a unique output filename based on doc title and input file
  filename = os.path.basename(filename)
  unique = filename.lower().translate(remove_punct_map).strip().replace(' ', '_')
  unique += '_'
  unique += hashlib.md5(filename.encode('utf-8')).hexdigest()
  return unique

def extract_text(site_info, input_file, corpus_dir):
  '''
  Extract the actual text from the HTML
  Write out file with text content
  '''
  results = dict()
  soup = BeautifulSoup(open(input_file), 'html.parser')
  if soup is None:
    return
  if soup.title is not None:
    results['title'] = soup.title.contents[0]
    print(results['title'])
    # clean up the title
    results['filename'] = os.path.join(corpus_dir, generate_unique_filename(input_file, results['title']))
  else:
    results['title'] = ''
    results['filename'] = ''
  # Fields in CSV with BeautifulSoup select() options
  for item in ['date','author','content']:
    results[item] = ''
    if (not len(site_info[item])):
      continue
    contents = soup.select(site_info[item])
    if contents is not None and len(contents):
      # Assume only the first result is relevant
      # BS4 returns a list of results even if only 1 found
      results[item] = contents[0].getText()
  if (len(results['title'])):
    with open(results['filename'], 'w') as content:
      content.write(str(results['content']))
  return results


def get_texts(input_dir, site_info, corpus_dir):
  '''
  Find matching directories that have HTML to parse
  Get a list of files from them
  Then extract text content, with metadata
  Return results
  '''
  text = list()
  # warcat extracts to subdirs by site URL
  walkdir = os.path.join(os.path.abspath(input_dir), site_info['url'])
  # NB: paths in CSV should not have a trailing slash
  paths_to_parse = site_info['paths'].split(',')
  for root, subdirs, files in os.walk(walkdir):
    # grab just the path(s) we want to parse
    if root.replace(walkdir,'') in paths_to_parse or subdirs in paths_to_parse:
        files_to_parse = find_files(root, subdirs, files)
  for filename in files_to_parse:
    # if (not filename.endswith('actualites_immigration-reunion_travail_20150916') ):
    #   continue
    # BUG: Possible duplicate files may overwrite existing content
    text.append(extract_text(site_info, filename, corpus_dir))
  return text

def write_metadata(path, results):
  # map to remove all punctuation from filenames
  with open(os.path.join(path, 'metadata.csv'), 'w') as csvfile:
    metadata = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_ALL)
    metadata.writerow(['site', 'title', 'date', 'author', 'filename'])
    for site, rows in results.items():
      for row in rows:
        try:
          metadata.writerow([site, row['title'], row['date'], row['author'], row['filename']])
        except KeyError as err:
          print('Could not write row. Missing data: ', row, err)

def main():
  results = dict()
  settings = get_settings()
  site_info = get_site_info(settings.site_info)

  # Set up the output directories
  corpus_dir = os.path.join(settings.output_dir, 'text')
  if (not os.path.isdir(corpus_dir)):
    os.makedirs(corpus_dir)

  for site in site_info:
    # NB: Will clobber existing results if multiple site definitions
    results[site['name']] = get_texts(settings.input_dir, site, corpus_dir)
  write_metadata(settings.output_dir, results)

if __name__ == '__main__':
  if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(-1)
  main()
