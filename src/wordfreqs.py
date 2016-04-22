 # -*- coding: utf-8 -*-
'''
Compute word frequencies from corpus

Mike Widner <mikewidner@stanford.edu>
'''

import os
import re
import csv
import sys
import math
import nltk
import string
import argparse
import statistics
import collections
import treetaggerwrapper as ttw

# These are the languages TreeTagger supports
lang_codes = {
  'bulgarian' : 'bg',
  'german'    : 'de',
  'english'   : 'en',
  'spanish'   : 'es',
  'estonian'  : 'et',
  'finnish'   : 'fi',
  'french'    : 'fr',
  'galician'  : 'gl',
  'italian'   : 'it',
  'latin'     : 'la',
  'mongolian' : 'mn',
  'dutch'     : 'nl',
  'polish'    : 'pl',
  'russian'   : 'ru',
  'slovak'    : 'sk',
  'swahili'   : 'sw',
}

settings = None # for global access to cmd-line options

def get_settings():
  ''' Return command-line settings '''
  parser = argparse.ArgumentParser(description='Calculate word frequencies for a corpus')
  parser.add_argument('-i', dest='input_dir', required=True, help='Input directory of files to analyze')
  parser.add_argument('-o', dest='output_dir', default='.',
                   help='Output directory for results')
  parser.add_argument('--pos', dest='pos', action='store_true', help='Tag parts-of-speech and calculate frequencies of their use')
  parser.add_argument('--lemmas', dest='lemmas', action='store_true', help='Count lemmas instead of words for part-of-speech frequencies')
  parser.add_argument('--pos-ignore', dest='pos_ignore', action='append', help='A list of POS tags to ignore')
  parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', required=False, help='Provide verbose output')
  parser.add_argument('-s', '--stopwords', dest='remove_stopwords', action='store_true', required=False, help='Remove stopwords')
  parser.add_argument('--extra-stopwords', dest='extra_stopwords', required=False, help='Path to a text file of more stopwords, separated by newlines')
  parser.add_argument('-l', '--lang', dest='language', default='french', required=False, help='Choose the language of the corpus (default: %(default)s', choices=lang_codes.keys(), type = str.lower)
  parser.add_argument('-p', '--punc', dest='remove_punctuation', action='store_true', required=False, help='Remove punctuation')
  return parser.parse_args()

def fix_sentence_end_without_space(text):
  '''
  Some texts in corpus have no spaces after ending punctuation
  Sentence tokenizer can't handle those, so add some spaces
  '''
  return re.sub(r"(\w+)([.,…»;\"':]+)(\w+)", r"\1\2 \3", text)

def get_text_from_file(filename):
  '''
  Read a file and return entire text as a string
  Note: we don't use PlaintextCorpusReader because it tokenizes,
  but we're tokenizing differently for our French corpus
  '''
  text = None
  try:
    f = open(filename, 'r', encoding='utf-8')
    text = f.read()
    f.close()
  except UnicodeDecodeError as err:
    print("Could not read {}: {}".format(filename, err))
  return fix_sentence_end_without_space(text)

def read_corpus(dir):
  '''
  Read in the entire corpus
  Return dict of texts keyed by filename paths
  '''
  corpus = dict()
  for root, subdirs, files in os.walk(dir):
    for filename in files:
      path = os.path.join(root, filename)
      text = get_text_from_file(path)
      corpus[path] = text
  return corpus

def replace_smart_quotes(text):
  '''
  Smart quotes aren't in stopwords list, so replace them
  '''
  return text.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u2019", '"').replace(u"\u201d", '"')

def strip_punctuation(words):
  '''
  Remove all punctuation from a list of words
  '''
  string.punctuation += "«»`'…–"  # Add some other punctuation marks
  return [replace_smart_quotes(word).strip(string.punctuation) for word in words if word not in string.punctuation]

def get_stopwords(language):
  '''
  Retrieve a list of stopwords, if one exists in the corpus
  '''
  stopwords = list()
  try:
    stopwords = nltk.corpus.stopwords.words(language)
  except OSError:
    print('Cannot find stopwords list for {}'.format(language))
  try:
    if (settings is not None) and settings.extra_stopwords:
      extra_stopwords = set(get_text_from_file(settings.extra_stopwords).split('\n'))
      stopwords = list(set(stopwords) | extra_stopwords)
  except NameError:
    pass # Can safely ignore this
  return stopwords

def strip_stopwords(words, stopwords):
  '''
  Remove all stop words from a word list
  Return the stripped text
  '''
  return [word for word in words if word.lower() not in stopwords]

def wordlist(sentences):
  '''
  Take in a list of sentences, which are lists of words
  Convert into just a list of words
  '''
  return [word.lower() for sentence in sentences for word in sentence]

def corpus_sents_to_words(corpus):
  '''
  Take in the entire sentence-tokenized corpus
  And convert into flat word lists
  '''
  corpus_words = dict()
  for filename in corpus:
    corpus_words[filename] = wordlist(corpus[filename])
  return corpus_words

def basic_stats(sentences):
  '''
  Return some basic statistics about a text
  Number of words, sentences, average sentence length
  Expects tokenized list of sentences of list of words
  '''
  stats = dict()
  stats['sentences'] = len(sentences)
  stats['words'] = len(wordlist(sentences))
  word_lengths = [len(word) for sentence in sentences for word in sentence]
  sentence_lengths = [len(sentence) for sentence in sentences]
  stats['mean_sentence_length'] = statistics.mean(sentence_lengths)
  stats['median_sentence_length'] = statistics.median(sentence_lengths)
  stats['mean_word_length'] = statistics.mean(word_lengths)
  stats['median_word_length'] = statistics.median(word_lengths)
  return stats

def tokenize_text(text, language, stopwords, remove_punctuation = False):
  '''
  Tokenize the given text string
  Return as a list of sentences that are lists of words
  '''
  try:
    sent_tokenizer = nltk.data.load('tokenizers/punkt/' + language + '.pickle')
    sentence_tokens = sent_tokenizer.tokenize(text)
  except LookupError:
    # Use default sentence tokenizer
    sentence_tokens = nltk.tokenize.sent_tokenize(text)
  sentences = list()
  for sentence in sentence_tokens:
    # Note: WordPunctTokenizer works better for French
    # General-purpose word tokenizer is nltk.tokenize.word_tokenize()
    word_tokenizer = nltk.tokenize.WordPunctTokenizer()
    words = word_tokenizer.tokenize(sentence)
    if len(stopwords):
      words = strip_stopwords(words, stopwords)
    if remove_punctuation:
      words = strip_punctuation(words)
    sentences.append(words)
  return sentences

def raw_freq(words):
  ''' Calculate raw word frequencies '''
  if not type(words) is list:
    raise TypeError('Expected a list of words for frequencies')
  return nltk.FreqDist(words)

def rel_freq(freqdist, words):
  '''
  Calculate relative term frequency for every word in a doc
  Expects raw frequencies and list of words
  Return a dict of results
  '''
  if not isinstance(freqdist, nltk.FreqDist):
    raise TypeError('Expected nltk.FreqDist for frequencies')
  if not isinstance(words, list):
    raise TypeError('Expected list() of words')
  doc_length = len(words)
  return {word: freq / doc_length for word, freq in freqdist.items()}

def n_containing(word, corpus):
  '''
  Counts number of documents in corpus that contain given word
  '''
  return sum(1 for filename in corpus if word in corpus[filename])

def idf(word, corpus):
  '''
  Give inverse document frequency score for given word
  '''
  return math.log(len(corpus) / (n_containing(word, corpus)))

def tfidf(word, freq, corpus):
  '''
  Return TF-IDF score for given word
  Expects the relative frequency
  '''
  return freq * idf(word, corpus)

def corpus_tfidf(wordfreqs, corpus):
  '''
  Calculate TF-IDF scores for entire corpus
  Expects dict of nltk.FreqDists for each file
  And a dict of word-tokenized documents
  '''
  tfidf_values = collections.defaultdict(dict)
  for filename in wordfreqs:
    for word, freq in wordfreqs[filename].items():
      tfidf_values[filename][word] = tfidf(word, freq, corpus)
  return tfidf_values

def tag_pos(text, language):
  ''' Tag parts-of-speech in text; return tagged text '''
  # ttw will throw an error if the code isn't supported
  tagger = ttw.TreeTagger(TAGLANG=lang_codes[language])
  tags = tagger.tag_text(text)
  return ttw.make_tags(tags)

def pos_raw_freq(tagged_tokens, pos_ignore_list, count_lemmas = False):
  '''
  Calculate part-of-speech raw frequencies
  '''
  counters = dict()
  for token in tagged_tokens:
    if not isinstance(token, ttw.Tag):
      continue
    pos = token.pos
    if ':' in token.pos:
      pos = token.pos.split(':')[0]
    if pos in pos_ignore_list:
      continue
    if pos not in counters:
      counters[pos] = collections.Counter()
    if count_lemmas:
      counters[pos][token.lemma] += 1
    else:
      counters[pos][token.word.lower()] += 1
  return counters

def pos_percents(text, pos_counters):
  '''
  Calculate the overall percentage of a document
  that each POS comprises
  '''
  total_word_count = len(text)
  pos_percent = dict()
  for pos in pos_counters:
    pos_word_count = 0
    for word, count in pos_counters[pos].items():
      pos_word_count += count
    pos_percent[pos] = round(100 * (pos_word_count / total_word_count), 2)
  return pos_percent

def output_filename(dest, filename):
  '''
  Return a new filename to write to
  '''
  table = str.maketrans('/.', '__')
  filename = os.path.basename(filename).translate(table).lstrip('_')
  return os.path.join(dest, filename) + '.csv'

def write_stats(data, outfile):
  '''
  Write general document-level stats
  '''
  if not os.path.isdir(os.path.dirname(outfile)):
    os.makedirs(outfile)
  with open(outfile, 'w') as f:
    csvfile = csv.writer(f, quotechar='|')
    sorted_keys = sorted(list(data.keys()), reverse=True)
    csvfile.writerow(sorted_keys)
    csvfile.writerow([data[key] for key in sorted_keys])

def gather_word_results(data):
  '''
  Convert multiple dictionaries of types of stats
  Into per-word entries
  '''
  word_data = collections.defaultdict(dict)
  for stat_type in data:
    for word in data[stat_type]:
      word_data[word.lower()][stat_type] = data[stat_type][word]
  return word_data

def write_results(word_data, columns, stopwords, outfile):
  '''
  Write out all results
  Expects the data to be keyed by items in the columns list
  '''
  if not isinstance(columns, list):
    raise TypeError('Expected a list of columns!')
  if not isinstance(word_data, dict):
    raise TypeError('Expected data as a dict!')
  with open(outfile, 'w') as f:
    csvfile = csv.writer(f, quotechar='|')
    csvfile.writerow(['word'] + columns)
    for word in word_data:
      if word in stopwords:
        # stopwords might be in POS results
        continue
      row = list()
      row.append(word)
      for column in columns:
        if column in word_data[word]:
          value = word_data[word][column]
          if type(value) is float:
            value = format(value, '.8f')
          row.append(value)
        else:
          row.append('')
      csvfile.writerow(row)

def main():
  '''
  Run the entire process based on command-line parameters
  Calculates all frequencies, then writes results
  '''
  global settings
  settings = get_settings()
  corpus_raw = dict() # as strings of text
  corpus_tagged = dict() # as dict of Tag objects
  corpus_tokenized = dict() # as lists of words in list of sentences
  wordfreqs = collections.defaultdict(dict) # all frequencies
  outfiles = dict() # output filenames
  stopwords = list()

  corpus_raw = read_corpus(settings.input_dir)

  if settings.remove_stopwords:
    stopwords = get_stopwords(settings.language)

  for filename, text in corpus_raw.items():
    # set once, then store
    outfiles[filename] = output_filename(settings.output_dir, filename)
    # Create tokenized corpus
    if settings.verbose:
      print('Tokenizing {}'.format(filename))
    corpus_tokenized[filename] = tokenize_text(text, settings.language, stopwords, settings.remove_punctuation)

    # Create POS-tagged corpus
    if settings.pos:
      if settings.verbose:
        print('Part-of-speeching tagging {}'.format(filename))
      corpus_tagged[filename] = tag_pos(text, settings.language)
      # Calculate POS frequencies and then write results
      if settings.verbose:
        print('Part-of-speech frequency calculation for {}'.format(filename))
      wordfreqs[filename]['pos_raw_freq'] = pos_raw_freq(corpus_tagged[filename], settings.pos_ignore, settings.lemmas)

  # Raw frequencies and overall stats
  # Requires sentence-tokenized corpus for sentence-level statistics
  for filename, text in corpus_tokenized.items():
    stats = basic_stats(text)
    if settings.pos:
      pos_percent = pos_percents(corpus_tagged[filename], wordfreqs[filename]['pos_raw_freq'])
      for pos in pos_percent:
        stats[pos] = pos_percent[pos]
    write_stats(stats, output_filename(settings.output_dir, filename + '_stats'))

  # Done with sentence-level work; convert to flat word lists
  corpus_tokenized = corpus_sents_to_words(corpus_tokenized)
  for filename, text in corpus_tokenized.items():
    if settings.verbose:
      print('Frequency calculations for {}'.format(filename))
    wordfreqs[filename]['raw_freq'] = raw_freq(text)
    wordfreqs[filename]['rel_freq'] = rel_freq(wordfreqs[filename]['raw_freq'], text)

  # TF-IDF
  if (len(corpus_tokenized) < 2):
    print('Cannot calculate TF-IDF scores because we need more than one file in our corpus!')
  else:
    if settings.verbose:
      print('Calculating TF-IDF for corpus')
    freqs = {filename: wordfreqs[filename]['rel_freq'] for filename in wordfreqs.keys()}
    for filename, data in corpus_tfidf(freqs, corpus_tokenized).items():
      wordfreqs[filename]['tfidf'] = data

  # Write word-level frequency results
  for filename, results in wordfreqs.items():
    word_data = gather_word_results(results)
    if settings.pos:
      for word in word_data:
        # Indicate what part(s)-of-speech this word appears as
        word_data[word]['pos'] = list()
        for pos, freq in wordfreqs[filename]['pos_raw_freq'].items():
          if word in freq.keys():
            word_data[word]['pos'].append(pos)
        word_data[word]['pos'] = ','.join(word_data[word]['pos'])

      write_results(word_data, ['pos', 'raw_freq', 'rel_freq', 'tfidf'], stopwords, outfiles[filename])
    else:
      write_results(word_data, ['raw_freq', 'rel_freq', 'tfidf'], stopwords, outfiles[filename])

if __name__ == '__main__':
  if sys.version_info < (3,0):
    print("This script requires Python 3")
    exit(-1)
  main()
