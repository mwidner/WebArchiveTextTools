'''
Generate bar charts of words and their values
'''

import os
import sys
import pandas as pd
import argparse
import gen_charts as gc


def get_settings():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='inputfile', required=True, help='Input CSV of words and values')
    parser.add_argument('-c', dest='column', required=True, help='Column name for the values')
    parser.add_argument('-o', dest='outputdir', required=True, help='Output directory')
    parser.add_argument('-s', dest='show', action='store_true', help='Show images before saving')
    parser.add_argument('-n', dest='number', type=int, help='Top N items', default=50)
    parser.add_argument('-t', dest='title', help='Chart title')
    parser.add_argument('-x', dest='xlabel', help='Label for x axis')
    parser.add_argument('-y', dest='ylabel', help='Label for y axis')
    return parser.parse_args()


def main():
    settings = get_settings()
    if not os.path.isdir(settings.outputdir):
        os.makedirs(settings.outputdir)
    df = pd.read_csv(settings.inputfile, error_bad_lines=False)

    # Raw frequency bar charts
    df.sort_values(settings.column, inplace=True, ascending=False)
    df.dropna(subset=[settings.column, 'word'], inplace=True)
    df['word'] = df['word'].apply(str.strip)
    basename = os.path.splitext(os.path.basename(settings.inputfile))[0]
    filename = os.path.join(settings.outputdir, "{}_{}_{}".format(basename, settings.number, settings.column + '.png'))
    if settings.number:
        data = df.head(settings.number)
    else:
        data = df
    gc.barplot(df=data, x='word', y=settings.column, filename=filename, xlabel=settings.xlabel, ylabel=settings.ylabel, title=settings.title, show=settings.show)


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        print("This script requires Python 3")
        exit(-1)
    main()
