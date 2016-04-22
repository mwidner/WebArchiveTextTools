'''
The Corpus Slicer

Read in an CSV file of metadata describing corpus and file locations
Organize and combine the text files for analysis and further processing

Mike Widner <mikewidner@stanford.edu>
'''
import os
import re
import sys
import argparse
import pandas as pd
from string import punctuation
from collections import defaultdict

verbose = False

def get_options():
	parser = argparse.ArgumentParser(description='Slice corpus into files by site or author')
	parser.add_argument('-i', dest='input_dir', required=True, help='Input directory where raw corpus exists')
	parser.add_argument('-m', '--metadata', dest='metadata', required=True, help='A CSV file of metadata describing all the files')
	parser.add_argument('-o', dest='output_dir', required=True, help='Output directory for results')
	parser.add_argument('-c', '--column', dest='columns', required=True, action='append', help='The column(s) by which to slice up the corpus. Multiple columns will create sub-categories, e.g., -c col1 -col2 will slice corpus into all col2 within col1')
	parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Verbose output')
	return parser.parse_args()

def get_year(value):
	'''
	Return a 4 digit year based on the given value
	'''
	match = re.search('(\d\d\d\d)$', str(value))
	return(match.group(1) if match is not None else None)

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
	return str(filename).translate(remove_punct_map).strip().replace(' ', '_')[:100]

def get_uniques(df, key):
	'''
	Return an array of unique values for the given column name/key
	'''
	return(pd.unique(df[key].values.ravel()))

def write_text(df, output_path, filename):
	'''
	Write out all words in a df as a single text file
	'''
	# clean up filenames
	filename = clean_filename(filename)
	if (len(df['words']) == 0 or len(filename) == 0):
		return 	# don't write empty files

	if verbose:
		print("Generating {}/{}.txt".format(output_path, filename))
	if not os.path.isdir(output_path):
		try:
			os.makedirs(output_path)
		except OSError as err:
			print("Cannot write {}: {}".format(output_path, err))
			return
	fh = open(os.path.join(output_path, filename + '.txt'), 'w')
	for row in df['words']:
		fh.write(row)
	fh.close()

def join_texts(df, columns, path, join_with = None):
	'''
	Generate a single text of all the words in the given column
	Pass another df as join_with to perform a join
	'''
	for index, column in enumerate(columns):
		path = os.path.join(path, column)

		for item in get_uniques(df, column):
			df_item = df[df[column] == item]

			if join_with is not None and not df_item.empty:
				df_left = df[df[join_with['column']] == join_with['item']]
				df_item = pd.merge(df_left, df_item)

			if index < len(columns) - 1:
				join_texts(df, columns[index + 1:], os.path.join(path, str(item)), {'column': str(column), 'item': str(item)})

			# if len(df_item.index):
			write_text(df_item, path, item)



def main():
	'''
	Process metadata
	Organize by different slicings
	'''
	options = get_options()
	if options.verbose:
		verbose = True
	df = pd.read_csv(options.metadata, quotechar='|')

	df['year'] = df['date'].apply(get_year)
	df['basename'] = df['filename'].apply(os.path.basename)
	df['words'] = df['filename'].apply(load_words)	# load words for every file
	join_texts(df, options.columns, options.output_dir)


if __name__ == '__main__':
	if sys.version_info[0] != 3:
		print("This program requires Python 3.")
		exit(-1)
	main()
