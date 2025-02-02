import pandas as pd
import numpy as np
import math
import os
from multiprocessing import Pool

# general
minutes_to_skip = 3
frames_per_sec = 60
frames_to_skip = minutes_to_skip * 60 * frames_per_sec

def main():
  
  csv_path = "./csv"
  
  csv_list = []
  file_names = []
  
  # create a folder to house all the analysis
  directory = os.getcwd()
  folder = "processed"
  main_path = os.path.join(directory, folder)

  if not os.path.exists(main_path):
    os.mkdir(main_path)
  
  # adds all the csv paths to a list
  for filename in os.listdir(csv_path):      
    file_names.append(filename)
    f = os.path.join(csv_path, filename)
    if os.path.isfile(f):
      csv_list.append(f)
      
  for i, csv_path in enumerate(csv_list):
    print("\n\n\n----------File {}/{}-----------".format(i + 1, len(csv_list)))

    # create a file for every csv
    file_name = file_names[i]
    head = file_name.split('.')[0]
    head = "Average_Position_" + head

    working_directory = os.path.join(main_path, head)
    
    if not os.path.exists(working_directory):
      os.mkdir(working_directory)
    
    # read in csv file
    data = pd.read_csv(csv_path)
    data = data.iloc[:, 1:]

    # get lists of unique individuals and bodyparts
    individuals = np.unique(data.iloc[0].values)
    bodyparts = np.unique(data.iloc[1].values)
    num_individuals = individuals.size
    num_bodyparts = bodyparts.size
    
    individual_pd = []

    #1. creating a list of data sets where each index is a different animal
    for i, individual in enumerate(individuals):
        individual_data = data.iloc[:, 3 * num_bodyparts * i:3 * num_bodyparts * (i + 1)]
        individual_pd.append(individual_data)
  
    #2. renaming column titles
    bodypart = individual_pd[0].iloc[1].values
    value = individual_pd[0].iloc[2].values
    column_titles = []
    for i in range (len(bodypart)):
        column_titles.append(bodypart[i] + '_' + value[i])
    for i in range(len(individual_pd)):
      individual_pd[i] = individual_pd[i].iloc[3:]
      individual_pd[i].columns = column_titles
    
    #3. dropping likelyhood columns
    for i in range (len(individual_pd)):
      columns_to_drop = []
      for x, column in enumerate(individual_pd[i].columns):
          if (x + 1) % 3 == 0:
              columns_to_drop.append(column)
      individual_pd[i].drop(columns_to_drop, inplace=True, axis=1)
    
    #3. skipping forward x minutes
    for i in range(len(individual_pd)):
        individual_pd[i] = individual_pd[i].iloc[frames_to_skip:]
        individual_pd[i].reset_index(drop=True, inplace=True)

    animals = []
    for i in range (len(individual_pd)):
      animals.append('rat_{}'.format(i))

    #4. creating an average position point, not including tail data
    # each animal's calcualtions is done simultanesouly on a different thread
    path = working_directory
        
    # if the avg position calculations have not been run already, run them
    work = []
    for i in range (len(individual_pd)):
      x = (individual_pd, i)
      work.append(x)
    
    p = Pool(num_individuals)
    average_pd = p.starmap(getAverage, work)  
    
    for i, avg in enumerate(average_pd):
      filename = "rat{}_avg.csv".format(i)
      single_path = os.path.join(path, filename)
      avg.to_csv(path_or_buf=single_path)

    
# returns the average x and average y point of a list of points (x1, y1, x2, y2, x3, ...)    
def getAverage(individual_pd, i):
  average_x = []
  average_y = []

  print ("started task {}".format(i))
  for frame in range (len(individual_pd[i])):
    sum_x = 0
    sum_y = 0
    count = 0
    
    for j in range (len(individual_pd[i].columns) - 4): # minus four columns to remove tail points
      if j % 2 == 0:    
        pos_x = individual_pd[i].iloc[frame, j]

        if (not math.isnan(pos_x)):
          sum_x += pos_x
          count += 1
      else:
        pos_y = individual_pd[i].iloc[frame, j]
          
        if (not math.isnan(pos_y)):
          sum_y += pos_y
      
    if (count == 0):
      average_x.append(None)
      average_y.append(None)
    else:
      avg_x = sum_x / count 
      average_x.append(avg_x)
      avg_y = sum_y / count
      average_y.append(avg_y)
    
  average_pd = pd.DataFrame()
  average_pd['average_x'] = average_x
  average_pd['average_y'] = average_y
  print ("finished task {}".format(i))
  
  return average_pd

if __name__ == "__main__":
 main()
