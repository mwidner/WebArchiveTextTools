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
  parser.add_argument('-r','--rules', dest='rules', required=True, help='A CSV file of regexes to apply to columns in the metadata')
  return parser.parse_args()

def read_csv(csvfile):
  csvdata = list()
  with open(csvfile) as f:
    reader = csv.DictReader((row for row in f if not row.startswith('#')), skipinitialspace=True, delimiter=',', quotechar="|")
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

def clean_metadata(metadata_file, rules_file):
  '''
  Replace strings in columns of metadata with regex matches
  '''
  metadata_clean = list()
  metadata = read_csv(metadata_file)
  rules = read_csv(rules_file)
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
  write_csv(metadata_file, metadata_clean)

def clean_files(metadata):
  pass

def main():
  settings = get_settings()
  clean_metadata(settings.metadata, settings.rules)
  clean_files(settings.metadata)

if __name__ == '__main__':
  if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(-1)
  main()
