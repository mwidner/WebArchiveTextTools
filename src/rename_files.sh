#!/bin/sh
QUARTERS=`ls -d */ | cut -f1 -d'/'`
for quarter in $QUARTERS; do
	AUTHORS=`ls $quarter/author`
	for author in $AUTHORS; do
    if [ ! -d "${quarter}/author/${author}" ]; then
     echo mv "${quarter}/author/${author}" "${author}_${quarter}"
    fi
	done
done

