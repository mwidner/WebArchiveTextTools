'''
Convert French dates into numbers
'''

import os
import re
import csv
import sys
import argparse
import datetime
from dateutil import parser

def get_options():
  parser = argparse.ArgumentParser(description='Convert date strings into numbers')
  parser.add_argument('-i', dest='input', required=True, help='Input file of metadata as CSV')
  parser.add_argument('-o', dest='output', required=True, help='Output file for results')
  parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Verbose output')
  parser.add_argument('-f', '--format', dest='format', required=True, help='Format for date string')
  return parser.parse_args()

def read_metadata(filename):
  metadata = list()
  with open(filename) as f:
    reader = csv.DictReader((row for row in f if not row.startswith('#')), skipinitialspace=True, delimiter=',', quotechar='|')
    metadata = [row for row in reader]
  return metadata

def convert_dates(metadata, date_format):
  ''' Could conceivably make these replacements configurable '''
  months = {
    'janvier': 1,
    'jan': 1,
    'février': 2,
    'fév': 2,
    'mars': 3,
    'mar': 3,
    'avril': 4,
    'avr': 4,
    'mai': 5,
    'juin': 6,
    'juillet': 7,
    'juil': 7,
    'août': 8,
    'septembre': 9,
    'sept': 9,
    'octobre': 10,
    'oct': 10,
    'novembre': 11,
    'nov': 11,
    'décembre': 12,
    'déc': 12,
  }
  date_patterns = dict()
  for month in months.keys():
    date_patterns[month] = re.compile('(\d+)\s*(' + month + ')\s*(\d+)', re.IGNORECASE)
  for row in metadata:
    for month in date_patterns.values():
      match = month.search(row['date'])
      if match:
        day = int(match.group(1))
        month = int(months[match.group(2).lower()])
        year = int(match.group(3))
        if len(str(year)) < 4 and year < 17:
          year += 2000
        date = datetime.date(year, month, day)
        row['date'] = date.strftime(date_format)
    # Now ensure all numeric dates are in desired format
    try:
      date = parser.parse(row['date'])
      row['date'] = date.strftime(date_format)
    except ValueError as err:
      print('Cannot parse {}: {}'.format(row['date'], err))
  return metadata

def write_metadata(metadata, filename):
  if not len(metadata):
    return
  values = [list(row.values()) for row in metadata]
  with open(filename, 'w') as f:
    csvfile = csv.writer(f, quotechar='|', quoting=csv.QUOTE_ALL)
    csvfile.writerow(list(metadata[0].keys())) # header
    csvfile.writerows(values) # values

def main():
  options = get_options()
  metadata = read_metadata(options.input)
  metadata = convert_dates(metadata, options.format)
  write_metadata(metadata, options.output)

if __name__ == '__main__':
  if sys.version_info[0] != 3:
    print("This program requires Python 3.")
    exit(-1)
  main()
