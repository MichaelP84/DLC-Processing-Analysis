# 1. Processing DLC Data

The output csv of one video from DLC inference will be structured as so:

- There will be 3 columns for every point in the video: x, y, and likelihood.
- There will then be n points for every rat, depending on the number of points you trained the model with.
- And there will be m rats, depending on how many are in the video

Put all your csv data in /csv, remove the file titled "remove_this" and run MovementExtraction.py.

Now, the all the outputs will be in the /Analysis folder.

Next, we are going to add the food drop column, which indicates if the frame was pre or post food drop. The food drop csv should have 3 columns: file, min, sec. The file column contains the name of the csv this record refers to. The min refers to the minute at which the food was dropped. The second contains the second of the minute when the food was dropped. This csv was created manually.
An example can be found here: https://utexas.box.com/s/78v6epa0hgty5cgxwdpfels88lxkmj4a

Update the _feeding_time_path_ variable to point towards your data then run **food_label.py**.

Now you should have a recreation of all the data that was in Analysis, but with a food_label column.

Finally, create a folder /data and put all your analyzed in this folder in this strucutre:

/data

> /3Rats

- Average_Position_01
- Average_Position_02

> /6Rats

- Average_Position_01
- Average_Position_02

> /9Rats

- Average_Position_01
- Average_Position_02

> /15Rats

- Average_Position_01
- Average_Position_02

This is how your data should look now: https://utexas.box.com/s/83ruk7fnqasl8r46idirlqcqpi517xyv
