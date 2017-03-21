#!/bin/sh

FILES=`ls $1/*-trigram_prefix.csv`
CMD="python src/ngrams2graph.py"
for FILE in $FILES
	do
		CMD="$CMD -i $FILE "
	done
CMD="$CMD -o book_corpus/results/ngrams/year/trigrams-network.gexf"
eval $CMD

FILES=`ls $1/*-bigram_prefix.csv`
CMD="python src/ngrams2graph.py"
for FILE in $FILES
  do
    CMD="$CMD -i $FILE "
  done
CMD="$CMD -o book_corpus/results/ngrams/year/bigrams-network.gexf"
eval $CMD
