'''
Deletes files not in a list of metadata
'''

import os
import sys
import metadata
import argparse

settings = None

def get_settings():
  ''' Return command-line settings '''
  parser = argparse.ArgumentParser(description='Delete files in corpus not listed in metadata')
  parser.add_argument('-i', dest='input', required=True, help='Input CSV of metadata describing files')
  return parser.parse_args()

def delete_files(md):
  directories = list()
  all_files = list()
  for row in md:
    directories.append(os.path.dirname(row['filename']))
    all_files.append(row['filename'])
  directories = set(directories)

  for basedir in directories:
    for root, subdirs, files in os.walk(basedir):
      for filename in files:
        path = os.path.join(root, filename)
        if filename not in all_files:
          os.remove(path)
    if not os.listdir(root):
      # remove empty directories
      os.rmdir(root)

def main():
  global settings
  settings = get_settings()
  md = metadata.read_csv(settings.input)
  delete_files(md)

if __name__ == '__main__':
  if sys.version_info < (3,0):
    print("This script requires Python 3")
    exit(-1)
  main()
