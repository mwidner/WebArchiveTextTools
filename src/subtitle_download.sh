#!/bin/sh
youtube="/Users/widner/Projects/DLCL/Alduy/French_Poli/venv/bin/youtube-dl"
subtitle_dir="/Users/widner/Projects/DLCL/Alduy/French_Poli/subtitles"
$youtube --skip-download --write-auto-sub --write-sub --sub-lang fr -o "${subtitle_dir}/%(title)s-%(id)s.$(ext)s" $1
