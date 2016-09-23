#!/bin/sh
AUTHORS=`ls -d */ | cut -f1 -d'/'`
for author in $AUTHORS; do
	# GENRES=`ls author/$author/genre/`
  YEARS=`ls $author/year/`
	# for genre in $GENRES; do
		# mv "author/$author/genre/$genre" "${author}_${genre}"
  for year in $YEARS; do
    mv "$author/year/$year" "${author}_${year}"
  #     # mv "author/$author/genre/$genre/year/$year" "${author}_${genre}_${year}"
  done
	# done
done

