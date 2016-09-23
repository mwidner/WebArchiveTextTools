'''
Extract date, title, and link to all MLP speeches
'''

import os
import csv
import sys
import argparse
from bs4 import BeautifulSoup

def get_options():
  parser = argparse.ArgumentParser(description='Extract date, title, and link to video assets from MLP site')
  parser.add_argument('-i', dest='input_dir', action='append', required=True, help='Input directories where index.html files exist')
  parser.add_argument('-o', dest='output_file', required=True, help='Output file for results')
  parser.add_argument('-b', dest='base_path', required=False, help='An optional base path to prepend to all paths')
  return parser.parse_args()

def read_data(path):
  '''
  Join all index.html files in path into a single string
  Return that string for processing
  '''
  data = ''
  for root, subdirs, files in os.walk(path):
    if 'index.html' in files:
      with open(os.path.join(root, 'index.html')) as f:
        data += f.read()
    for subdir in subdirs:
      if subdir != 'feed':
        data += read_data(os.path.join(root, subdir))
  return data

def parse_data(data):
  '''
  Extract all relevant data found in HTML
  '''
  results = list()
  soup = BeautifulSoup(data, 'html.parser')
  for item in soup.select('div#main div.data'):
    date = None
    desc = None
    # Relying on uniqueness of tags within each data item
    title = item.h2.text
    if ('time' in item.span['class']):
      date = item.span.text
    link = item.a['href']
    if ('desc' in item.p['class']):
      desc = item.p.text
    if (date):
      row = [title, date, link, desc]
      results.append(row)
  return results

def write_data(data, output_file):
  '''
  Write CSV of results
  '''
  os.makedirs(os.path.dirname(output_file), exist_ok = True)
  header = None
  if (not os.path.isfile(output_file)):
    header = ['title', 'date', 'link', 'description']
  with open(output_file, 'a') as csvfile:
    results = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL)
    if (header):
      results.writerow(header)
    for row in data:
      results.writerow(row)

def main():
  options = get_options()
  for path in options.input_dir:
    if len(options.base_path):
      path = os.path.join(options.base_path, path)
    raw_data = read_data(path)
    parsed_data = parse_data(raw_data)
    write_data(parsed_data, options.output_file)

if __name__ == '__main__':
  if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(-1)
  main()
