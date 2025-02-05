library(tidyverse)
library(rstudioapi)
library(dplyr)
library(tidyr)
library(glue)
library(readr)

approaches <- read_csv("/Users/michaelpasala/Research/MovementLab/all_approaches.csv")

approaches <- approaches[, 2:3]
approaches$Condition <- as.factor(approaches$Condition)

ggplot(approaches, aes(Condition, Approaches, fill=Condition)) + 
  geom_violin() +
  xlab("Total Approaches") +
  ylab("Condition") + 
  ggtitle("Approaches Across Conditions") +
  theme_classic()
