'''
Download speeches and metadata from Elysee.fr

'''

import re
import csv
import urllib.request
import argparse
from bs4 import BeautifulSoup

def parse_arguments():
  parser = argparse.ArgumentParser(description='Download metadata and speech text from Elyssee.fr')
  parser.add_argument('-u', '--url', help='URL to scrape')
  parser.add_argument('-o', dest='output_dir', required=True,
                     help='Output directory')
  args = parser.parse_args()
  return args

def get_results(url):
  '''
  Get the results listing for downloading actual pages
  '''
  # li class="page-next" has link to next page
  # gone on last page
  # a class="main-link" points to the page content itself
  page = urllib.request.urlopen(url)
  soup = BeautifulSoup(page.read(), 'html.parser')
  print(soup)
  for block in soup.find_all('div', attrs={'class': 'block-content'}):
    date = block.find('div', attrs={'class': 'date'}).content
    if date.startswith('Publié le '):
      date = date[:10]
    themes = block.find('div', attrs={'class': 'themes'}).content
    print(date, themes)

def get_page():
  '''
  Get the text and metadata
  '''
  # div.article div.text
  #   span.article-date
  #   div.themes
  #   p
  pass


def write_results():
  pass

def main():
  args = parse_arguments()
  get_results(args.url)


if __name__ == '__main__':
  # nothing specific to Python 3 in here
  # if sys.version_info[0] != 3:
  #   print("This script requires Python 3")
  #   exit(-1)
  main()
