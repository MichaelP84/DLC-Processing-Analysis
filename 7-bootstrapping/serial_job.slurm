#!/bin/bash

#SBATCH -J 9_Rat_run           # Job name
#SBATCH -o 9_Rat_run.o%j       # Name of stdout output file
#SBATCH -e 9_Rat_run.e%j       # Name of stderr error file
#SBATCH -p normal          # Queue (partition) name
#SBATCH -N 1               # Total # of nodes (must be 1 for serial)
#SBATCH -n 1               # Total # of mpi tasks (should be 1 for serial)
#SBATCH -t 00:15:00        # Run time (hh:mm:ss)
#SBATCH --mail-type=all    # Send email at begin and end of job
##SBATCH -A        # Project/Allocation name (req'd if you have more than 1)
#SBATCH --mail-user=michaelp3844@tacc.utexas.edu


## Start Time
start=`date +%s`

Rscript --no-save software/AnalyzeGIC_Static.R data/9rats

## End Time
end=`date +%s`

touch "$SCRATCH/time.txt"
echo Execution time was `expr $end - $start` Seconds. > "$SCRATCH/time.txt"