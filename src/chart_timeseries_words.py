'''
Generate time series for certain words
'''

import os
import sys
import nltk
import pandas as pd
import argparse
import dateutil
import wordfreqs as wf
import gen_charts as gc


def get_settings():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='inputfile', required=True, help='Input CSV of metadata')
    parser.add_argument('-o', dest='outputdir', required=True, help='Output directory')
    parser.add_argument('-s', dest='show', action='store_true', help='Show images before saving')
    parser.add_argument('-n', dest='number', type=int, help='Top N items', default=50)
    parser.add_argument('-t', '--time', dest='time', type=int, help='Default intervals, in months', default=1)
    parser.add_argument('-l', '--language', dest='language', required=True,
                        help='Language in which the texts were written',
                        choices=wf.lang_codes.keys(), type = str.lower)
    parser.add_argument('-w', '--word', dest='word', action='append')
    return parser.parse_args()


def get_year(value):
    datetime = dateutil.parser.parse(value)
    return datetime.year


def get_month(value):
    datetime = dateutil.parser.parse(value)
    return datetime.month


def get_words(filename, language):
    text = wf.get_text_from_file(filename)
    sentences = wf.tokenize_text(text, language)
    return wf.wordlist(sentences)


def main():
    settings = get_settings()
    if not os.path.isdir(settings.outputdir):
        os.makedirs(settings.outputdir)

    df = pd.read_csv(settings.inputfile, quotechar='|')
    df['words'] = df['filename'].apply(get_words, args=(settings.language,))
    df['year'] = df['date'].apply(get_year)
    df['month'] = df['date'].apply(get_month)
    df.dropna(subset=['words'], inplace=True)
    words_df = df.groupby(by=['year', 'month'])['words']
    print(words_df)

    # for name, group in words_df:
    #     documents = group.tolist()
    #     tokens = list()
    #     for words in documents:
    #         tokens += words
    #     group['fd'] = nltk.FreqDist(tokens)
    #     print(group)


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        print("This script requires Python 3")
        exit(-1)
    main()
