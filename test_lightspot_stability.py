#%%
import os
from miscmath import fit_circle
import numpy as np
import matplotlib.pyplot as plt
import time
import pandas as pd
import bench as bench
from progress.bar import Bar

cam, allpos, pos21, pos22, pos23, pos24, pos25, pos26 = bench.bench_init()

POSID = 25
TEMP = 5
#%%
nb_images = 100
waiting_time = 0.2 # [s]
results_dict = {"x": [],
                "y": [],
                }

print(f"Starting image burst")
with Bar('Taking images') as bar:
    for i in range(nb_images):
        x,y = cam.getCentroid()
        results_dict['x'].append(x)
        results_dict['y'].append(y)
        time.sleep(waiting_time)
        bar.next()
print("Image burst done")
#%%
# Compute repeatability
df = pd.DataFrame(results_dict)
df.to_csv('measurement_noise_pos22_chamber_on_minus10degrees_15000us_expo.csv')
#%%
res_x = np.array(results_dict['x'])
res_y = np.array(results_dict['y'])

meanX = np.mean(res_x)
meanY = np.mean(res_y)
distanceX = res_x - meanX
distanceY = res_y - meanY
distances = np.sqrt(distanceX **2 + distanceY ** 2)
repeatability =  np.std(distances)
print(f"Measurement noise = {repeatability*1000} um")    
