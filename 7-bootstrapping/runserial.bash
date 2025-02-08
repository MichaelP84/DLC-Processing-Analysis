#!/bin/bash
#SBATCH -J all_condition_2000boot            # job name
#SBATCH -o all_condition_2000boot.o%j             # output and error file name (%j expands to SLURM jobID)
#SBATCH -N 1                        # number of nodes requested
#SBATCH -n 32                       # total number of tasks to run in parallel
#SBATCH -p normal              # queue (partition) 
#SBATCH -t 24:00:00                 # run time (hh:mm:ss) 

module load launcher

export LAUNCHER_WORKDIR=/scratch/09634/michaelp3844/Run
export LAUNCHER_JOB_FILE=/scratch/09634/michaelp3844/Run/bootstrapping.bash

${LAUNCHER_DIR}/paramrun