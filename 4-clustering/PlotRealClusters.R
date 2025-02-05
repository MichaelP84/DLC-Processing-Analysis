###### Plot real data and boot data overlaid #########
library(tidyverse)
library(ggplot2)
library(glue)
library(grid)
### Load files first! ####
## If the files are not in your working directory, you will need to 
## specify the path, or load the files "by hand" (and comment out the 
## load() lines below)

n_rats <- 9

#load("15RatsClusterSummary.RData")
load(paste0("Cluster/", n_rats, "RatsClusterSummary.RData"))  # make sure this path is correct


### files loaded ###

# thresholding parameters
min_grp_size <- 3
min_grp_len <- 10


##### Group sizes plot with SEM #####

title_str <- paste(n_rats, "Rats") 

# threshold for minimum group lifetime
plt_lengths <- cluster_lengths_sizes[cluster_lengths_sizes$lengths > min_grp_len, ]
plt_lengths$lengths <- (plt_lengths$lengths)/60 # convert to seconds

grp_breaks <- seq(0, 16)
size_hist_info <- hist(plt_lengths$values, breaks = grp_breaks, plot = FALSE)

# Create histograms for each run_label
run_labels <- unique(plt_lengths$run_label)
bin_counts <- matrix(NA, nrow = length(size_hist_info$breaks) - 1, ncol = length(run_labels))

for (i in 1:length(run_labels)) {
  label_data <- plt_lengths$values[plt_lengths$run_label == run_labels[i]]
  label_hist <- hist(label_data, breaks = size_hist_info$breaks, plot = FALSE)
  bin_counts[, i] <- label_hist$counts
}

# Calculate average counts and standard errors
avg_counts <- rowMeans(bin_counts, na.rm = TRUE)
stderr <- apply(bin_counts, 1, function(x) sd(x, na.rm = TRUE) / sqrt(length(x)))

# Prepare data for ggplot
size_plot_data <- data.frame(bin_mid = size_hist_info$mids, avg_counts = avg_counts, stderr = stderr)

size_overlay <- ggplot() +
  geom_bar(data = size_plot_data, aes(x = bin_mid, y = avg_counts), stat = "identity", fill = "blue", alpha = 0.7) +
  geom_errorbar(data = size_plot_data, aes(x = bin_mid, ymin = avg_counts - stderr, ymax = avg_counts + stderr), width = 0.1) +
  #geom_bar(data = size_summary, 
  #         aes(x = size_mids, y = size_mean), 
  #         stat="identity") +
  #geom_errorbar(data = size_summary,
  #              aes(x = size_mids, 
  #                  ymin = size_mean - size_sd, 
  #                  ymax = size_mean + size_sd),
  #              width = 0.25  # Width of the error bars
  #) +
  coord_cartesian(ylim = c(0, 220)) +
  ggtitle(title_str) +
  labs(y = "Number of Clusters", x = "Cluster Size", title = title_str) +
  theme(
    #plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 14, face = "bold"),
    axis.text = element_text(face = "bold")
  )

print(size_overlay)



#### Group lifetime with SEM ####


### make group duration histogram ###
# Create overall histogram to get bin edges
dur_breaks <- seq(0, 15, length.out = 75) # why isn't this working for breaks?
dur_hist_info <- hist(plt_lengths$lengths, breaks = dur_breaks, plot = FALSE)

# Create histograms for each run_label
run_labels <- unique(plt_lengths$run_label)
bin_counts <- matrix(NA, nrow = length(dur_hist_info$breaks) - 1, ncol = length(run_labels))

for (i in 1:length(run_labels)) {
  label_data <- plt_lengths$lengths[plt_lengths$run_label == run_labels[i]]
  label_hist <- hist(label_data, breaks = dur_hist_info$breaks, plot = FALSE)
  bin_counts[, i] <- label_hist$counts
}
write.csv(bin_counts, file=glue("/Users/michaelpasala/Research/MovementLab/plots/RealAndBoot/Real/individual/{n_rats}_lifetime.csv"))

# Calculate average counts and standard errors
avg_counts <- rowMeans(bin_counts, na.rm = TRUE)
stderr <- apply(bin_counts, 1, function(x) sd(x, na.rm = TRUE) / sqrt(length(x)))

# Actual Plotting

# Prepare data for ggplot
lifetime_plot_data <- data.frame(bin_mid = dur_hist_info$mids, avg_counts = avg_counts, stderr = stderr)

#p <- ggplot(plot_data, aes(x = bin_mid, y = avg_counts)) +
#  geom_bar(stat = "identity", fill = "blue", alpha = 0.7) +
#  geom_errorbar(aes(ymin = avg_counts - stderr, ymax = avg_counts + stderr), width = 0.1) +
#  xlim(0, 6) +
#  xlab("Group Duration (sec)") +
#  ylab("Average Count") +
#  ggtitle(title_str)
#show(p)


nRats <- max(cluster_dat$rat_num) # number of rats
title_str <- paste(nRats, "Rats") # number of rats for figure titles


len_overlay <- ggplot() +
  geom_bar(data = lifetime_plot_data, aes(x = bin_mid, y = avg_counts), stat = "identity", fill = "blue", alpha = 0.7) +
  geom_errorbar(data = lifetime_plot_data, aes(x = bin_mid, ymin = avg_counts - stderr, ymax = avg_counts + stderr), width = 0.1) +
  #geom_errorbar(data = lifetm_summary, 
  #              aes(x = lifetm_mids, 
  #                  ymin = lifetm_mean - lifetm_sd, 
  #                  ymax = lifetm_mean + lifetm_sd),
  #              width = 0.25  # Width of the error bars
  #) +
  #geom_bar(data = lifetm_summary, 
  #         aes(x = lifetm_mids, y = lifetm_mean), 
  #         stat="identity") +
  # geom_histogram(data = plt_lengths, aes(x = lengths),
  #                 breaks = seq(0, 20, 0.2), fill = "pink", alpha = 0.5) +
  xlim(0, 6) +
  coord_cartesian(ylim = c(0, 200)) +
  labs(y = "Mean Counts", x = "Group Lifetime (sec)", title = title_str) +
  theme(
    #plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 14, face = "bold"),
    axis.text = element_text(face = "bold")
  )
print(len_overlay)


