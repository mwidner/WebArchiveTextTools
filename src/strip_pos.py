'''
Strip parts of speech we don't want
preps corpus for topic modelling, other processing

mlw
'''

import os
import csv
from bs4 import BeautifulSoup

BASE_DIR = '/Users/widner/Projects/DLCL/Alduy/Rhetoric_of_LePen/'
INPUT_DIR = BASE_DIR + 'results/treetagger/year/'
OUTPUT_DIR = BASE_DIR + 'results/stripped/year/'

if not os.path.isdir(OUTPUT_DIR):
	os.makedirs(OUTPUT_DIR)

filelist = csv.writer(open(OUTPUT_DIR + 'filelist.csv', 'w'))
filelist.writerow(["filename","words"])

for filename in os.listdir(INPUT_DIR):
	print(filename)
	fh = open(INPUT_DIR + filename, "r")
	text = fh.read()
	fh.close()
	soup = BeautifulSoup(text)
	# nouns = list()
	# adjectives = list()
	words = list()
	for phrase in soup.find_all(['s']):
		for line in phrase.get_text().split('\n'):
			tokens = line.split('\t')
			if len(tokens) < 3:
				continue
			choice = list()
			choice = tokens[2].split('|')
			if len(choice) > 1:
				tokens[2] = choice[0]	# default to the first option
			# if tokens[1] == 'NOM':
				# nouns.append(tokens[2])
			if tokens[1] == 'NUM' or len(tokens[2]) == 0:
				words.append(tokens[0])
			else:
				words.append(tokens[2])
			# if tokens[1] == 'ADJ':
				# words.append(tokens[2])
				# adjectives.append(tokens[2])
	outfile = OUTPUT_DIR + filename
	fh = open(outfile, "w")
	fh.write(' '.join(words))
	fh.close()
	filelist.writerow([outfile, len(words)])
