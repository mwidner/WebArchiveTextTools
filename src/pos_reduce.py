#
# Strip some parts of speech from all texts
# and lemmatize for better topic models
#

import os
import sys
import nltk
import argparse

def parse_options():
  # tag_method
  parser = argparse.ArgumentParser(prog='PROG', description='Usage: %(prog) -i input -o output_path')
  parser.add_argument('-i', '--input',
                    dest = 'input_path',
                    required = True,
                    help = 'Path to corpus')
  parser.add_argument('-o', '--out',
                    dest = 'output_path',
                    required = True,
                    help = 'Path for output')

  options = parser.parse_args()
  if options.input_path is None or options.output_path is None:
      print(parser.print_help())
      exit(-1)
  return(options)

def load_corpus(path):
  return nltk.corpus.PlaintextCorpusReader(path, '.*')

def reduce_pos(sentences):
  '''
  Return words with desired POS
  Expects list of sentences
  '''
  # adjectives, nouns, and verbs only
  parts_to_keep = ['JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
  return [token for sent in sentences
      for token, pos in nltk.pos_tag(sent)
      if pos in parts_to_keep]

def lemmatize(words):
  wl = nltk.stem.WordNetLemmatizer()
  return [wl.lemmatize(word) for word in words]

def write_results(text, outfile):
  d = os.path.dirname(outfile)
  if not os.path.exists(d):
    os.makedirs(d)
  with open(outfile, "w") as out:
    out.write(text)

def main():
  options = parse_options()
  corpus = load_corpus(options.input_path)
  for fileid in corpus.fileids():
    words = lemmatize(reduce_pos(corpus.sents(fileid)))
    write_results(' '.join(words), options.output_path + '/' + fileid)

if __name__ == '__main__':
  if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(-1)
  main()
