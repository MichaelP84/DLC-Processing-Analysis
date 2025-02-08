# 7. Bootstrapping

Two basic bootstrapping analyses were run. In the first, a simulation of a 3 rat run, for example, consisted only of trajectories from rats that were run in a 3 rat condition. In the other (the “mother” bootstrap), a simulation of a 3 rat run, for example, could consist of trajectories from rats that were run in any condition (3, 6, 9, or 15 rats). The idea here was to see if there were grouping differences based solely on how rats moved with different numbers of rats in the environment, independent of any particular social behavior of one rat reacting to the presence of another.

We ran bootstrapped trials within condition and across conditions on the TACC supercomputer lonestar6. We calculated clustering data in these bootsrapped trials

For all of the following files, make sure you go through the code and change any file paths to point towards the correct data and output locations.

First, make sure you still have all the position Rdata, and change the files paths for the code in /software to point to it.
Then use the SLURM cli to schedule the seriail_job.slurm job to run.

Changing the file in serial_job.slurm will change which gets run

#### TACC_BootAnalyzeGroupsInCondition.R

This is the main file that chews through the original data, and constructs bootstrap replicates based on actual rat trajectories, but that we’re not from the same actual run (recording). In other words, each “rat” in the bootstrap run could not have adjusted its behavior based on the other “rats” in the bootstrapped trial. The rats were, in effect, ghost rats that could not see, smell, or feel one another.

In this version, all rat trajectories come from the same condition. In other words, for a “3 rats” bootstrap run, all rat trajectories came from rats that ran with only 2 other rats.

It outputs a series of lists (one list for each bootstrap replication), where each list is a tibble of group sizes and lengths like the output of `AnalyzeGroupsInCondition.R` for the actual data.

#### BootMotherAnalyzeGroupsInCond.R

Same as above, except that a rat in a “3 rat” bootstrap replicate could have come from a 15 rat condition, i.e. might have been actually in the box with 14 other rats.

### Summarizing and plotting the results

Takes the output of the RLE analysis from the above code, computes histogram data (bins, counts) and plots the results. for the bootstrapping data, it plots the mean counts in each bin with error bars showing the standard deviations across bootstrap replications (i.e., the estimated standard errors).

#### PlotRealAndBootSummary.R

This takes the `cluster_lengths_sizes` from a actual rat data file, and a corresponding `rle_data_list` from the bootstrapping, each of which contains a tibble analogous to the `cluster_lengths_sizes` tibble from the experimental data, and then plots a histogram of the real data and the average histogram of the bootstrapping data (averaged across bootstrap replications).

NB: should modify to call `make_boot_hist.R` to be consistent and modular.

#### PlotBootVsBootDistributions.R

Computes and plots the histograms for the within-condition vs. “mother” bootstrapping findings. In other words, bootstrapping an _n_ rats condition using only only rats that were run in that condition vs. sampling from rats that were run in any condition. (So a 6 rat condition might be simulated from 6 trajectories from any of 3, 6, 9, and/or 15 experimental conditions).

##### make_boot_hist.R

The function called to compute the histogram values by the above script (and needs to be sourced by the calling script).
