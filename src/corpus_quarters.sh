#!/bin/sh
# all.2014.01-03.txt
# all.2014.04-06.txt
# all.2014.07-09.txt
# all.2014.10-12.txt
# AJ.2014.01-03.txt
# AJ.2014.04-07.txt

WORKDIR="/Users/widner/Projects/DLCL/Alduy/French_Poli/book_corpus"
METADATA="$WORKDIR/metadata/all.csv"
SRC="/Users/widner/Projects/DLCL/Alduy/French_Poli/src"

for year in "2014" "2015" "2016"; do
  for start_month in "01" "04" "07" "10"; do
    end_month=$(($start_month + 2))
    next_month=$(($end_month + 1))
    if [ $end_month -ne "12" ]; then
      last_day=`/bin/date -v1d -v${next_month}m -v${year}y -v-1d +%d`
    else
      last_day=31
    fi

    outfile="$WORKDIR/metadata/all_${year}-${start_month}-${end_month}.csv"
    outdir="$WORKDIR/${year}_${start_month}_${end_month}"
    python $SRC/filter_dates.py -i $METADATA -o $outfile -s ${year}-${start_month}-01 -e ${year}-${end_month}-${last_day}
    python $SRC/join_corpus.py -m $outfile -i $WORKDIR/texts -o $outdir -c author
    cat $outdir/author/*.txt >> $outdir/all.${year}.${start_month}-${end_month}.txt
    for author in `ls $outdir/author/*.txt`; do
      author_name=`basename $author .txt`
      mv $author $outdir/author/$author_name.${year}.${start_month}-${end_month}.txt
    done
  done
done
