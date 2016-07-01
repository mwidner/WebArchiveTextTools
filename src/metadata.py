'''
Library for handling the reading/writing of CSV metadata
'''

import os
import sys
import csv

def read_csv(csvfile, quotechar = '|'):
  csvdata = list()
  with open(csvfile) as f:
    reader = csv.DictReader((row for row in f if not row.startswith('#')), skipinitialspace=True, delimiter=',', quotechar=quotechar)
    csvdata = [row for row in reader]
  return csvdata

def write_csv(filename, data, quotechar = '|'):
  if not len(data):
    return
  values = [list(row.values()) for row in data]
  with open(filename, 'w') as csvfile:
    metadata = csv.writer(csvfile, quotechar=quotechar, quoting=csv.QUOTE_ALL)
    metadata.writerow(list(data[0].keys())) # header
    metadata.writerows(values) # values
