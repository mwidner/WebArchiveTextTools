'''
Extract date, title, and link to media items
Requires a CSV file with selectors for each bit of metadata

'''

import os
import csv
import sys
import argparse
from bs4 import BeautifulSoup

def get_options():
  parser = argparse.ArgumentParser(description='Extract date, title, and link to video assets from MLP site')
  parser.add_argument('-i', dest='input_dir', required=True, help='Input directory where site crawls exist')
  parser.add_argument('-o', dest='output_file', required=True, help='Output file for results')
  parser.add_argument('-s', '--sites', dest='sites', required=True, help='A CSV file of crawled sites, metadata, and DOM structure for extraction')
  return parser.parse_args()

def get_site_info(csvfile):
  site_info = list()
  with open(csvfile) as f:
    reader = csv.DictReader((row for row in f if not row.startswith('#')), skipinitialspace=True, delimiter=',', quotechar="'")
    site_info = [row for row in reader]
  return site_info

def read_data(path):
  '''
  Join all index.html files in path into a single string
  Skip 'feed' directories to avoid duplicates
  Return that string for processing
  '''
  data = ''
  for root, subdirs, files in os.walk(path):
    for filename in files:
      if filename.startswith('_index_'):
        with open(os.path.join(root, filename)) as f:
          data += f.read()
    for subdir in subdirs:
      if subdir != 'feed':
        data += read_data(os.path.join(root, subdir))
  return data

def parse_data(site, data, columns):
  '''
  Extract all relevant data found in HTML
  '''
  results = list()
  soup = BeautifulSoup(data, 'html.parser')
  # for item in soup.select('div#main div.data'):
  for item in soup.select(site['item']):
    result = dict()
    item_soup = BeautifulSoup(str(item), 'html.parser')
    for metadata in columns:
      selection = item_soup.select(site[metadata])
      if len(selection):
        if metadata != 'link':
          result[metadata] = selection[0].get_text().strip()
        else:
          # Links are a special case; we want href, not text
          result[metadata] = selection[0]['href']
    results.append(result)
  return results

def write_data(site, data, output_file, columns):
  '''
  Write CSV of results
  '''
  os.makedirs(os.path.dirname(output_file), exist_ok = True)
  needs_header = False
  if (not os.path.isfile(output_file)):
    needs_header = True
  with open(output_file, 'a') as csvfile:
    results = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL)
    if (needs_header):
      results.writerow(columns)
      needs_header = False
    for row in data:
      data_row = [row[col] for col in columns]
      results.writerow(data_row)

def main():
  columns = ['title','date','link','description']
  options = get_options()
  site_info = get_site_info(options.sites)
  for site in site_info:
    raw_data = read_data(os.path.join(options.input_dir, site['path']))
    parsed_data = parse_data(site, raw_data, columns)
    write_data(site['path'], parsed_data, options.output_file, columns)

if __name__ == '__main__':
  if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(-1)
  main()
