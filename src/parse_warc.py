#
# Extract HTML pages from WARC
#
# Mike Widner <mikewidner@stanford.edu>
#

import os
import csv
import argparse
from urllib.parse import urlparse
import warcat.model


parser = argparse.ArgumentParser(description='Write individual HTML files from WARC')
parser.add_argument('-i', dest='input_file', required=True, help='Input file')
parser.add_argument('-o', dest='output_dir', required=True,
                   help='Output directory')
args = parser.parse_args()

warc = warcat.model.WARC()
warc.load(args.input_file)

print('Records:', len(warc.records))
for record in warc.records:
  if (record.warc_type == 'response' or 'request') and (record.header.fields['Content-Type'].startswith('application/http')):
    try:
      url = urlparse(record.header.fields['WARC-Target-URI'])
    except KeyError as err:
      print('Cannot find Target-URI in', record.header.fields)
      continue
    path = args.output_dir + '/' + url.netloc
    if (not os.path.isdir(path)):
      os.makedirs(path)
    print(record.header.fields['WARC-Target-URI'])
    if (len(url.path)):
      f = open(path + url.path, 'wb')
      for byte in record.content_block.iter_bytes():
        f.write(byte)
