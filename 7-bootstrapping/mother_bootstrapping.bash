#!/bin/bash

## Track Time
start=`date +%s`

Rscript --no-save software/BootMotherAnalyzeGroupsInCond.R --cond=3 --iter=2000

Rscript --no-save software/BootMotherAnalyzeGroupsInCond.R --cond=6 --iter=2000

Rscript --no-save software/BootMotherAnalyzeGroupsInCond.R --cond=9 --iter=2000

Rscript --no-save software/BootMotherAnalyzeGroupsInCond.R --cond=15 --iter=2000