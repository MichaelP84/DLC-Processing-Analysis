import pandas as pd
import numpy as np
import math
from multiprocessing import Pool
import itertools
import os
import specifications

# general
minutes_to_skip = specifications.minutes_to_skip
frames_per_sec = specifications.frames_per_sec
frames_to_skip = minutes_to_skip * frames_per_sec * frames_per_sec
pixel_to_inch = specifications.pixel_to_inch
debug = specifications.debug
titles = specifications.titles
download_raw_approaches = specifications.download_raw_approaches
thresholds = specifications.thresholds

# Blue color in BGR
color = (255, 0, 0)
red = (0, 0, 255)

def main():
  
  # velocity and distance
  velocity_bin = specifications.velocity_bin
  avg_point_only = specifications.avg_point_only
  
  # points
  csv_path = specifications.csv_path
  video_path = specifications.video_path
  
  csv_list = []
  file_names = []
  
  # create a folder to house all the analysis
  directory = os.getcwd()
  folder = "Analysis"
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
    head, _, _ = file_name.partition('_resnet50')

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
    directory = "Average_Position"  
    path = os.path.join(working_directory, directory)
        
    # if the avg position calculations have not been run already, run them
    if not os.path.exists(path):
      os.mkdir(path)
      print("Directory '{}' created at '{}' ".format(directory, path))
      work = []
      print(video_path)
      for i in range (len(individual_pd)):
        x = (individual_pd, i)
        work.append(x)
      
      p = Pool(num_individuals)
      average_pd = p.starmap(getAverage, work)  
      
      for i, avg in enumerate(average_pd):
        filename = "rat{}_avg.csv".format(i)
        single_path = os.path.join(path, filename)
        avg.to_csv(path_or_buf=single_path)

    
    # otherwise, load data from existing folder
    else:
      print("Skipping Average Point calculations because directory Average_Point exists")
      average_pd = []
      for i, csv in enumerate(os.listdir(path)):
        f = os.path.join(path, csv)
        data = pd.read_csv(f)
        data = data.drop(data.columns[0], axis=1)
        average_pd.append(data)

    if (not avg_point_only):
      # calculate all statistics

      #5. calculating velocity and distance in bins
      # assuming the nose is the basis of the movement
      # curently skips over nan values
      velocity_path = os.path.join(working_directory, 'velocity.csv')
      distance_path = os.path.join(working_directory, 'total_distance.csv')
      if not os.path.exists(velocity_path) or not os.path.exists(distance_path):
        print("Calculating velocity...")
        work = []
        
        for i in range (len(individual_pd)):
          w = (i, individual_pd, velocity_bin)
          work.append(w)

        p = Pool(num_individuals)
        results = p.starmap(getVelocity, work) # multi-processing
              
        velocity = pd.DataFrame()
        total_distance = pd.DataFrame()

        for i in range(len(results)):
        
          total_distance[f'rat_{i}'] = [results[i][1]]
          velocity[f'rat_{i}'] = results[i][0]
        
        velocity.to_csv(velocity_path)
        total_distance.to_csv(distance_path)

        print("\t ...done")
          
      else:
        print("Skipping Veloctity and Distance calculations because directory 'velocity.csv' and 'total_distance.csv' already exists")

      
class Combination:
  def __init__(self, threshold: int, comb: list, centriod: tuple) -> None:
    self.centriod = centriod
    self.framesLeft = threshold
    self.bufferFrames = 4
    self.comb = comb
    self.frames = []
  
  def isWithin(self, newCombinations: list) -> bool:
    return any(group == self.comb for group in newCombinations)
  
  def subtract_time(self) -> None:
    if (self.framesLeft > 0):
      self.framesLeft -= 1
  
  def buffer(self):
    self.bufferFrames -= 1
  
  def hasBuffer(self) -> bool:
    return self.bufferFrames > 0
    
  def isCleared(self) -> bool:
    return self.framesLeft == 0
  
  def addFrame(self, f) -> None:
    self.frames.append(f)
    
  def getFrames(self) -> list:
    return self.frames
  
  def getCentriod(self) -> tuple:
    return self.centriod

  def wraps(self, comb: list) -> bool:
    return self.comb == comb
  
  def getList(self) -> list:
    return self.comb

# returns the binned velocity for rats over time
def getVelocity(i: int, individual_pd: list, velocity_bin: int):  
  
  max_inputs = (len(individual_pd[i]) // velocity_bin)

  velocity_singular = [] # velocity list for a single animal
  total_distance = 0
  
  frame = 0
  while frame < len(individual_pd[i]):
      # get current x and y position
      prev_x, prev_y = individual_pd[i].iloc[frame, :2] # 2 refers to nose since they are the first 2 points
      # skipping over nan frames
      while (math.isnan(prev_x)):
              frame += 1
              prev_x, prev_y = individual_pd[i].iloc[frame, :2]
      
      # get next non-nan x and y position
      frame += velocity_bin
      if (frame < len(individual_pd[i])):
          next_x, next_y = individual_pd[i].iloc[frame, :2]
          
          frames_added = 0
          while (math.isnan(next_x) and frame < len(individual_pd[0])): # add frames until next non-nan frame
              frame += 1
              frames_added += 1
              if (frame < len(individual_pd[0])):
                next_x, next_y = individual_pd[i].iloc[frame, :2]
          
          if (frame < len(individual_pd[0])):
            #calculate the distance traveled in the bin for total distance and velocity (inches)
            dist = getDistance(prev_x, prev_y, next_x, next_y)
            total_distance += dist
            
            time = (velocity_bin + frames_added) / frames_per_sec
            temp_velocity = dist / time
            velocity_singular.append(temp_velocity)
  
  while (len(velocity_singular) < max_inputs):
    velocity_singular.append(None)
  
  return velocity_singular, total_distance
  
      
# given a list of cluster and a new combination, return true if any item in the combination
# is already within a cluster
def contain(clusters: list, comb: list) -> bool:
  
    for group in clusters:
      if (any(item in group for item in comb) == True):
        return True
    
    return False

# represents a rat's average point
class Rat_Point:

  def __init__(self, x: float, y: float, index: str):
    self.x = x
    self.y = y
    self.name = "rat_" + index
  
  def __eq__(self, other):
    if isinstance(other, self.__class__):
        return self.name == other.name
    else:
        return False
    
  def getCoordinates(self):
    return self.x, self.y

  def __str__(self):
    return self.name
  
  def __repr__(self):
    return self.name

  def getName(self):
    return self.name
  
  def isNan(self):
    return math.isnan(self.x)
  
  def getPointDistance(self, Rat_Point):
    other_x, other_y = Rat_Point.getCoordinates()
    return getDistance(self.x, self.y, other_x, other_y)
  
# returns every combination of rats in 'arr' of 'choose' size
def getCombinations(arr: list, choose: int):
  combinations = []
  for comb in itertools.combinations(arr, choose):
    combinations.append(comb)
  
  return combinations
  
# determine if the rats in arr form a cluster
# threshold is in inches
def isACluster(arr: list, threshold: int, frame: int) -> bool:
  count = 0
  sum_x = 0
  sum_y = 0
  for rat in arr:
    count += 1
    x, y = rat.getCoordinates()
    sum_x += x
    sum_y += y
  
  avg_x = sum_x / count
  avg_y = sum_y / count
  
  temp_x = avg_x
  temp_y = avg_y
   
  max = 0
  for rat in arr:
    rat_x, rat_y = rat.getCoordinates()
    dist = getDistance(rat_x, rat_y, avg_x, avg_y)
    if dist > max:
      max = dist

    if (specifications.cluster_debug):
      if (dist > threshold + 1):
        return False, False, None
    else: 
      if dist > threshold:
        # not a cluster
        return False, False, None
  
  if (specifications.cluster_debug and max > threshold and max <= threshold + 1):
    # perimeter cluster exists but not regular cluster
    return False, True, [temp_x, temp_y, threshold]
  # only regular cluster exists
  return True, False, [temp_x, temp_y, threshold]

# for a given rat i, tracks its approach behavior onto all other rats
def trackRatX(approach_distance: float, approach_time: float, null_frame_tolerance: int, i: int, individual_pd: list, rat_path: str):
  # print('I am number %d in process %d' % (i, os.getpid()))
  print ("started task {}".format(i))

  # how many frames the rat should be < 'approach_distance' from another to count as an approach behaviours
  approach_frames = round(approach_time * frames_per_sec)  
  
  # each element in approach_singular is a dataframe of interactions with the other rats
  approach_singular = []
  
  counts = np.zeros(len(individual_pd), dtype=np.intc)  
  saved_frames = []
  debugging_approaches = []
  
  for j in range (len(individual_pd)):
      # there is a column for every body parts, the rows indicate interactions
      # also a column for time of interactions
      approach_to_j = pd.DataFrame(columns=titles)
      
      #comparing every animal to each other, so exclude comparing to self
      path = rat_path
      if (i != j):
        frame = 0 # total frames = frame + skipped frames
        engagement_frames = 0 # number of frames less than a distance
        null_frames = 0
        # go through the whole video comparing rat i with rat j
        while frame < (len(individual_pd[i])):
            nose_x, nose_y = individual_pd[i].iloc[frame, :2]
            while (math.isnan(nose_x) and frame < len(individual_pd[i])):
                frame += 1
                if frame < len(individual_pd[i]):
                  nose_x, nose_y = individual_pd[i].iloc[frame, :2]

            if (frame < len(individual_pd[i])):
              
              bodyparts = individual_pd[j].iloc[frame, :-4] # exclude last four columns because they refer to points on the rat's tail
              
              min_index, min_distance, min_list = findMinDistance(bodyparts, nose_x, nose_y)
              # min_distance in inches

              if (not min_index is None and min_distance < approach_distance): # approach distance is in inches
                engagement_frames += 1
                if (engagement_frames >= approach_frames):
                  
                  # for debugging keep a list of interactions and the frames they happen
                  if (debug):
                    # print(f'Frame {frame + frames_to_skip} \t Engangement_frames {engagement_frames} > {approach_frames} \t {min_distance} < {approach_distance}')
                    adjusted_frame = frame + frames_to_skip
                    saved_frames.append(adjusted_frame)
                    debugging_approaches.append([nose_x, nose_y])
                  
                  counts[j] += 1
                  
                  if (download_raw_approaches):
                    min = pd.DataFrame(min_list).T
                    min.columns = titles
                    approach_to_j = pd.concat([approach_to_j, min], axis=0, ignore_index=True)
                  
                  engagement_frames = 0
                  null_frames = 0
                
              elif (min_index is None and null_frames < null_frame_tolerance):
                null_frames += 1

              else:
                engagement_frames = 0
                null_frames = 0
              
              frame += 1
            
        if (download_raw_approaches):
          approach_singular.append(approach_to_j)
        
      elif (download_raw_approaches):
          approach_singular.append(['same animal'])

      if (download_raw_approaches):
        filename = "rat{}_to_rat{}.csv".format(i, j)
        path = os.path.join(path, filename)
        approach_to_j.to_csv(path_or_buf=path)
  
  print ("finished task {}".format(i))
  return saved_frames, debugging_approaches, counts
  
# from a list of x and y points for body parts, return the min, its distance (inches) and its index
def findMinDistance(bodyparts: list, nose_x: float, nose_y: float):
    min_index = -1
    min_distance = 1_000
    min_list = [None] * (round(len(bodyparts) / 2))
    # divide by 2 because we are going from a list with two columns for every body point (x and y) to just every body point

    i = 0
    while (i < len(bodyparts)):
        part_x = bodyparts[i]
        part_y = bodyparts[i + 1]
        
        if (not part_x is None):
            distance = getDistance(nose_x, nose_y, part_x, part_y)
            if (distance < min_distance):
                min_distance = distance
                min_index = i
            
        i += 2
    
    if (min_index == -1):
        return None, None, min_list
    
    min_list[round(min_index/2)] = min_distance
    return min_index, min_distance, min_list
  
      
# returns the distance between two points (inches)
def getDistance(x1, y1, x2, y2):
    return convertPixelToInch(math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2)))

# converts a pixel length to inches
def convertPixelToInch(x):
  return x / pixel_to_inch

# converts a inch to pixel
def convertInchToPixel(x):
  return x * pixel_to_inch

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

def time_convert(sec) -> None:
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60
  print("Time Lapsed = {0}:{1}:{2}".format(int(hours),int(mins),sec))
  
def printTime(frame: int) -> None:
  sec = frame // 60 % 60
  min = frame // 3600
  print(f'Frame: {frame}, Minute: {min}, Second: {sec}')
  
def getTime(frame: int) -> None:
  sec = frame // 60 % 60
  min = frame // 3600
  return(f'{min}:{sec}')

if __name__ == "__main__":
 main()
