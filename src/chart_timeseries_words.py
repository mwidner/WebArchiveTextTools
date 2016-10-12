'''
Generate time series for certain words
'''

import os
import sys
import nltk
import pandas as pd
import argparse
import dateutil
import datetime
import wordfreqs as wf
import matplotlib.pyplot as plt


def get_settings():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='inputfile', required=True, help='Input CSV of metadata')
    parser.add_argument('-o', dest='outputdir', required=True, help='Output directory')
    parser.add_argument('-s', dest='show', action='store_true', help='Show images before saving')
    parser.add_argument('-n', dest='number', type=int, help='Top N items', default=50)
    parser.add_argument('-t', '--time', dest='time', type=int, help='Default intervals, in months', default=1)
    parser.add_argument('-a', '--author', dest='author', help='Limit results to a specific author')
    parser.add_argument('-l', '--language', dest='language', required=True,
                        help='Language in which the texts were written',
                        choices=wf.lang_codes.keys(), type = str.lower)
    parser.add_argument('-w', '--word', dest='words', action='append')
    parser.add_argument('--exact', dest='exact', action='store_true', default=False, help='Require an exact match')
    return parser.parse_args()


def get_words(filename, language):
    text = wf.get_text_from_file(filename)
    sentences = wf.tokenize_text(text, language)
    return wf.wordlist(sentences)


def get_frequency(fd, word, exact):
    freq = 0
    if exact and word in fd:
        freq = fd.freq(word)
    else:
        for token in fd:
            if token.startswith(word):
                freq += fd[token]
    return freq


def relative_frequency(row, words):
    for word in words:
        if len(row['words']):
            row[word] = row[word] / len(row['words'])
        else:
            row[word] = 0
    return row

def main():
    settings = get_settings()
    if not os.path.isdir(settings.outputdir):
        os.makedirs(settings.outputdir)

    df = pd.read_csv(settings.inputfile, quotechar='|')

    if settings.author:
        df = df[df.author == settings.author]

    df['date'] = df['date'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
    df.set_index(['date'], inplace=True)
    df.sort_index(inplace=True)
    df['words'] = df['filename'].apply(get_words, args=(settings.language,))
    df['fd'] = df['words'].apply(nltk.FreqDist)

    for word in settings.words:
        df[word] = df['fd'].apply(get_frequency, args=(word, settings.exact))
    df = df.apply(relative_frequency, axis=1, args=(settings.words,))

    tsres = df[settings.words].resample('M').median().interpolate('time')
    lines = ['-.s', '--o', '-v', ':^']
    tsres.plot(style=lines, color='k')
    plt.savefig(os.path.join(settings.outputdir, '_'.join(settings.words)), pad_inches=.1, dpi=600)
    # plt.show()


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        print("This script requires Python 3")
        exit(-1)
    main()
