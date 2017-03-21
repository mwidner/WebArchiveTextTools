import os
import sys
import pandas as pd
import argparse


def get_settings():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='input', help='Input CSV of word frequencies', required=True)
    parser.add_argument('-w', dest='wordpairs', action='append', help='Word pair separated, by commas, to combine', required=True)
    return parser.parse_args()


def main()
  settings = get_settings()
  df = pd.read_csv(settings.input)
  for pair in settings.wordpairs:
    base, variant = pair.split(',')
    df[]


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        print("This script requires Python 3")
        exit(-1)
    main()
