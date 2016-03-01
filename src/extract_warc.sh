#!/bin/sh
# Extract a WARC
# Requires Python with the Warcat package (https://pypi.python.org/pypi/Warcat/)
# to be in path
#
# Mike Widner <mikewidner@stanford.edu>
#
####

if [ -z $1 ] || [ -z $2 ]; then
  echo "Usage: $0 INPUT_FILE OUTPUT_DIR"
  exit 1
fi
python -m warcat extract $1 --output-dir $2 --progress
