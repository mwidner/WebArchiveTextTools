#!/bin/sh
CMD="python /Users/widner/Projects/DLCL/Alduy/French_Poli/src/wordfilecounts.py"
OUTPUT=`dirname $1`
OUTPUT="-o ${OUTPUT}/wordcounts.csv"
for file in $@; do
  INPUT="$INPUT -i $file "
done
eval "$CMD $INPUT $OUTPUT -l french -c author -c genre"
