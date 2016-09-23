'''
Create intersections of items in text files
'''

import os
import sys
import argparse
import itertools


def get_settings():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', action='append',
                        required=True, help='Input directory of text files')
    parser.add_argument('-o', '--output', dest='output', required=True,
                        help='Output directory for results')
    return parser.parse_args()


def get_texts(filenames):
    texts = dict()
    for filename in filenames:
        f = open(filename, 'r')
        texts[filename] = f.read().strip().split('\n')
        f.close()
    return texts


def get_filename(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def make_filename(pair):
    filename = get_filename(pair[0])
    filename += '-'
    filename += get_filename(pair[1])
    filename += '.txt'
    return filename


def main():
    settings = get_settings()
    if not os.path.isdir(settings.output):
        os.makedirs(settings.output)
    texts = get_texts(settings.input)
    for pair in itertools.permutations(list(texts.keys()), 2):
        intersection = set(texts[pair[0]]) & set(texts[pair[1]])
        filename = make_filename(pair)
        f = open(os.path.join(settings.output, filename), 'w')
        for row in intersection:
            f.write(row)
            f.write("\n")
        f.close()


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        print("This script requires Python 3")
        exit(-1)
    main()
