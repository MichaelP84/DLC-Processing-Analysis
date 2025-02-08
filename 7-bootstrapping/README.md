# 7. Bootstrapping

We ran bootstrapped trials within condition and across conditions on the TACC supercomputer lonestar6. We calculated clustering data in these bootsrapped trials

For all of the following files, make sure you go through the code and change any file paths to point towards the correct data and output locations.

First, make sure you still have all the position Rdata, and change the files paths for the code in /software to point to it.
Then use the SLURM cli to schedule the seriail_job.slurm job to run.

Changing the file in serial_job.slurm will change which gets run:

- bootstrapping.bash will run trials within condition
- mother_bootstrapping.bash will run trials across condition

After running this code, the same plotting code at (6) can be used for the resulting data.
