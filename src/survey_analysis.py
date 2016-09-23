import os
import csv
import nltk
import statistics
import argparse

settings = None

def get_settings():
  parser = argparse.ArgumentParser(description='Split CSV into text by column')
  parser.add_argument('-i', dest='inputfile', required=True, help='The CSV file to read')
  parser.add_argument('-o', dest='outputdir', required=True, help='Output directory')
  parser.add_argument('-s', dest='skip', action='append', help='Columns to skip, in lowercase')
  return parser.parse_args()

def calc_stats(column_data):
  ''' Calculate average words, most words in a column '''
  word_counts = list()
  word_tokenizer = nltk.tokenize.WordPunctTokenizer()
  for row in column_data:
    word_counts.append(len(word_tokenizer.tokenize(row)))
  return {'avg': statistics.mean(word_counts), 'max': max(word_counts)}

def column_lists(inputfile):
  ''' Convert CSV into lists by column '''
  columns = dict()
  with open(settings.inputfile) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      for key, value in row.items():
        if key not in columns:
          columns[key] = list()
        columns[key].append(value)
  return columns

def write_text(data, outputdir, filename):
  outfile = os.path.join(outputdir, filename)
  if not os.path.isdir(outputdir):
    os.makedirs(outputdir)
  with open(outfile, 'w') as f:
    f.write('\n'.join(data))

def write_stats(data, outputdir):
  outfile = os.path.join(outputdir, 'statistics.csv')
  with open(outfile, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['file', 'avg', 'max'])
    for column in data:
      writer.writerow([column, data[column]['avg'], data[column]['max']])

def main():
  global settings
  settings = get_settings()
  data = column_lists(settings.inputfile)
  stats = dict()
  for column in data.keys():
    if column.lower() not in settings.skip:
      stats[column] = calc_stats(data[column])
      write_text(data[column], settings.outputdir, column.lower())
  write_stats(stats, settings.outputdir)




if __name__ == "__main__":
  main()
