import cv2
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os
from scipy import stats
warnings.filterwarnings('ignore')



def getArea(line2Path, line1Path, savePath = None, customStart = None, customEnd = None):
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

    lines = line1+line2
    y[y==0] = np.nan
    yFinite = np.argwhere(np.isfinite(y)) #get indexes of non NaN to find endpoints of line

    start = yFinite[0][0] + 300
    end = yFinite[-1][0] - 300

    if customStart != None:
        start = customStart
    if customEnd != None:
        end = customEnd

    y[:start] = np.nan
    y[end:] = np.nan
    mean =  y[~np.isnan(y)].mean()
    sd =  y[~np.isnan(y)].std()


    f, (ax1,ax2) = plt.subplots(2, 1, height_ratios=[10,4], sharex=True, figsize=(6,10))
    ax1.imshow(lines, origin='upper', aspect='auto')

    
    textstr = '\n'.join((
    r'mean=%.2f' % (mean, ),
    r'SD=%.2f' % (sd, )))

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    ax2.plot(y)
    if savePath != None:
        plt.savefig(savePath)
    else:
        plt.show()
    # print('trimmed mean:', stats.trim_mean(y, 0.1) )
    return mean, sd, start, end

def getAvg(line1Path, line2Path, savePath=None): #layers path
    line1 = np.load(line1Path)
    line2 = np.load(line2Path)

    x = list(range(1,line1.shape[1]))
    # y = [0] * (line1.shape[1])
    y = np.zeros(line1.shape)
    # print(line1.shape)
    # print(line2.shape)
    for i in x:
        line1Y = np.where(line1[: ,i] == 1)[0]
        line2Y = np.where(line2[: ,i] == 1)[0]
        # print(line1Y.size, line2Y.size)
        if line1Y.size != 0 and line2Y.size != 0:
            # print(i)
            avg = (np.median(line1Y) + np.median(line2Y))/2
            y[int(avg)][i] = 1
            # print(y[i][x])
    y = cv2.dilate(y, kernel=np.ones((7,7), np.uint8))
    lines = line1+line2

    f, (ax1,ax2) = plt.subplots(2, 1, sharex=True, figsize=(6,10))
    ax1.imshow(lines, origin='upper', aspect='auto')
    ax2.imshow(y, aspect='auto')
    plt.show()
    # print('trimmed mean:', stats.trim_mean(y, 0.1) )
    if savePath != None:
        im = np.zeros((line1.shape[0], line1.shape[1],4))
        im[:, :, 0] = y*255
        im[:, :, 3] = y*255
        cv2.imwrite(os.path.join(savePath, os.path.join('LineImages', os.path.basename(line2Path) + '_' + os.path.basename(line1Path)+ '_Avg.png'), im))
        np.save(os.path.join(savePath, os.path.join('LineData', os.path.basename(line2Path) + '_' + os.path.basename(line1Path)+ '_Avg.npy'), y))


# cwd = os.getcwd()
# upPath = os.path.join(cwd, 'tests/CCC_K10_FL1_s2_Layers/LineData/DPUCL.npy')
# # line2Path = os.path.join(cwd, 'CCC_K01_FL1_Layers/LineData/GZAP.npy')
# lowPath = os.path.join(cwd, 'tests/CCC_K10_FL1_s2_Layers/LineData/DPUML.npy') 
# getArea(upPath, lowPath)


# line1Path = os.path.join(cwd, 'tests/CCC_K10_FL1_s2_Layers/LineData/C5GLL.npy') #Lower
# # line2Path = os.path.join(cwd, 'CCC_K01_FL1_Layers/LineData/GZAP.npy')
# line2Path = os.path.join(cwd, 'tests/CCC_K10_FL1_s2_Layers/LineData/GZAP.npy') #Upper
# savePath = os.path.join(cwd, 'tests/CCC_K10_FL1_s2_Layers/LineData/C5GLL_GZAP_Avg.npy')
# getAvg(line1Path, line2Path, savePath)