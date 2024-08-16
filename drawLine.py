import cv2
import numpy as np
import matplotlib.pyplot as plt
import warnings
from scipy.ndimage import gaussian_filter

warnings.filterwarnings('ignore')


class Line():
    def __init__(self):
        self.name = ''# name of line
        self.direction = 0 # 0 = upper line, 1 = lower line
        self.upperBound, self.lowerBound, self.leftBound, self.rightBound = 0,0,0,0 
        self.line = None # npy ndarray line
        # self.sigma = 0
        # self.dilKernel = 0
        # self.eroKernel = 0
        # self.dilIter = 0
        # self.eroIter = 0

class LineImage:
    def __init__(self, path2img):
        self.img = np.array(plt.imread(path2img))
        self.overlapped_img = np.zeros(self.img.shape)
        
        self.grayImg = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
        
        self.tempImg = self.grayImg
        self.img_section = None
        self.lines = []

        # current line
        self.lineInfo = Line()

    def filterRGB(self):
        # print('rgb')
        lower_red = np.array([160,0,0])
        upper_red = np.array([182,100,100])
        rgbImg = cv2.inRange(self.img, lower_red, upper_red)
        self.tempImg = rgbImg[self.lineInfo.upperBound:self.lineInfo.lowerBound, self.lineInfo.leftBound:self.lineInfo.rightBound]
        # plt.imshow(self.grayImg)
        # plt.show()


       

    def setSection(self, upperBound, lowerBound, leftBound, rightBound):
        self.lineInfo = Line()
        self.lineInfo.upperBound = upperBound
        self.lineInfo.lowerBound = lowerBound
        self.lineInfo.leftBound = leftBound
        self.lineInfo.rightBound = rightBound
        self.img_section = self.grayImg[self.lineInfo.upperBound:self.lineInfo.lowerBound, self.lineInfo.leftBound:self.lineInfo.rightBound]
        self.tempImg = self.img_section
    
    def generateMask(self, blurKSize, blurIter, sobelKSize):
        # Generate Mask
        blurred = cv2.GaussianBlur(self.tempImg, (blurKSize,blurKSize), blurIter)

        # Apply Sobel operator
        sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=sobelKSize)
        sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=sobelKSize)

        # Compute the magnitude of the gradient
        magnitude = cv2.magnitude(sobelx, sobely)

        # Convert the magnitude to 8-bit image
        magnitude = cv2.convertScaleAbs(magnitude)
        self.tempImg = magnitude

    def threshold(self, threshold):
        edges = cv2.threshold(self.tempImg, threshold, 255, cv2.THRESH_BINARY)[1]

        self.tempImg = edges

    def morph(self, dilKernelX, dilKernelY, dilIter, eroIter):
        # kernel1 = np.ones((dilKernelY,dilKernelX), np.uint8)
        # kernel1[0, 0] = 0
        # kernel1[dilKernelY - 1, 0] = 0
        # kernel1[0, dilKernelX - 1] = 0
        # kernel1[dilKernelY - 1, dilKernelX - 1] = 0


        # kernel1 = np.zeros((dilKernelY,dilKernelX), np.uint8)
        # kernel1[int(dilKernelY/2), :] = 1
        # kernel1[:, int(dilKernelX/2)] = 1
        try:
            kernel1 = np.zeros((dilKernelY,dilKernelX), np.uint8)
            kernel1[int(dilKernelY/2)-1:int((dilKernelY+1)/2)+1, :] = 1
            kernel1[:, int(dilKernelX/2)-1:int((dilKernelX+1)/2)+1] = 1

            kernel2 = np.ones((2,2), np.uint8)
            dilated_image = cv2.dilate(self.tempImg, kernel1, iterations=dilIter)
            closed_img = cv2.erode(dilated_image, kernel2, iterations=eroIter)

            # Close the object
            idx_img=sorted(np.where(closed_img==255)[1])
            left_idx = idx_img[0]
            right_idx = idx_img[-1]
            closed_img[0, left_idx:right_idx] = 255

            self.tempImg = closed_img
        except:
            pass

    def contour(self, i):
        contours, _ = cv2.findContours(self.tempImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Select the largest contour
        largest_contour = sorted(contours, key=cv2.contourArea, reverse=True)[i]

        # Create a mask for the largest contour
        largest_contour_mask = np.zeros_like(self.tempImg)
        cv2.drawContours(largest_contour_mask, [largest_contour], -1, 255, -1)
        self.tempImg = largest_contour_mask

    def gaussian(self, sigma):
        # print(self.tempImg.shape)
        # self.lineInfo.sigma = sigma
        # Apply a gaussian filter
        xscipy=gaussian_filter(self.tempImg, sigma=sigma, mode="wrap")
        # plt.figure()
        # plt.imshow(xscipy)
        # plt.title('gaussian1')
        # plt.show()
        thres_xscipy = np.where(xscipy>255*0.5, 255, 0).astype(np.uint8)
        self.tempImg = thres_xscipy
        # print(self.tempImg.shape)

    def getLine(self, dir):
        self.lineInfo.direction = dir
        roi_idx_x, roi_idx_y = np.where(self.tempImg==255)
        unique_y = np.unique(roi_idx_y)
        points_list = []
        for y in unique_y:
            x_list = []
            overlapped_y_idx = np.where(np.array(roi_idx_y) ==y)[0]
            x_list = [roi_idx_x[i] for i in overlapped_y_idx]
            points_list.append([x_list, y])
        # print("possible pairs of x,y are gathered")

        dir_line_ = None
        if self.lineInfo.direction == 1:
            # print('bottom')
            bottom_line_idx = []
            for xy in points_list:
                pair = [max(xy[0]), xy[1]]
                bottom_line_idx.append(pair)

            bottom_line = np.zeros(self.tempImg.shape)
            for i, j in bottom_line_idx:
                bottom_line[i,j] = 1

            dir_line_ = cv2.dilate(bottom_line, kernel=np.ones((7,7), np.uint8))
        else:
            top_line_idx = []
            for xy in points_list:
                pair = [min(xy[0]), xy[1]]
                top_line_idx.append(pair)

            top_line = np.zeros(self.tempImg.shape)
            for i, j in top_line_idx:
                top_line[i,j] = 1

            dir_line_ = cv2.dilate(top_line, kernel=np.ones((7,7), np.uint8))

        # plt.figure()
        # plt.imshow(dir_line_, 'gray')
        # plt.title('line')
        # plt.show()
        self.tempImg = dir_line_

        self.lineInfo.line = dir_line_
        # self.lines.append(self.lineInfo)

    def showImage(self, title):
        plt.figure()
        plt.imshow(self.tempImg, 'gray')
        plt.title(title)
        plt.show()

    def showLines(self):
        for line in self.lines:
            # print(color, self.overlapped_img.shape)
            # print(line.shape)
            self.overlapped_img[line.upperBound:line.lowerBound, line.leftBound:line.rightBound, 1] += line.line*255
            # self.overlapped_img[self.upperBound:self.lowerBound,self.leftBound:self.rightBound,2] = np.zeros(self.img_section.shape) # Blue
            # self.overlapped_img[self.upperBound:self.lowerBound,self.leftBound:self.rightBound,1] = np.zeros(self.img_section.shape) # Green

        plt.imshow(self.img, alpha=0.7)
        plt.imshow(self.overlapped_img, alpha=0.7)
        plt.title('Detected Mineral lines')
        plt.show()
        # plt.savefig(path2save, dpi=1200)
        plt.close()