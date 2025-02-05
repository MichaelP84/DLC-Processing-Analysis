# DLC Analysis and Reporting

To follow this repo, you should have already trained a pose estimation model in DLC, and have run the model on videos to create output csv’s.

## 1. Processing DLC Data

The output csv of one video will be structured as so:

- There will be 3 columns for every point in the video: x, y, and likelihood.
- There will then be n points for every rat, depending on the number of points you trained the model with.
- And there will be m rats, depending on how many are in the video

Put all your csv data in /csv, remove the file titled "remove_this" and run MovementExtraction.py

## 2. Speed Analysis

## 1. Distance Analysis

## 1. Clustering Analysis
