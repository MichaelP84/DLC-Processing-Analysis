import os
import pandas as pd
import specifications
import numpy as np

csv_path = specifications.csv_path
frames_to_skip = specifications.minutes_to_skip * 3600
analysis_path = specifications.analysis_path

def main():

    feeding_time_path = ''
    for file in os.listdir(csv_path):
        if file.endswith(".xlsx"):
            feeding_time_path = os.path.join(csv_path, file)

    feeding_times = pd.read_excel(feeding_time_path)

    save = "./food_labeled"
    if (not os.path.exists(save)):
        os.mkdir(save)
    
    tag = 'DLC\\Average_Position'
    for row in range(len(feeding_times)):
        file, min, sec = feeding_times.iloc[row, -3:]
        position_path = specifications.analysis_path + '\\' + file + tag
        print(f'\t{position_path}')
        drop_frame = (60 * sec) + (3600 * min) - frames_to_skip # since the analysis starts at the frame skipped to, subtract frames skipped
        
        if not (os.path.exists(save + "\\" + file + "DLC")):
            os.mkdir(save + "\\" + file + "DLC")
        download_to = save + "\\" + file + tag
        os.mkdir(download_to)
        for data in os.listdir(position_path):
            path = os.path.join(position_path, data)
            pos = pd.read_csv(path)
            pos["food_label"] = np.where(pos["Unnamed: 0"] > drop_frame, 1, 0)
            pos = pos.drop('Unnamed: 0', axis=1)
            
            pos.to_csv(download_to + f'\\{data}')




if __name__ == "__main__":
    main()