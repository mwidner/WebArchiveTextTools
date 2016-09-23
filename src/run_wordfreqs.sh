#!/bin/sh
export TAGDIR="/farmshare/user_data/widner/treetagger"
pip3 install -r wordfreq_requirements.txt --user
python3 -u ./wordfreqs.py -i ./corpus/joined -s -p -l french -o results --extra-stopwords ./stopwords.txt --pos --pos-ignore PUN --pos-ignore SENT -v
