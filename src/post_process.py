'''
Post-processing of metadata and texts for after extraction from warcs
Will match regexes to strings in the given column of the metadata
If any groups found, will replace the value with findings
Otherwise, will remove the regex from the string
'''

import os
import re
import sys
import csv
import argparse
import datetime

def get_settings():
  parser = argparse.ArgumentParser(description='Clean up metadata CSV and text files')
  parser.add_argument('-i','--input', dest='metadata', required=True, help='A CSV file of metadata about text files')
  parser.add_argument('-s','--settings', dest='rules', help='A CSV file of regexes to apply to columns in the metadata')
  parser.add_argument('-o','--output', dest='output', required=True, help='Filename for metadata output')
  parser.add_argument('-c', '--convert', dest='convert', action='store_true', help='Convert dates from natural language to numbers')
  parser.add_argument('-r', '--rename', dest='rename', action='store_true', help='Move files based on metadata. Pattern: author-date-title.txt')
  parser.add_argument('-d', '--date_format', dest='date_format', help='Reformat dates using strftime() format codes')
  return parser.parse_args()

def read_csv(csvfile):
  csvdata = list()
  with open(csvfile) as f:
    reader = csv.DictReader((row for row in f if not row.startswith('#')), skipinitialspace=True, delimiter=',', quotechar='|')
    csvdata = [row for row in reader]
  return csvdata

def write_csv(filename, data):
  if not len(data):
    return
  values = [list(row.values()) for row in data]
  with open(filename, 'w') as csvfile:
    metadata = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_ALL)
    metadata.writerow(list(data[0].keys())) # header
    metadata.writerows(values) # values

def remove_whitespace(metadata):
  for row in metadata:
    for col in row:
      row[col] = row[col].strip()

def clean_metadata(metadata, rules):
  '''
  Replace strings in columns of metadata with regex matches
  '''
  metadata_clean = list()
  remove_whitespace(metadata)
  for row in metadata:
    for rule in rules:
      col = rule['column']
      if col in row:
        pattern = re.compile(rule['regex'])
        match = pattern.search(row[col])
        if match:
          try:
            replace = match.group(1)
          except IndexError as err:
            # No group, just strip the regex
            replace = re.sub(rule['regex'], '', row[col])
          finally:
            row[col] = replace
    metadata_clean.append(row)
  return metadata_clean

def convert_dates(metadata, date_format = None):
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
  if date_format is None:
    date_format = '%Y-%m-%d'
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
  return metadata

def reformat_dates(metadata, date_format):
  '''
  Reformat dates using a strftime() code
  '''
  from dateutil import parser
  for row in metadata:
    try:
      date = parser.parse(row['date'], dayfirst = True)
    except ValueError as err:
      print(row, row['date'], err)
    else:
      row['date'] = date.strftime(date_format)
  return metadata

def rename_files(metadata):
  '''
  Rename each file to match the metadata
  author-date-title.txt
  Update metadata sheet to match
  '''
  from extract_text import strip_string
  for row in metadata:
    values = list()
    filename = ''
    for item in ['author', 'date', 'title']:
      # remove punctuation and spaces for filenames
      # truncate over-long strings
      values.append(strip_string(row[item])[:100])
    filename = '_'.join(values) + '.txt'
    if len(filename):
      path = os.path.dirname(row['filename'])
      filename = os.path.join(path, filename)
      try:
        os.rename(row['filename'], filename)
      except OSError as err:
        print("Error renaming {}: {}".format(row['filename'], err))
    else:
      raise ValueError('No new filename generated!')
    row['filename'] = filename
  return metadata

def main():
  settings = get_settings()
  metadata = read_csv(settings.metadata)
  if settings.rules:
    rules = read_csv(settings.rules)
    metadata = clean_metadata(metadata, rules)
  if settings.date_format:
    # Needs to come before date conversion to ensure consistent month/day ordering
    metadata = reformat_dates(metadata, settings.date_format)
  if settings.convert:
    metadata = convert_dates(metadata, settings.date_format)
  if settings.rename:
    metadata = rename_files(metadata)
  write_csv(settings.output, metadata)


if __name__ == '__main__':
  if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(-1)
  main()
