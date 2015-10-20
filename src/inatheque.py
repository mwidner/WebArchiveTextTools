'''
Download metadata tables from inatheque.ina.fr

Mike Widner <mikewidner@stanford.edu>
'''

from bs4 import BeautifulSoup
import requests
import argparse
import csv
import re

'''
http://inatheque.ina.fr/Ina/ws/dlr/dlweb/general/ResultSet?rpp=-50&upp=0&w=NATIVE%28%27ITOUSTEXT+ph+like+%27%27Marine+Le+Pen%27%27+and+DATDIF+%3E+%27%2701%2F01%2F2014%27%27+and+GEN+ph+words+%27%27Marine+Le+Pen%27%27%27%29&r=1
'''

parser = argparse.ArgumentParser(description='Download metadata from Inatheque')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--url', help='URL to scrape')
group.add_argument('-i', dest='input_file', help='Input file' )
parser.add_argument('-o', dest='output_file', required=True,
                   help='Output file')

args = parser.parse_args()
with open(args.output_file, 'w') as csvfile:
  metadata = csv.writer(csvfile)
  if (args.url):
    req = requests.get(args.url)
    text = req.text
  else:
    f = open(args.input_file, 'r', encoding='latin-1')
    text = f.read()
    f.close()
  soup = BeautifulSoup(text, 'html.parser')
  headers = soup.find_all(attrs={'class': 'header-select-title'})
  metadata.writerow([column.string for column in headers])
  rows = soup.find_all(attrs={'class': re.compile("result_line_?")})
  for row in rows:
    output = list()
    for column in row.find_all('div'):
      # Indices have no id, we don't want them anyway
      if column.has_attr('id'):
        if len(column.contents) == 1:
          output.append(column.string.strip())
        else:
          if (column.a is not None):
            output.append(column.a['href'])
          elif (column.strong is not None):
            output.append(column.strong.string.strip())
    metadata.writerow(output)
