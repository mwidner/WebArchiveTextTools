'''
Takes topic model output and converts it into a Gexf file, which Gephi can read
Assumes that your topic model input was a corpus where each document was split into chunks
and that each chunk lives in a subdirectory for the parent document
Expects the standard Mallet output of doc-topics.txt and topic-keys.txt

Mike Widner <mikewidner@stanford.edu>
February 2014
@author: widner
'''

import os
import csv
import sys
import numpy
import networkx as nx
from optparse import OptionParser

def parse_options():
    parser = OptionParser(usage='Usage: %prog -d doc-topics.txt -t topic-keys.txt -o output')
    parser.add_option('-d', '--doc-topics',
                      dest = 'doc_topics',
                      metavar = 'FILE',
                      help = 'The doc-topics.txt MALLET output')
    parser.add_option('-o', '--out',
                      dest = 'out',
                      metavar = 'FILE',
                      help = 'Output file')
    parser.add_option('-t', '--topic-keys',
                      dest = 'topics',
                      metavar = 'FILE',
                      help = 'The topic-keys.txt MALLET output')
    parser.add_option('-w', '--weight-method',
                      dest = 'weight_method',
                      default = 'median',
                      help = "The method by which to calculate document-topic edge weights: "
                              "median, mean, or max [default: %default]")

    options, args = parser.parse_args()
    if options.doc_topics is None or options.topics is None or options.out is None:
        print(parser.print_help())
        exit(-1)
    return(options)

def split_doc_chunk(doc):
  '''
  Return the document name and the chunk name
  '''
  doc = doc.replace('file:', '', 1) # strip any leading "file:" string
  doc, chunk = os.path.split(doc)
  # tweaks for LePen - take last 3 segments of path for name
  doc = doc.rsplit('/', 3)       # Note: assumes *nix-style path delimiters
  label = "-".join(doc[1:])
  filename = doc[-1]
  return(filename, chunk, label)

def build_edge_weight_lists(weights):
  '''
  Build a list of all edge weights by document and topic
  Return aggregate weights and document labels
  '''
  all_weights = dict()
  labels = dict()
  for weight in weights:
    doc_name, chunk_name, label = split_doc_chunk(weight[1])
    labels[doc_name] = label
    weight = weight[2:] # first two items are index and file path
    while len(weight) >= 2:
      tid = weight.pop(0)
      current_weight = float(weight.pop(0))
      if doc_name not in all_weights.keys():
        all_weights[doc_name] = dict()
      if tid not in all_weights[doc_name].keys():
        all_weights[doc_name][tid] = list()
      all_weights[doc_name][tid].append(current_weight)
  return(all_weights, labels)

def calc_edge_weights(all_weights, weight_method):
  '''
  Determine the edge weights for each document-topic link
  Method varies based on option chosen
  '''
  doc_topic_weights = dict()
  for doc_name in all_weights.keys():
    if doc_name not in doc_topic_weights.keys():
      doc_topic_weights[doc_name] = dict()
    for tid in all_weights[doc_name].keys():
      if weight_method == 'max':
        doc_topic_weights[doc_name][tid] = max(all_weights[doc_name][tid])
      elif weight_method == 'median':
        doc_topic_weights[doc_name][tid] = numpy.median(all_weights[doc_name][tid])
      elif weight_method == 'mean':
        doc_topic_weights[doc_name][tid] = numpy.mean(all_weights[doc_name][tid])
 
  return(doc_topic_weights)

def write_graph_file(topics, doc_topic_weights, labels, outfile):
  ''' 
  Generate the network graph and write it 
  '''
  G = nx.Graph()
  for doc in doc_topic_weights.keys():
    G.add_node(doc, label=labels[doc])
  # G.add_nodes_from([doc for doc in doc_topic_weights.keys()])
  for topic in topics:
    G.add_node(topic[0], label=topic[2], viz={'size': topic[1]}) # size by topic weight
    for doc in doc_topic_weights.keys():
      for tid in doc_topic_weights[doc].keys():
        if tid == topic[0]:
          G.add_edge(tid, doc, weight=doc_topic_weights[doc][tid])

  try:
    nx.write_gexf(G, outfile)
  except Exception as err:
    print("Could not write graphfile", outfile, err)

def main():
  options = parse_options()
  weights = csv.reader(open(options.doc_topics, 'r'), delimiter='\t')
  next(weights, None) # skip first line, which is a poorly-formatted header
  all_weights, labels = build_edge_weight_lists(weights)
  doc_topic_weights = calc_edge_weights(all_weights, options.weight_method)  
  topics = csv.reader(open(options.topics, 'r'), delimiter='\t')
  write_graph_file(topics, doc_topic_weights, labels, options.out)

if __name__ == '__main__':
  # nothing specific to Python 3 in here
  # if sys.version_info[0] != 3:
  #   print("This script requires Python 3")
  #   exit(-1)
  main()