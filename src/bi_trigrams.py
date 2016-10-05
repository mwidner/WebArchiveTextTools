"""
Read output from a corpus of text files
Create bigrams, trigrams, and frequency distributions

See documentation here: http://www.nltk.org/howto/collocations.html

Mike Widner <mikewidner@stanford.edu>
"""

import os
import csv
import sys
import string
import argparse
import collections

from nltk.corpus import PlaintextCorpusReader
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
from nltk.collocations import TrigramAssocMeasures, TrigramCollocationFinder

string.punctuation += "…"


def get_options():
    parser = argparse.ArgumentParser(
        description='Generate bigrams and trigrams')
    parser.add_argument('-i', '--input', dest='input', required=True,
                        help='Input directory of text files')
    parser.add_argument('-o', '--output', dest='output', required=True,
                        help='Output directory for results')
    parser.add_argument('-n', '--ngrams', dest='total_ngrams', default=500,
                        type=int, help='Total ngrams')
    parser.add_argument('-f', '--min-freq', dest='min_freq', default=3,
                        type=int, help='Minimum frequency')
    parser.add_argument('-s', '--stopwords', dest='stopwords',
                        help='Stopwords file')
    parser.add_argument('-l', '--min-length', dest='min_length',
                        help='Minimum length of words to include',
                        default=4, type=int)
    parser.add_argument('-m', '--min-measure', dest='min_measure',
                        help='Minimum ngram score to include in results',
                        default=0, type=int)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-b', '--bigrams-only', dest='bigrams_only',
                       action='store_true',
                       help='Calculate only bigrams')
    group.add_argument('-t', '--trigrams-only', dest='trigrams_only',
                       action='store_true',
                       help='Calculate only trigrams')
    return parser.parse_args()


def analyze_text(text, filename, stopwords, min_length, freq,
                 total_ngrams, min_measure, bigrams_only, trigrams_only):
    print(len(text), filename)
    words = [w.lower() for w in text
             if w not in string.punctuation
             if w.lower() not in stopwords and len(w) >= min_length]

    bigrams = None
    b_prefix_keys = None
    trigrams = None
    t_prefix_keys = None

    # what follows could totally be generalized
    if not trigrams_only:
        # Bigrams
        print("Generating bigrams from", filename)
        b_finder = BigramCollocationFinder.from_words(words)
        b_finder.ngram_fd
        b_finder.apply_freq_filter(freq)
        # if stopwords:
        #   b_finder.apply_word_filter(lambda w: w in stopwords)
        bigrams = b_finder.nbest(BigramAssocMeasures.pmi, total_ngrams)
        b_scored = b_finder.score_ngrams(BigramAssocMeasures.pmi)
        b_prefix_keys = collections.defaultdict(list)
        for key, scores in b_scored:
            if scores > min_measure:
                b_prefix_keys[key[0]].append((key[1], scores))

    # Trigrams
    if not bigrams_only:
        print("Generating trigrams from", filename)
        t_finder = TrigramCollocationFinder.from_words(words)
        t_finder.apply_freq_filter(freq)
        # if stopwords:
        #   t_finder.apply_word_filter(lambda w: w in stopwords)
        trigrams = t_finder.nbest(TrigramAssocMeasures.pmi, total_ngrams)
        t_scored = t_finder.score_ngrams(TrigramAssocMeasures.pmi)
        t_prefix_keys = collections.defaultdict(list)
        for key, scores in t_scored:
            if scores > min_measure:
                t_prefix_keys[key[0]].append((key[1], key[2], scores))

    if bigrams_only:
        ret = {'bigrams': bigrams, 'b_prefix': b_prefix_keys,
               'b_fd': b_finder.ngram_fd}
    elif trigrams_only:
        ret = {'trigrams': trigrams, 't_prefix': t_prefix_keys,
               't_fd': t_finder.ngram_fd}
    else:
        ret = {'bigrams': bigrams, 'b_prefix': b_prefix_keys,
               'b_fd': b_finder.ngram_fd,
               'trigrams': trigrams, 't_prefix': t_prefix_keys,
               't_fd': t_finder.ngram_fd}
    return ret


def get_stopwords(filename):
    fh = open(filename, 'r')
    stopwords = fh.read()
    fh.close()
    return stopwords.split()


def write_results(results, prefix, bigrams_only, trigrams_only):
    filename = os.path.splitext(os.path.basename(prefix))[0]
    outdir = os.path.dirname(prefix)
    prefix = os.path.join(outdir, filename)
    # Bigrams
    if not trigrams_only:
        fh = open(prefix + '-bigrams.txt', 'w')
        for bigram in results['bigrams']:
            fh.write(' '.join(bigram) + "\n")
        fh.close()
        fh = csv.writer(open(prefix + '-bigram_prefix.csv', 'w',
                        encoding='utf-8'), dialect='excel')
        fh.writerow(['measure', 'freq', 'first', 'second'])
        for key in results['b_prefix']:
            for item in results['b_prefix'][key]:
                fh.writerow([item[1], results['b_fd'][(key, item[0])],
                            key, item[0]])

    # Trigrams
    if not bigrams_only:
        fh = open(prefix + '-trigrams.txt', 'w')
        for trigram in results['trigrams']:
            fh.write(' '.join(trigram) + "\n")
        fh.close()
        fh = csv.writer(open(prefix + '-trigram_prefix.csv', 'w',
                        encoding='utf-8'))
        fh.writerow(['measure', 'freq', 'first', 'second', 'third'])
        for key in results['t_prefix']:
            for item in results['t_prefix'][key]:
                fh.writerow([item[2], results['t_fd'][(key, item[0], item[1])],
                            key, item[0], item[1]])


def main():
    options = get_options()
    if not os.path.isdir(options.output):
        os.makedirs(options.output)

    wordlists = PlaintextCorpusReader(options.input, '.*\.txt$')

    stopwords = list()
    if options.stopwords:
        stopwords = get_stopwords(options.stopwords)

    for fileid in wordlists.fileids():
        results = analyze_text(wordlists.words(fileid), fileid,
                               stopwords, options.min_length,
                               options.min_freq, options.total_ngrams,
                               options.min_measure, options.bigrams_only,
                               options.trigrams_only)
        write_results(results, os.path.join(options.output, fileid),
                      options.bigrams_only, options.trigrams_only)


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        print("This script requires Python 3")
        exit(-1)
    main()
