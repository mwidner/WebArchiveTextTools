'''
File counts per genre, author, year
'''

import os
import re
import csv
import sys
import pandas as pd
import argparse
import join_corpus as jc
import wordfreqs as wf


def get_settings():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='inputfile', required=True)
    parser.add_argument('-o', dest='outputfile', required=True)
    parser.add_argument('-l', '--language', dest='language', required=True,
                        help='Language in which the texts were written',
                        choices=wf.lang_codes.keys(), type = str.lower)
    parser.add_argument('-c', dest='columns', required=True, action='append')
    return parser.parse_args()


def count_words(filename, language):
    text = wf.get_text_from_file(filename)
    sentences = wf.tokenize_text(text, language)
    return len(wf.wordlist(sentences))


def write_rows(df, columns, csvfile, values=None):
    for i, col in enumerate(columns):
        for value in jc.get_uniques(df, col):
            sub_df = df[df[col] == value]
            row = {col: value, 'words': sub_df['words'].sum(), 'files': len(sub_df.index)}
            if values is not None:
                if 'words' in values:
                    del values['words']
                if 'files' in values:
                    del values['files']
                if col in values:
                    del values[col]
                row.update(values)
            csvfile.writerow(row)
            if i < len(columns) - 1:
                write_rows(sub_df, columns[i+1:], csvfile, row)

def main():
    settings = get_settings()
    df = pd.read_csv(settings.inputfile, quotechar='|')
    df['year'] = df['date'].apply(jc.get_year)
    df['file_exists'] = df['filename'].apply(os.path.isfile)
    df = df.drop(df[df['file_exists'] == False].index)
    df['words'] = df['filename'].apply(count_words, args=(settings.language,))

    if not os.path.exists(os.path.dirname(settings.outputfile)):
        os.makedirs(os.path.dirname(settings.outputfile))
    with open(settings.outputfile, 'w') as f:
        csvfile = csv.DictWriter(f, fieldnames=settings.columns + ['words', 'files'])
        csvfile.writeheader()
        write_rows(df, settings.columns, csvfile)


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        print("This script requires Python 3")
        exit(-1)
    main()
