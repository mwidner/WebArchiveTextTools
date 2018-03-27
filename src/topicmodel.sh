#!/bin/sh
#
# This script runs MALLET on a corpus with different numbers of
# topics and also generates detailed diagnostic output for
# analysis of the topic quality
#
# It generates however many sub-directories it needs to store
# the different outputs (determined by $n_topics)
#
# Set the variables as needed for your project
#
# Mike Widner <mikewidner@stanford.edu>
#
#####


### VARIABLES ###
MALLET_HOME=/Applications/mallet
mallet=$MALLET_HOME/bin/mallet
networks="/Users/widner/Projects/DLCL/Alduy/French_Poli/venv/bin/python3 /Users/widner/Projects/DLCL/Alduy/French_Poli/src/mallet2graph.py"
n_topics=(20 40 80)
PROJECT=FrenchPoli
inputdir=/Users/widner/Documents/Work/Teaching/Tolstoy/Corpora_export/AK
outputdir=/Users/widner/Documents/Work/Teaching/Tolstoy/Corpora_export/AK/topics
stopwords=/Users/widner/Documents/Work/Teaching/Tolstoy/Corpora_export/stopwords.txt	# wherever they live

if [ -d outputdir ];
	then
		rm -rf $outputdir
fi

### IMPORT ###
mallet_import="$mallet import-dir --input $inputdir --output $outputdir/${PROJECT}.vectors --token-regex '[\p{L}\p{M}]+' --stoplist-file ${stopwords} --keep-sequence"
# if [ ! -z $extra_stopwords ]; then
# 	mallet_import="$mallet_import --extra-stopwords $extra_stopwords"
# fi

if [ ! -d outputdir ];
	then
		mkdir -p $outputdir
fi

eval "$mallet_import"

### TRAIN TOPICS ###
for topics in ${n_topics[@]}
  do
    topics_output="$outputdir/$topics"
    if [ ! -d $topics_output ];
      then
        mkdir -p $topics_output
    fi
	$mallet run cc.mallet.topics.tui.TopicTrainer --input $outputdir/${PROJECT}.vectors --num-topics $topics --optimize-interval 20 --diagnostics-file $topics_output/diagnostics.xml --output-topic-keys $topics_output/topic-keys.txt --output-doc-topics $topics_output/doc-topics.txt --xml-topic-phrase-report $topics_output/topic-phrase-report.xml --xml-topic-report $topics_output/topic-report.xml --topic-word-weights-file $topics_output/topic-word-weights.txt --word-topic-counts-file $topics_output/word-topic-counts.txt --output-state $topics_output/state.gz

  ## Generate network graphs from topic models
  # $networks -d ${outputdir}/${topics}/doc-topics.txt -t ${outputdir}/${topics}/topic-keys.txt -o ${outputdir}/${topics}/network.gexf
  done
