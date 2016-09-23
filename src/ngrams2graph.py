'''
Turns ngrams into network graphs
Uses output from bi_trigrams.py script, nltk-based collocations

Mike Widner <mikewidner@stanford.edu>
'''

import sys
import csv
import argparse
import networkx as nx


def get_options():
    parser = argparse.ArgumentParser(
        description='Generate graphs from ngram csv')
    parser.add_argument('-i', '--input', dest='input', action='append',
                        required=True, help='Input file of ngram CSV measures')
    parser.add_argument('-o', '--output', dest='output', required=True,
                        help='Output directory for results')
    parser.add_argument('-n', '--label', dest='label', action='append',
                        help='Labels')
    return parser.parse_args()


def parse_ngram_csv(filename):
    '''
    Read in a CSV of ngrams with their measures as the first column
    Return a dict with the information
    '''
    results = dict()
    fh = open(filename, 'r')
    reader = csv.reader(fh)
    next(reader, None)  # skip header
    for row in reader:
        # TODO: Rewrite so it understands column names!
        results[row[0]] = ' '.join(row[2:])
    fh.close()
    return(results)


def write_graph_file(outfile, ngrams, labels):
    '''
    Generate the network graph and write it
    '''
    G = nx.DiGraph()
    for filename in ngrams.keys():
        # TODO: Generate nice labels automatically
        G.add_node(labels[filename], label=labels[filename])
        G.add_nodes_from([ngram for ngram in ngrams[filename].values()])
        for item in ngrams[filename].items():
            G.add_edge(labels[filename], item[1], weight=item[0])
        try:
            nx.write_gexf(G, outfile)
        except Exception as err:
            print("Could not write graphfile", outfile, err)


def main():
    options = get_options()
    ngrams = dict()
    labels = dict()

    if isinstance(options.input, list):
        for filename in options.input:
            if options.label:
                labels[filename] = options.label.pop(0)
            else:
                labels[filename] = filename
            ngrams[filename] = parse_ngram_csv(filename)
    else:
        labels[options.input] = options.input
        ngrams[options.input] = parse_ngram_csv(options.input)
    write_graph_file(options.output, ngrams, labels)


if __name__ == '__main__':
    if sys.version_info[0] != 3:
        print("This script requires Python 3")
        exit(-1)
    main()
