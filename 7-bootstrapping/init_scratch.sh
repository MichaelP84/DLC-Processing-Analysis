#!/bin/bash
echo Copying data and software into scratch ...

##mkdir $SCRATCH/Run/

tar -cvf ./temp_soft.tar ./software # compress software
tar -xvf temp_soft.tar -C $SCRATCH/Run/ # extract software in scratch
rm temp_soft.tar # remove home compression

cp /home1/09634/michaelp3844/MonfilsLab/mother_bootstrapping.bash $SCRATCH/Run/ # copy bootstrapping job
cp /home1/09634/michaelp3844/MonfilsLab/runserial.bash $SCRATCH/Run/ # copy bootstrapping job

## tar -xvf dataR.tar.gz -C $SCRATCH/Run/ # extract data 

echo done!