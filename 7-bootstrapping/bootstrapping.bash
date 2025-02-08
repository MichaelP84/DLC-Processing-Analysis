#!/bin/bash

## Track Time
start=`date +%s`

Rscript --no-save software/TACC_BootAnalyzeGroupsInCondition.R --cond=3Rats --iter=2000 && end=`date +%s` && touch "$SCRATCH/3time.txt" && echo  Condition 3 execution time was `expr $end - $start` seconds. >> "$SCRATCH/3time.txt"

Rscript --no-save software/TACC_BootAnalyzeGroupsInCondition.R --cond=6Rats --iter=2000 && end=`date +%s` && touch "$SCRATCH/6time.txt" && echo  Condition 6 execution time was `expr $end - $start` seconds. >> "$SCRATCH/6time.txt"

Rscript --no-save software/TACC_BootAnalyzeGroupsInCondition.R --cond=9Rats --iter=2000 && end=`date +%s` && touch "$SCRATCH/9time.txt" && echo  Condition 9 execution time was `expr $end - $start` seconds. >> "$SCRATCH/9time.txt"

Rscript --no-save software/TACC_BootAnalyzeGroupsInCondition.R --cond=15Rats --iter=2000 && end=`date +%s` && touch "$SCRATCH/15time.txt" && echo  Condition 15 execution time was `expr $end - $start` seconds. >> "$SCRATCH/15time.txt"
