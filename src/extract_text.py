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
import argparse
from bs4 import BeautifulSoup

def get_settings():
  parser = argparse.ArgumentParser(description='Write individual HTML files from WARC')
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
    # crawl files have a consistent naming structure
    if os.path.basename(filename).startswith('_index_'):
      files_to_parse.append(os.path.join(root,filename))
  return files_to_parse

def extract_text(site_info, filename):
  '''
  Extract the actual text from the HTML
  '''
  results = dict()
  soup = BeautifulSoup(open(filename), 'html.parser')
  results['filename'] = filename
  results['title'] = soup.title.contents[0]
  # Fields in CSV with BeautifulSoup select() options
  for item in ['date','author','content']:
    contents = soup.select(site_info[item])
    if len(contents):
      # Assume only the first result is relevant
      # BS4 returns a list of results even if only 1 found
      results[item] = contents[0].getText()
  return results


def get_texts(path, site_info):
  '''
  Find matching directories that have HTML to parse
  Get a list of files from them
  Then extract text content, with metadata
  Return results
  '''
  text = list()
  walkdir = os.path.join(os.path.abspath(path), site_info['url'])
  # Make sure paths don't have a trailing slash in the CSV
  paths_to_parse = site_info['paths'].split(',')
  for root, subdirs, files in os.walk(walkdir):
    # grab just the path(s) we want to parse
    if root.replace(walkdir,'') in paths_to_parse or subdirs in paths_to_parse:
        files_to_parse = find_files(root, subdirs, files)
  for filename in files_to_parse:
    text.append(extract_text(site_info, filename))
  return text

def write_results(path, results):
  if (not os.path.isdir(path)):
    os.makedirs(path)
  with open(os.path.join(path, 'metadata.csv'), 'w') as csvfile:
    metadata = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_ALL)
    metadata.writerow(['site', 'title', 'date', 'author', 'filename'])
    for site, rows in results.items():
      for row in rows:
        filename = os.path.join(path, row['title'])
        metadata.writerow([site, row['title'], row['date'], row['author'], filename])
        with open(filename, 'w') as content:
          content.write(str(row['content']))

def main():
  settings = get_settings()
  site_info = get_site_info(settings.site_info)
  results = dict()
  for site in site_info:
    results[site['name']] = get_texts(settings.input_dir, site)
  write_results(settings.output_dir, results)

if __name__ == '__main__':
  if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(-1)
  main()
