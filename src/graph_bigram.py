'''
Generate bigram networks with interlinks
'''

import os
import sys
import csv
import igraph
import argparse


def get_settings():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='inputfile', required=True, help='CSV of bigram data')
    parser.add_argument('-o', dest='outputfile', required=True, help='Output filename')
    parser.add_argument('-w', dest='words', action='append', help='Word(s) to base network on')
    parser.add_argument('-d', dest='distance', type=int, default=1, help='Maximum distance from keyword(s) to include')
    parser.add_argument('-f', dest='frequency', type=float, default=0, help='Minimum frequency to include')
    parser.add_argument('-m', dest='measure', type=float, default=0, help='Minimum measure')
    return parser.parse_args()


def build_network(data):
    g = igraph.Graph().as_directed()
    nodes = list()
    edges = list()
    weights = list()
    freq = list()
    for row in data:
        nodes.append(row['first'])
        nodes.append(row['second'])
        edge = (row['first'], row['second'])
        edges.append(edge)
        weights.append(float(row['measure']))
        freq.append(float(row['freq']))

    nodes = list(set(nodes))
    g.add_vertices(nodes)
    g.vs['label'] = nodes
    g.add_edges(edges)
    g.es['weight'] = weights
    g.es['frequency'] = freq
    return g


def filter_network(g, words, frequency, measure, distance):
    # Remove edges that don't match thresholds
    edges = [e.index for e in g.es.select(frequency_lt=frequency)]
    g.delete_edges(edges)
    edges = [e.index for e in g.es.select(weight_lt=measure)]
    g.delete_edges(edges)

    # Delete the orphaned nodes
    nodes = [n.index for n in g.vs.select(_degree=0)]
    g.delete_vertices(nodes)

    # Find ego networks for selected words
    sources = g.vs.select(name_in=words)
    neighborhoods = g.neighborhood(vertices=sources, mode='all', order=distance)
    nids = [n for neighborhood in neighborhoods for n in neighborhood]  # flatten the lists
    nodes = g.vs.select(nids)
    return g.subgraph(nodes)


def main():
    settings = get_settings()
    with open(settings.inputfile) as f:
        reader = csv.DictReader(f)
        data = list(reader)

    g = build_network(data)

    ## Now filter the network
    g = filter_network(g=g, frequency=settings.frequency, words=settings.words, distance=settings.distance, measure=settings.measure)


    # Write results
    outdir =  os.path.dirname(settings.outputfile)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    g.write_gml(settings.outputfile)

if __name__ == '__main__':
    if sys.version_info[0] != 3:
        print("This script requires Python 3")
        exit(-1)
    main()
