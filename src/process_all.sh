#!/bin/sh

BASE_DIR="/Users/widner/Projects/DLCL/Alduy/French_Poli"
WARC_DIR="${BASE_DIR}/warcs/June16/extracted"
CODE_DIR="${BASE_DIR}/src"
OUTPUT_DIR="${BASE_DIR}/test"
SETTINGS_DIR="${BASE_DIR}/settings"

python ${CODE_DIR}/extract_text.py -i ${WARC_DIR} -s ${SETTINGS_DIR}/sites_info.csv -o ${OUTPUT_DIR}/corpus -w 50

python ${CODE_DIR}/convert_dates.py -i ${OUTPUT_DIR}/metadata.csv -o ${OUTPUT_DIR}/metadata_dates.csv

python ${CODE_DIR}/post_process.py -m ${OUTPUT_DIR}/metadata_dates.csv -c ${SETTINGS_DIR}/post_process_rules.csv -r -o ${OUTPUT_DIR}/metadata_processed.csv -d '%Y-%m-%d'

python ${CODE_DIR}/join_corpus.py -i ${OUTPUT_DIR}/text -o {OUTPUT_DIR}/joined -m ${OUTPUT_DIR}/metadata.csv.clean -c author -c site


