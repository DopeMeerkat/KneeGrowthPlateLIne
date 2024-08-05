import cv2
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os
import tkinter as tk
from scipy.ndimage import gaussian_filter
from tkinter import filedialog
# from scipy.signal import find_peaks, peak_widths
DILATION_ITERATIONS = 3
EROSION_ITERATIONS = 3
THRESHOLD = 200
plotToggle = []
direction = 0
warnings.filterwarnings('ignore')
root = tk.Tk()
root.withdraw()
path2img = filedialog.askopenfilename(initialdir=os.getcwd(), title='')
path2save = os.path.basename(path2img)[:-4] + '_save.jpg'

# m = mineral(path2img)
# m.plot_img(path2save)

img = plt.imread(path2img)
# print(img.shape)
overlapped_img = np.zeros(img.shape)
img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
# print(img.shape)

# plt.imshow(img, 'gray')
# plt.show()

# Get intensity plot of the image for extracing RoI

imgArray = np.array(img)
print(imgArray.shape)

upper_bound = 3180
lower_bound = 5475
left_bound = 340
right_bound = 3860

# print('upper bound:', upper_bound, '\nlower bound:', lower_bound)
# print('left bound:', left_bound, '\nlower bound:', right_bound)



img_section = img[upper_bound:lower_bound, left_bound:right_bound]
print(img_section.shape)
plt.imshow(img_section, 'gray')
plt.show()
# Generate Mask
blurred = cv2.GaussianBlur(img_section, (7,7), 0)

# Apply Sobel operator
sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=5)
sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=5)

# Compute the magnitude of the gradient
magnitude = cv2.magnitude(sobelx, sobely)

# Convert the magnitude to 8-bit image
magnitude = cv2.convertScaleAbs(magnitude)

# Threshold the image to get edges
threshold = THRESHOLD  # You can adjust this threshold value
edges = cv2.threshold(magnitude, threshold, 255, cv2.THRESH_BINARY)[1]

kernel1 = np.ones((7,7), np.uint8)
kernel2 = np.ones((2,2), np.uint8)
dilated_image = cv2.dilate(edges, kernel1, iterations=DILATION_ITERATIONS)
closed_img = cv2.erode(dilated_image, kernel2, iterations=EROSION_ITERATIONS)

# Close the object
idx_img=sorted(np.where(closed_img==255)[1])
left_idx = idx_img[0]
right_idx = idx_img[-1]
closed_img[0, left_idx:right_idx] = 255

plt.figure()
plt.imshow(closed_img, 'gray')
plt.show()

# Find contours

def getBordered(image, width):
    bg = np.zeros(image.shape)
    contours, _ = cv2.findContours(image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    biggest = 0
    bigcontour = None
    for contour in contours:
        area = cv2.contourArea(contour) 
        if area > biggest:
            biggest = area
            bigcontour = contour
    return cv2.drawContours(bg, [bigcontour], 0, (255, 255, 255), width).astype(bool) 



contours, _ = cv2.findContours(closed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Select the largest contour
largest_contour = max(contours, key=cv2.contourArea)

# Create a mask for the largest contour
largest_contour_mask = np.zeros_like(closed_img)
cv2.drawContours(largest_contour_mask, [largest_contour], -1, 255, -1)


# Display the result
plt.figure()
plt.imshow(largest_contour_mask, 'gray')

edge = getBordered(largest_contour_mask, 3)
plt.figure()
plt.imshow(edge, 'gray')
plt.show()

# Apply a gaussian filter
xscipy=gaussian_filter(largest_contour_mask, sigma=70, mode="wrap")
thres_xscipy = np.where(xscipy>255*0.5, 255, 0)
plt.imshow(thres_xscipy, 'gray')
plt.show()

roi_idx_x, roi_idx_y = np.where(thres_xscipy==255)
unique_y = np.unique(roi_idx_y)
points_list = []
for y in unique_y:
    x_list = []
    overlapped_y_idx = np.where(np.array(roi_idx_y) ==y)[0]
    x_list = [roi_idx_x[i] for i in overlapped_y_idx]
    points_list.append([x_list, y])
# print("possible pairs of x,y are gathered")

dir_line_ = None
if direction == 1:
    bottom_line_idx = []
    for xy in points_list:
        pair = [max(xy[0]), xy[1]]
        bottom_line_idx.append(pair)

    bottom_line = np.zeros(thres_xscipy.shape)
    for i, j in bottom_line_idx:
        bottom_line[i,j] = 1

    dir_line_ = cv2.dilate(bottom_line, kernel=np.ones((7,7), np.uint8))
else:
    top_line_idx = []
    for xy in points_list:
        pair = [min(xy[0]), xy[1]]
        top_line_idx.append(pair)

    top_line = np.zeros(thres_xscipy.shape)
    for i, j in top_line_idx:
        top_line[i,j] = 1

    dir_line_ = cv2.dilate(top_line, kernel=np.ones((7,7), np.uint8))


plt.imshow(dir_line_, 'gray')
plt.title('Detected line')
plt.show()


overlapped_img[upper_bound:lower_bound,left_bound:right_bound,0] = dir_line_*255
overlapped_img[upper_bound:lower_bound,left_bound:right_bound,2] = np.zeros(img_section.shape) # Blue
overlapped_img[upper_bound:lower_bound,left_bound:right_bound,1] = np.zeros(img_section.shape) # Green

plt.imshow(img, 'gray', alpha=0.7)
plt.imshow(overlapped_img, alpha=0.7)
plt.title('Detected Mineral lines')

plt.savefig(path2save, dpi=1200)
plt.close()