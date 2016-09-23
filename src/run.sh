#!/bin/sh
export TAGDIR="/farmshare/user_data/widner/treetagger"
pip3 install -r requirements.txt --user
time python3 ./wordfreqs.py -i ./corpus -s -p -l french -o results --extra-stopwords ./stopwords.txt --pos --pos-ignore PUN --pos-ignore SENT -v
