'''
Deletes files not in a list of metadata
'''

import os
import sys
import metadata
import argparse
import unicodedata

settings = None

def get_settings():
  ''' Return command-line settings '''
  parser = argparse.ArgumentParser(description='Delete files in corpus not listed in metadata')
  parser.add_argument('-i', dest='input', required=True, help='Input CSV of metadata describing files')
  parser.add_argument('-t', '--test', dest='test', action='store_true', help='Do a test run; only list files to be deleted.')
  return parser.parse_args()

def delete_files(md):
  directories = list()
  all_files = list()
  for row in md:
    directories.append(os.path.dirname(row['filename']))
    all_files.append(row['filename'])
  directories = frozenset(directories)
  all_files = frozenset(all_files)

  for basedir in directories:
    for root, subdirs, files in os.walk(basedir):
      for filename in files:
        # Note: Mac OS X stores files as fully decomposed unicode
        # whereas our metadata strings are 'normal form composed'
        # @see: http://stackoverflow.com/questions/16467479/normalizing-unicode
        # @see: http://apple.stackexchange.com/questions/10476/how-to-enter-special-characters-so-that-bash-terminal-understands-them
        path = unicodedata.normalize('NFC', os.path.join(root, filename))
        if path not in all_files:
          if settings.test:
            print(path)
          else:
            print('Removing {}'.format(path))
            os.remove(path)
    if not os.listdir(root):
      # remove empty directories
      if settings.test:
        print(root)
      else:
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
