'''
Read subtitle files
Write as plain text
'''

import pysrt
import argparse


parser = argparse.ArgumentParser(description='Extract text from subtitle files')
parser.add_argument('-i', dest='input_file', required=True, help='Input file' )
parser.add_argument('-o', dest='output_file', required=True,
                   help='Output file')
args = parser.parse_args()

subs = pysrt.open(args.input_file)
with open(args.output_file, 'w') as f:
  f.write(subs.text)

