import os
import re
import csv
import metadata


csvfile = "Macron/macron-metadata.csv"
csvdata = list()
with open(csvfile) as f:
	reader = csv.DictReader((row for row in f if not row.startswith('#')), skipinitialspace=True, delimiter=',')
	csvdata = [row for row in reader]

for row in csvdata:
	info_search = re.search('(\d{4} \d{2} \d{2}) (\w+)', row['filename'])
	if info_search:
		row['date'] = info_search.group(1)
		row['genre'] = info_search.group(2)
		row['author'] = 'EM'
		row['filename'] = 'book_corpus/texts/' + row['filename'] + '.txt'

metadata.write_csv('Macron/metadata-processed.csv', csvdata)
