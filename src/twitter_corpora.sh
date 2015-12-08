#!/bin/sh

CMD='python src/tweets_to_text.py'

$CMD -i corpus/tweets/mlp/mlp_twitter_data.csv -o corpus/tweets/MLP/since_october_cleaned.txt -s 2015-10-01

$CMD -i corpus/tweets/aj/aj_twitter_data.csv -o corpus/tweets/AJ/aj_aveccalmels_clean.txt -s 2015-11-28 --hashtag AvecCalmels -c

$CMD -i twitter_data.csv -o corpus/tweets/NS/ns_rouen_clean.txt -s 2015-11-30 -e 2015-11-30 --hashtag NSRouen -c

$CMD -i corpus/tweets/mlp/mlp_twitter_data.csv -o corpus/tweets/mlp/mlp_npdcp_clean.txt -s 2015-11-30 -e 2015-11-30 --hashtag NPDCP -c

$CMD -i corpus/tweets/mlp/mlp_twitter_data.csv -o corpus/tweets/mlp/mlp_ajaccio_clean.txt -c -s 2015-11-28 -e 2015-11-28 --hashtag Ajaccio

$CMD -i twitter_data.csv -o corpus/tweets/NS/ns_avignon_clean.txt -s 2015-11-26 -e 2015-11-26 --hashtag Avignon -c

$CMD -i corpus/tweets/mlp/mlp_twitter_data.csv -o corpus/tweets/mlp/mlp_acal_clean.txt -s 2015-11-25 -e 2015-11-25 --hashtag ACAL -c
