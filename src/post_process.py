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

def get_settings():
  parser = argparse.ArgumentParser(description='Clean up metadata CSV and text files')
  parser.add_argument('-m','--metadata', dest='metadata', required=True, help='A CSV file of metadata about text files')
  parser.add_argument('-c','--clean', dest='rules', required=True, help='A CSV file of regexes to apply to columns in the metadata')
  parser.add_argument('-r', '--rename', dest='rename', action='store_true', help='Move files based on metadata. Pattern: author-date-title.txt')
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
  with open(filename + '.clean', 'w') as csvfile:
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
  rules = read_csv(settings.rules)
  metadata = clean_metadata(metadata, rules)
  if settings.rename:
    metadata = rename_files(metadata)
  write_csv(settings.metadata, metadata)


if __name__ == '__main__':
  if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(-1)
  main()
