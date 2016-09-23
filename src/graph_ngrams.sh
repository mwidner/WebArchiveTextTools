#!/bin/sh

FILES=`ls book_corpus/results/ngrams/author/bigrams-f10-n100-m5/*-bigram_prefix.csv`
CMD="python src/ngrams2graph.py"
for FILE in $FILES
	do
		CMD="$CMD -i $FILE "
	done
CMD="$CMD -o book_corpus/results/ngrams/author/bigrams-f10-n100-m5/network.gexf"
eval $CMD
