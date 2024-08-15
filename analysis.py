import cv2
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os
from scipy import stats
warnings.filterwarnings('ignore')



def getArea(line1Path, line2Path):
    line1 = np.load(line1Path)
    line2 = np.load(line2Path)

    x = list(range(1,line1.shape[1]))
    # y = [0] * (line1.shape[1])
    y = np.zeros((line1.shape[1],1))
    # print(y.shape)
    for i in x:
        line1Y = np.where(line1[: ,i] == 1)[0]
        line2Y = np.where(line2[: ,i] == 1)[0]
        # print(line1Y.size, line2Y.size)
        if line1Y.size != 0 and line2Y.size != 0:
            y[i] = np.median(line1Y) - np.median(line2Y)
        else:
            y[i] = 0

    # print(type(y))
    # y = y[np.where(y != 0)]
    # y = y[300:-300]
    lines = line1+line2
    y[y==0] = np.nan

    y[:500] = np.nan
    y[3800:] = np.nan


    f, (ax1,ax2) = plt.subplots(2, 1, height_ratios=[10,4], sharex=True, figsize=(6,10))
    ax1.imshow(lines, origin='upper', aspect='auto')



    ax2.plot(y)

    # plt.figure()
    # plt.subplot(2,1,1)
    # plt.imshow(lines)
    # plt.subplot(2,1,2)
    # plt.plot(y)

    plt.show()

    print('mean:', y[~np.isnan(y)].mean())
    print('SD:', y[~np.isnan(y)].std())
    # print('trimmed mean:', stats.trim_mean(y, 0.1) )

cwd = os.getcwd()
line1Path = os.path.join(cwd, 'tests/CCC_K10_FL1_s2_Layers/LineData/C5GLL.npy') #Lower
# line2Path = os.path.join(cwd, 'CCC_K01_FL1_Layers/LineData/GZAP.npy')
line2Path = os.path.join(cwd, 'tests/CCC_K10_FL1_s2_Layers/LineData/SOGUL.npy') #Upper

getArea(line1Path, line2Path)