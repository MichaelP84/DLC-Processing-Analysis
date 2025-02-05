import specifications
import os
import pandas as pd
import numpy as np
import math
from multiprocessing import Pool

data_path = "" # should point to the folder that contains 3Rats, 6Rats, 9Rats, 15Rats

def main():

    all_approaches = pd.DataFrame(columns=["Condition", "Food", "Approaches"])

    for condition in os.listdir(data_path):

        approached_in_condition = pd.DataFrame(columns=["Condition", "Food", "Approaches"])
        cond_path = os.path.join(data_path, condition)

        for folder in os.listdir(cond_path):
            # print(folder)
            folder_path = os.path.join(cond_path, folder)

            # avg_pos = os.path.join(folder_path, os.listdir(folder_path)[0])
            print(folder_path)

            data_pre = []
            data_post = []
            for csv in (os.listdir(folder_path)):
                d = pd.read_csv(os.path.join(folder_path, csv))
                pre = d[d['food_label'] == 0]
                post = d[d['food_label'] == 1]

                pre = pre.drop(columns=['Unnamed: 0', 'food_label'], axis=1)
                post = post.drop(columns=['Unnamed: 0', 'food_label'], axis=1)
                data_pre.append(pre)
                data_post.append(post)

            work_pre= []
            for i in range(len(data_pre)):
                work_pre.append((i, data_pre))

            p1 = Pool(len(data_pre))
            pre_approaches = p1.starmap(trackRatX, work_pre) 
            print("done!")
            new_row_pre = pd.DataFrame({'Condition': [condition], 'Food': 'pre', 'Approaches': [sum(pre_approaches)/2]})

            work_post= []
            for i in range(len(data_post)):
                work_post.append((i, data_post))

            p2 = Pool(len(data_post))
            post_approaches = p2.starmap(trackRatX, work_post) 
            print("done!")
            new_row_post = pd.DataFrame({'Condition': [condition], 'Food': 'post', 'Approaches': [sum(post_approaches)/2]})

            # Concatenate the original DataFrame and the new row
            approached_in_condition = pd.concat([approached_in_condition, new_row_pre], ignore_index=True)
            approached_in_condition = pd.concat([approached_in_condition, new_row_post], ignore_index=True)

            # print(approaches)
            #print(f'{folder} {len(approaches)}: {sum(approaches)/2}')

        all_approaches = pd.concat([all_approaches, approached_in_condition], ignore_index=True)



    print(all_approaches.head())
        
    all_approaches.to_csv(path_or_buf="all_approaches.csv")


# for a given rat i, tracks its approach behavior onto all other rats
def trackRatX( i: int, individual_pd: list,):
    print('I am number %d in process %d' % (i, os.getpid()))
    print ("started task {}".format(i))

    # how many frames the rat should be < 'approach_distance' from another to count as an approach behaviours
    approach_frames = round(specifications.approach_time * specifications.frames_per_sec)
    # print('approach frames ', approach_frames)

    total_interactions = 0
  
    for j in range (len(individual_pd)):
        # there is a column for every body parts, the rows indicate interactions
        # also a column for time of interactions
        approach_to_j = 0
        
        #comparing every animal to each other, so exclude comparing to self
        if (i != j):
            frame = 0 # total frames = frame + skipped frames
            engagement_frames = 0 # number of frames less than a distance
            null_frames = 0
            # go through the whole video comparing rat i with rat j
            while frame < (len(individual_pd[i])):
                x, y = individual_pd[i].iloc[frame, :]
                while (math.isnan(x) and frame < len(individual_pd[i])):
                    frame += 1
                    if frame < len(individual_pd[i]):
                        x, y = individual_pd[i].iloc[frame, :2]

                if (frame < len(individual_pd[i])):
                    other_x, other_y = individual_pd[j].iloc[frame, :]
                    
                    if not math.isnan(other_x):
                        min_distance = getDistance(x, y, other_x, other_y)
                        # print(min_distance)

                        if (min_distance < specifications.approach_distance): # approach distance is in inches
                            # print(x, y, other_x, other_y)
                            engagement_frames += 1
                            if (engagement_frames >= approach_frames):
                                approach_to_j += 1
                                engagement_frames = 0
                                null_frames = 0
                    
                        else:
                            engagement_frames = 0
                            null_frames = 0
                            
                    elif (null_frames < specifications.null_frame_tolerance):
                            null_frames += 1
                    
                frame += 1
        
        total_interactions += approach_to_j

        # if j > 1:
        #     break

    print ("finished task {}".format(i))
    return total_interactions

def getDistance(x1, y1, x2, y2):
    return convertPixelToInch(math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2)))

def convertPixelToInch(x):
    return x / specifications.pixel_to_inch 


if __name__ == '__main__':
    main()