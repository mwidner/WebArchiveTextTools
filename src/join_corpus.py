'''
The Corpus Slicer

Read in an CSV file of metadata describing corpus and file locations
Organize and slice the text files for analysis and further processing

Mike Widner <mikewidner@stanford.edu>
'''
import os
import re
import sys
import argparse
import pandas as pd
from string import punctuation

def get_year(value):
	'''
	Return a 4 digit year based on the given value
	'''
	match = re.search('(\d{4})', str(value))
	return(match.group(0) if match is not None and len(match.group(0)) else '')

def load_words(filename):
	'''
	Open and read a text file
	Return contents as raw string
	'''
	words = list()
	raw = str()
	try:
		fh = open(filename, "r")
		raw = fh.read()
		fh.close()
		# wordlist = nltk.corpus.PlaintextCorpusReader(SOURCE, filename)
		# words = wordlist.words(fileids=[filename])
	except OSError as err:
		print("Missing: " + filename)
	return(raw)

def clean_filename(filename):
	remove_punct_map = dict.fromkeys(map(ord, punctuation.replace('_', '') + '’'))
	return str(filename)[:100].translate(remove_punct_map).strip().replace(' ', '_')

def generate_text(df, output_dir, dirname, filename):
	'''
	Takes all words for a given slice
	Write out as a single text file
	'''
	# clean up filenames
	filename = clean_filename(filename)
	if (len(df['words']) == 0 or len(filename) == 0):
		return 	# don't write empty files

	output_path = os.path.join(output_dir, dirname)
	print("Generating {}/{}.txt".format(output_path, filename))
	if not os.path.isdir(output_path):
		os.makedirs(output_path)
	fh = open(os.path.join(output_path, filename + '.txt'), 'w')
	for row in df['words']:
		fh.write(row)
	fh.close()

def get_unique(df, key):
	'''
	Return an array of unique values for the given column name/key
	'''
	return(pd.unique(df[key].values.ravel()))

def get_options():
	parser = argparse.ArgumentParser(description='Slice corpus into files by site or author')
	parser.add_argument('-i', dest='input_dir', required=True, help='Input directory where raw corpus exists')
	parser.add_argument('-m', '--metadata', dest='metadata', required=True, help='A CSV file of metadata describing all the files')
	parser.add_argument('-o', dest='output_dir', required=True, help='Output directory for results')
	parser.add_argument('-c', '--column', dest='columns', required=True, action='append', help='The column(s) by which to slice up the corpus. Multiple columns will create sub-categories, e.g., -c col1 -col2 will slice corpus into all col2 within col1')
	return parser.parse_args()

def main():
	'''
	Process metadata
	Organize by different slicings
	'''
	options = get_options()
	df = pd.read_csv(options.metadata, quotechar='|')

	df['year'] = df['date'].apply(get_year)
	df['basename'] = df['filename'].apply(os.path.basename)
	df['words'] = df['filename'].apply(load_words)	# load words for every file

	for column in options.columns:
		# get a list of our unique values for each column
		uniques = get_unique(df, column)
		# now iterate through our desired columns and generate new text files
		for item in uniques:
			generate_text(df[df[column] == item], options.output_dir, column, item)

if __name__ == '__main__':
	if sys.version_info[0] != 3:
	    print("This script requires Python 3")
	    exit(-1)
	main()
