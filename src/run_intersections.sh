#!/bin/sh
CMD="python /Users/widner/Projects/DLCL/Alduy/French_Poli/src/intersections.py"
OUTPUT=`dirname $1`
OUTPUT="-o ${OUTPUT}/shared"
for file in $@; do
  INPUT="$INPUT -i $file "
done
eval "$CMD $INPUT $OUTPUT"
