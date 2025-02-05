# Get binned velocity and total distance data for rats

library(tidyverse)
library(rstudioapi)
library(progress) # this script is going to take a while to run...
library(fpc)
library(glue)

BIN = 100 # frames
FPS = 60

# def function to get abs distance between two points
abs_distance <- function(x1, y1, x2, y2) {
  abs(sqrt((x1 - x2)^2 + (y1 - y2)^2))
}

# Pick a Condition
dir_path <- selectDirectory(caption = "Select Directory",
                            label = "Select",
                            path = getActiveProject())

# get list of the directories (runs) in in this condition
dir_list <- list.dirs(path = dir_path,
                      recursive = FALSE,
                      full.names = TRUE)
n_runs <- length(dir_list) # should always be 15

# Create a progress bar object
pb <- progress_bar$new(total = n_runs)

all_speeds = data.frame()

pb = txtProgressBar(min = 0, max = length(dir_list), initial = 0) 

############### big momma loop #############################
for (i in 1:length(dir_list)) {
  setTxtProgressBar(pb,i)
  
  # print(paste("In", dir_list[i])) # for debugging
  # load the list of files in this directory
  file_list <-
    list.files(path = dir_list[i],
               pattern = ".RData",
               full.names = TRUE)
  n_files <- length(file_list)
  
  # condition ID for the filename
  cond <- paste0('n_Rats', n_files)
  
  # create an empty data frame to hold the combined data
  tmp = data.frame()
  
  # load the .RData files for the rats in this run
  for (j in 1:length(file_list)) {
    # print(paste("Loading rat", j)) # for debugging
    # combine into one data frame
    load(file_list[j])
    tmp <- rbind(tmp, xyt_dat)
    
  } # end of looping through files for this run
  
  xyt_dat <- tmp
  
  ##### NA removal #########################################
  # Find the frames with NaNs in either data column
  nan_frames = xyt_dat[is.na(xyt_dat$x) | is.na(xyt_dat$y), 'frame']
  # Keep the frames that are *not* a member of nan_frames
  # this will omit a rat's data for a given frame if one of its
  # buddies has a NA on that frame, even if the first rat's data is valid...
  # Which is what we need.
  xyt_dat <- xyt_dat[!xyt_dat$frame %in% nan_frames$frame, ]
  #########################################################
  
  if (anyNA(xyt_dat)) {
    stop("NA's found after removing them!")
  }
  
  # create column that is the absolute val of change in distance
  xyt_dat <- xyt_dat %>% mutate(delta_pos = abs_distance(x, y, lag(x), lag(y)))
  
  # drop the first frame for each rat because its value is NULL
  nan_frames_pos = xyt_dat[is.na(xyt_dat$delta_pos), 'frame']
  xyt_dat <- xyt_dat[!xyt_dat$frame %in% nan_frames_pos$frame, ]

  if (anyNA(xyt_dat)) {
    nan_frames = xyt_dat[is.na(xyt_dat$delta_pos), ]
    print(nan_frames)
    stop("NA's found after removing the first row of run!")
  }
  
  #View(xyt_dat)
  
  # calculate expected number of bins
  rats <- unique(xyt_dat$rat_num) # list of rat nums
  num_rats <- length(rats)
  exp_bins <- as.integer(length(xyt_dat$frame) / (length(rats) * BIN))
  
  # data frame for all rats velocity bins in a run
  speed_bin_dat <- data.frame() #matrix(0, nrow = exp_bins, ncol = 1)
  
  # total distance for all rats instantaneous >? 
  total_dist <- c()
  # go through all rat nums 
  for (k in 1:length(rats)) {

    # get all rows for a single rat
    new_dat <- xyt_dat[xyt_dat$rat_num == rats[k],]
    # calculate total distance traveled
    traveled <-sum(new_dat$delta_pos)
    total_dist <- append(total_dist, traveled)
    
    col_name = glue('rat_{k}')
    new_bins = c() # holds binned velocity for one rat
    sum = as.double(0) # tracks sum of values in bin
    not_nan = as.integer(0) # tracks number of non nan frames in a bin
    
    prev_bin = 0
    # go through each frame for single rat
    for (m in 1:length(new_dat$frame)) {
      f <- as.integer(new_dat[m, 'frame'])
      curr_bin = f %/% BIN
      if (curr_bin - prev_bin == 1) {
        # the next frame is in the next bin (or two over, meaning a whole bin was NaN)
        
        avg <- sum / BIN # this averages every bin over the expected size
        # effect: the perceived high speed found between frames that had NaN frames between them is reduced
        # consequences: bins with a lot of NaN frames may have their avg watered down
        
        new_bins <- c(new_bins, avg)
        sum = 0
        not_nan <- 0
      }
      prev_bin <- curr_bin
      
      sum = sum + (as.double(new_dat[m, 'delta_pos']))
      not_nan <- not_nan + 1
    }
    # add bins for one rat to collective list
    if (nrow(speed_bin_dat) == 0) {
      speed_bin_dat <- data.frame(matrix(0, nrow = length(new_bins), ncol = 1))
    }
    speed_bin_dat[col_name] <- new_bins
  }
  # maybe there is a work around for this but I found that to add a list to an empty dataframe,
  # the initial length dimensions have to match, so here I am just dropping a empty column I made initally to allow me to concat the first list
  speed_bin_dat <- speed_bin_dat[ , 2:length(speed_bin_dat)]
  speed_bin_dat['run'] <- as.character(i)
  # save(speed_bin_dat, file=paste(dir_list[i],"speed_bin_dat.Rda", sep="/"))
  # View(speed_bin_dat)
  all_speeds <- rbind(all_speeds, speed_bin_dat)

}

if (anyNA(all_speeds)) {
  stop("NA's found after at the very end")
}

save(all_speeds, file=paste(dir_path,"all_speeds.Rda", sep="/"))