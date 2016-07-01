'''
Filter text output by date ranges
'''
import os
import csv
import sys
import dateutil.parser
import argparse
import metadata

settings = None

def get_settings():
  ''' Return command-line settings '''
  parser = argparse.ArgumentParser(description='Filter text corpus by date range')
  parser.add_argument('-i', dest='input', required=True, help='Input CSV of metadata describing files')
  parser.add_argument('-o', dest='output', required=True,
                   help='Output CSV for filtered results')
  parser.add_argument('-s', '--start', dest='start', help='Start date, YYYY-MM-DD format')
  parser.add_argument('-e', '--end', dest='end', help='End date, YYYY-MM-DD format')
  return parser.parse_args()

def filter_dates(metadata, start, end):
  results = list()
  if start is not None:
    start = dateutil.parser.parse(start)
  if end is not None:
    end = dateutil.parser.parse(end)
  for row in metadata:
    date = dateutil.parser.parse(row['date'])
    if date is None:
      continue
    if (start is None or start <= date) and (end is None or date <= end):
      results.append(row)
  return results

def main():
  global settings
  settings = get_settings()
  md = metadata.read_csv(settings.input)
  filtered = filter_dates(md, settings.start, settings.end)
  metadata.write_csv(settings.output, filtered)

if __name__ == '__main__':
  if sys.version_info < (3,0):
    print("This script requires Python 3")
    exit(-1)
  main()
