import sys
import os
import itertools
from PyQt5 import QtCore, QtGui, QtWidgets
from psd_tools import PSDImage
from PIL import Image
from drawLine import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


Image.MAX_IMAGE_PIXELS = 200000000
IMAGE_HEIGHT = 1200
IMAGE_WIDTH = 1000
# imageNames = ['cfo','ap', 'ap_low','dapi', 'trap', 'ac', 'cal', 'am', 'sfo']

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class GraphicView(QtWidgets.QGraphicsView):
    rectChanged = QtCore.pyqtSignal(QtCore.QRect)

    def __init__(self, *args, **kwargs):
        QtWidgets.QGraphicsView.__init__(self, *args, **kwargs)
        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.setMouseTracking(True)
        self.origin = QtCore.QPoint()
        self.changeRubberBand = False
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.setSceneRect(QtCore.QRectF(0,0,IMAGE_WIDTH, IMAGE_HEIGHT))
        self.setScene(self.scene)
        self.selectedRegion = {'x':0,'y':0,'w':-1,'h':-1}
        self.graphicsPixmapItem = None
        self.minPixels = 0


    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rectChanged.emit(self.rubberBand.geometry())
        self.rubberBand.show()
        self.changeRubberBand = True
        QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.changeRubberBand:
            self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())
            self.rectChanged.emit(self.rubberBand.geometry())
        QtWidgets.QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.changeRubberBand = False
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)
        self.selectedRegion['x'] = self.rubberBand.geometry().x()
        self.selectedRegion['y'] = self.rubberBand.geometry().y()
        self.selectedRegion['w'] = self.rubberBand.geometry().width()
        self.selectedRegion['h'] = self.rubberBand.geometry().height()


        # self.scene.addRect(self.selectedRegion['x'],self.selectedRegion['y'],self.selectedRegion['w'],self.selectedRegion['h'], pen = QtGui.QPen(QtCore.Qt.red, 4))
        # self.ROIList.append(ROI(self.selectedRegion['x'],self.selectedRegion['y'],self.selectedRegion['w'],self.selectedRegion['h']))
        # self.rubberBand.hide()
        # print('mouse released', self.selectedRegion)

class ImageLoader(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        mainLayout = QtWidgets.QGridLayout(self)

        # self.label = QtWidgets.QLabel()
        self.label = GraphicView()
        self.label.setAlignment(QtCore.Qt.AlignTop)
        self.label.setAlignment(QtCore.Qt.AlignLeft)
        mainLayout.addWidget(self.label, 1, 0, 1, 4)
        self.label.setMinimumSize(IMAGE_WIDTH, IMAGE_HEIGHT)
        self.label.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.label.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                                                        
        self.setWindowTitle('Load an Image')

        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.loadImageButton = QtWidgets.QPushButton('Load Image')
        mainLayout.addWidget(self.loadImageButton, 0, 0, 1, 1)

        # self.clearButton = QtWidgets.QPushButton('Clear Canvas')
        # mainLayout.addWidget(self.clearButton, 0, 1, 1, 1)

        # self.undoButton = QtWidgets.QPushButton('Undo')
        # mainLayout.addWidget(self.undoButton, 0, 2, 1, 1)

        # self.saveAllROIButton = QtWidgets.QPushButton('Save and Crop All')
        # mainLayout.addWidget(self.saveAllROIButton, 0, 3, 1, 1)

        self.prevImageButton = QtWidgets.QPushButton('<')
        mainLayout.addWidget(self.prevImageButton, 0, 1)
        self.nextImageButton = QtWidgets.QPushButton('>')
        mainLayout.addWidget(self.nextImageButton, 0, 2)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setMinimumSize(int(IMAGE_WIDTH/2), IMAGE_HEIGHT)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(3)

        controlLayout = QtWidgets.QGridLayout(self.frame)

        self.sectionButton = QtWidgets.QPushButton('Select Section', self.frame)
        controlLayout.addWidget(self.sectionButton, 1, 1, 1, 1)

        rgbFrame = QtWidgets.QFrame(self.frame)
        rgbLayout = QtWidgets.QGridLayout(rgbFrame)

        self.lowerRedLineEdit = QtWidgets.QLineEdit(self.frame)
        self.lowerRedLineEdit.setText('160')
        rgbLayout.addWidget(self.lowerRedLineEdit, 0, 0, 1, 1)

        self.upperRedLineEdit = QtWidgets.QLineEdit(self.frame)
        self.upperRedLineEdit.setText('182')
        rgbLayout.addWidget(self.upperRedLineEdit, 0, 1, 1, 1)

        controlLayout.addWidget(rgbFrame, 2, 0, 1, 1)

        self.rgbButton = QtWidgets.QPushButton('Filter RGB', self.frame)
        controlLayout.addWidget(self.rgbButton, 2, 1, 1, 1)

        maskFrame = QtWidgets.QFrame(self.frame)
        maskLayout = QtWidgets.QGridLayout(maskFrame)
        self.blurKSizeText = QtWidgets.QLabel(self.frame)
        self.blurKSizeText.setText('Gaussian Blur Kernel Size')
        maskLayout.addWidget(self.blurKSizeText, 0, 0)

        self.blurKSize = QtWidgets.QLineEdit(self.frame)
        self.blurKSize.setText('7')
        maskLayout.addWidget(self.blurKSize, 1, 0, 2, 1)

        self.blurIterText = QtWidgets.QLabel(self.frame)
        self.blurIterText.setText('Gaussian Blur Iterations')
        maskLayout.addWidget(self.blurIterText, 0, 1)

        self.blurIter = QtWidgets.QLineEdit(self.frame)
        self.blurIter.setText('9')
        maskLayout.addWidget(self.blurIter, 1, 1, 2, 1)

        self.sobelKSizeText = QtWidgets.QLabel(self.frame)
        self.sobelKSizeText.setText('Sobel Kernel Size')
        maskLayout.addWidget(self.sobelKSizeText, 0, 2)

        self.sobelKSize = QtWidgets.QLineEdit(self.frame)
        self.sobelKSize.setText('3')
        maskLayout.addWidget(self.sobelKSize, 1, 2, 2, 1)

        controlLayout.addWidget(maskFrame, 3, 0, 1, 1)

        self.maskButton = QtWidgets.QPushButton('Generate Mask', self.frame)
        controlLayout.addWidget(self.maskButton, 3, 1, 1, 1)

        self.thresholdLineEdit = QtWidgets.QLineEdit(self.frame)
        self.thresholdLineEdit.setText('30')
        controlLayout.addWidget(self.thresholdLineEdit, 4, 0, 1, 1)

        self.thresholdButton = QtWidgets.QPushButton('Threshold', self.frame)
        controlLayout.addWidget(self.thresholdButton, 4, 1, 1, 1)


        DEFrame = QtWidgets.QFrame(self.frame)
        DELayout = QtWidgets.QGridLayout(DEFrame)
        self.dilKernelText = QtWidgets.QLabel(self.frame)
        self.dilKernelText.setText('Dilation X')
        DELayout.addWidget(self.dilKernelText, 0, 0)
        self.eroKernelText = QtWidgets.QLabel(self.frame)
        self.eroKernelText.setText('Dilation Y')
        DELayout.addWidget(self.eroKernelText, 0, 1)
        self.dilIterText = QtWidgets.QLabel(self.frame)
        self.dilIterText.setText('Dilation Iterations')
        DELayout.addWidget(self.dilIterText, 0, 2)
        self.eroIterText = QtWidgets.QLabel(self.frame)
        self.eroIterText.setText('Erosion Iterations')
        DELayout.addWidget(self.eroIterText, 0, 3)
        
        self.dilKernelX = QtWidgets.QLineEdit(self.frame)
        self.dilKernelX.setText('5')
        DELayout.addWidget(self.dilKernelX, 1, 0, 2, 1)
        self.dilKernelY = QtWidgets.QLineEdit(self.frame)
        self.dilKernelY.setText('5')
        DELayout.addWidget(self.dilKernelY, 1, 1, 2, 1)
        self.dilIter = QtWidgets.QLineEdit(self.frame)
        self.dilIter.setText('3')
        DELayout.addWidget(self.dilIter, 1, 2, 2, 1)
        self.eroIter = QtWidgets.QLineEdit(self.frame)
        self.eroIter.setText('3')
        DELayout.addWidget(self.eroIter, 1, 3, 2, 1)
        controlLayout.addWidget(DEFrame, 5, 0, 1, 1)

        self.morphButton = QtWidgets.QPushButton('Dilation/Erosion', self.frame)
        controlLayout.addWidget(self.morphButton, 5, 1, 1, 1)

        self.contourCombo = QtWidgets.QComboBox(self.frame)
        self.contourCombo.addItems(['Largest', 'Second Largest'])
        controlLayout.addWidget(self.contourCombo, 6, 0, 1, 1)

        self.contourButton = QtWidgets.QPushButton('Countour', self.frame)
        controlLayout.addWidget(self.contourButton, 6, 1, 1, 1)

        self.gaussianLineEdit = QtWidgets.QLineEdit(self.frame)
        self.gaussianLineEdit.setText('30')
        controlLayout.addWidget(self.gaussianLineEdit, 7, 0, 1, 1)

        self.gaussianButton = QtWidgets.QPushButton('Gaussian', self.frame)
        controlLayout.addWidget(self.gaussianButton, 7, 1, 1, 1)

        self.drawLineCombo = QtWidgets.QComboBox(self.frame)
        self.drawLineCombo.addItems(['Up', 'Down'])
        controlLayout.addWidget(self.drawLineCombo, 8, 0, 1, 1)

        self.drawLineButton = QtWidgets.QPushButton('Draw Line', self.frame)
        controlLayout.addWidget(self.drawLineButton, 8, 1, 1, 1)


        lineInfoFrame = QtWidgets.QFrame(self.frame)
        lineInfoLayout = QtWidgets.QGridLayout(lineInfoFrame)

        self.lineColorCombo = QtWidgets.QComboBox(self.frame)
        self.lineColorCombo.addItems(['Blue', 'Green', 'Red'])
        lineInfoLayout.addWidget(self.lineColorCombo, 0, 0, 1, 1)

        self.nameLineEdit = QtWidgets.QLineEdit(self.frame)
        self.nameLineEdit.setText('Name of Line')
        lineInfoLayout.addWidget(self.nameLineEdit, 0, 1, 1, 3)
        controlLayout.addWidget(lineInfoFrame, 9, 0, 1, 1)


        self.saveLineButton = QtWidgets.QPushButton('Save Line', self.frame)
        controlLayout.addWidget(self.saveLineButton, 9, 1, 1, 1)

        mainLayout.addWidget(self.frame, 1, 4, 1, 1)


        self.figure = Figure()
        self.canvas = MplCanvas(self)

        controlLayout.addWidget(self.canvas, 0, 0, 1, 2)



        self.loadImageButton.clicked.connect(self.loadImage)
        self.prevImageButton.clicked.connect(self.prevImage)
        self.nextImageButton.clicked.connect(self.nextImage)
        self.rgbButton.clicked.connect(self.filterRGB)
        self.sectionButton.clicked.connect(self.selectSection)
        self.maskButton.clicked.connect(self.generateMask)
        self.thresholdButton.clicked.connect(self.threshold)
        self.morphButton.clicked.connect(self.morph)
        self.contourButton.clicked.connect(self.contour)
        self.gaussianButton.clicked.connect(self.gaussian)
        self.drawLineButton.clicked.connect(self.drawLine)
        self.saveLineButton.clicked.connect(self.saveLine)
        

        self.filename = ''
        self.baseName = ''
        self.dirname = ''
        self.dirIterator = None
        self.fileList = []
        self.pixmap = None

        self.image = None


    def loadImage(self):
        self.clearScene()
        self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select Image', '', 'Image Files (*.psd)')
        self.baseName = os.path.basename(self.filename)[:-4]
        self.dirname = os.path.dirname(self.filename) 
        layersDir = os.path.join(self.dirname, self.baseName + '_Layers')
        # otherDir = os.path.join(layersDir, 'OtherImages')
        lineDataDir = os.path.join(layersDir, 'LineData')
        lineImageDir = os.path.join(layersDir, 'LineImages')
        self.dirname = layersDir

        if not os.path.exists(layersDir) and layersDir != '_Layers':
            os.mkdir(layersDir)
            # if not os.path.exists(otherDir):
            #     os.mkdir(otherDir)
            if not os.path.exists(lineDataDir):
                os.mkdir(lineDataDir)
            if not os.path.exists(lineImageDir):
                os.mkdir(lineImageDir)

            psd = PSDImage.open(self.filename)
            # psd.composite().convert('RGB').save(os.path.join(layersDir, newFilename), format = 'JPEG', dpi = (300,300))
            for layer in psd:
                # print(layer.name)
                # if layer.name in imageNames:
                layer_image = layer.composite()
                layer_image = layer_image.convert('RGB')
                layer_image.save(os.path.join(layersDir, self.baseName + '_%s.jpg' % layer.name), format = 'JPEG', dpi = (300,300))

                # else:
                #     layer_image = layer.composite()
                #     layer_image = layer_image.convert('RGB')
                #     layer_image.save(os.path.join(otherDir, self.baseName + '_%s.jpg' % layer.name), format = 'JPEG', dpi = (300,300))

        self.fileList = [os.path.join(layersDir, f) for f in os.listdir(layersDir) if f.endswith('.jpg')]

        self.fileList.sort()
        self.dirIterator = iter(self.fileList)
        self.filename = next(self.dirIterator)

        # print(self.fileList)
        if self.filename:
            self.setWindowTitle(os.path.basename(self.filename)[:-4])
            self.pixmap = QtGui.QPixmap(self.filename).scaled(self.label.size(), QtCore.Qt.KeepAspectRatio)
            if self.pixmap.isNull():
                return
            self.label.graphicsPixmapItem = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(self.pixmap))
            self.label.scene.addItem(self.label.graphicsPixmapItem)

            self.image = LineImage(self.filename)

    def nextImage(self):
        if self.fileList:
            try:
                self.filename = next(self.dirIterator)
                self.setWindowTitle(os.path.basename(self.filename)[:-4])
                self.pixmap = QtGui.QPixmap(self.filename).scaled(self.label.size(), 
                    QtCore.Qt.KeepAspectRatio)
                if self.pixmap.isNull():
                    self.fileList.remove(self.filename)
                    self.nextImage()
                else:
                    self.clearScene()

                self.image = LineImage(self.filename)
            except:
                # the iterator has finished, restart it
                self.dirIterator = iter(self.fileList)
                self.nextImage()
        else:
            # no file list found, load an image
            self.loadImage()


    def prevImage(self):
        if self.fileList:
            for _ in itertools.repeat(None, len(self.fileList) - 1):
                try:
                    self.filename = next(self.dirIterator)
                except:
                    # the iterator has finished, restart it
                    self.dirIterator = iter(self.fileList)
                    self.nextImage()
            self.setWindowTitle(os.path.basename(self.filename)[:-4])
            self.pixmap = QtGui.QPixmap(self.filename).scaled(self.label.size(), 
                QtCore.Qt.KeepAspectRatio)

            self.image = LineImage(self.filename)
            self.clearScene()
        else:
            # no file list found, load an image
            self.loadImage()

    def clearScene(self):
        self.label.scene.clear()
        self.label.graphicsPixmapItem = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(self.pixmap))
        self.label.scene.addItem(self.label.graphicsPixmapItem)
        # print(self.label.ROIList)
    
    def updateVisual(self):
        self.canvas.axes.cla()
        self.canvas.axes.imshow(self.image.tempImg, 'gray')
        self.canvas.draw()


    def selectSection(self):
        im = Image.open(self.filename)
        width, _ = im.size
        ratio = width / self.pixmap.width()
        im.close()
        self.image.setSection(int(self.label.selectedRegion['y'] * ratio),
                              int((self.label.selectedRegion['h'] + self.label.selectedRegion['y']) * ratio),
                              int(self.label.selectedRegion['x'] * ratio),
                              int((self.label.selectedRegion['w'] + self.label.selectedRegion['x']) * ratio))
        # print(int(self.label.selectedRegion['y'] * ratio),
        #       int((self.label.selectedRegion['h'] + self.label.selectedRegion['y']) * ratio),
        #       int(self.label.selectedRegion['x'] * ratio),
        #       int((self.label.selectedRegion['w'] + self.label.selectedRegion['x']) * ratio))
        try:
            self.canvas.axes.cla()
            self.canvas.draw()
        except:
            pass
        self.updateVisual()

    def filterRGB(self):
        self.image.filterRGB(int(self.lowerRedLineEdit.text()), int(self.upperRedLineEdit.text()))
        self.updateVisual()

    def generateMask(self):
        self.image.generateMask(int(self.blurKSize.text()), int(self.blurIter.text()), int(self.sobelKSize.text()))
        self.updateVisual()

    def threshold(self):
        self.image.threshold(int(self.thresholdLineEdit.text()))
        self.updateVisual()

    def morph(self):
        self.image.morph(int(self.dilKernelX.text()),int(self.dilKernelY.text()),int(self.dilIter.text()),int(self.eroIter.text()))
        self.updateVisual()
    
    def contour(self):
        self.image.contour(self.contourCombo.currentIndex())
        self.updateVisual()
    
    def gaussian(self):
        self.image.gaussian(int(self.gaussianLineEdit.text()))
        self.updateVisual()
    
    def drawLine(self):
        # print(self.drawLineCombo.currentIndex())
        self.image.getLine(self.drawLineCombo.currentIndex())
        try:
            self.canvas.axes.cla()
            self.canvas.axes.clf()
        except:
            pass
        overlapped_img = np.zeros(self.image.img.shape)
        overlapped_img[self.image.lineInfo.upperBound:self.image.lineInfo.lowerBound, 
                       self.image.lineInfo.leftBound:self.image.lineInfo.rightBound, 1] = self.image.lineInfo.line*255

        self.canvas.axes.imshow(self.image.img, alpha=0.7)
        self.canvas.axes.imshow(overlapped_img, alpha=0.7)
        self.canvas.draw()

    def saveLine(self):
        overlapped_img = np.zeros(self.image.img.shape)
        # print(overlapped_img.shape)
        overlapped_img = np.dstack((overlapped_img, np.zeros((self.image.img.shape[0], self.image.img.shape[1]))))
        # print(overlapped_img.shape)
        overlapped_img[self.image.lineInfo.upperBound:self.image.lineInfo.lowerBound, 
                       self.image.lineInfo.leftBound:self.image.lineInfo.rightBound, self.lineColorCombo.currentIndex()] = self.image.lineInfo.line*255
        overlapped_img[self.image.lineInfo.upperBound:self.image.lineInfo.lowerBound, 
                       self.image.lineInfo.leftBound:self.image.lineInfo.rightBound, 3] = self.image.lineInfo.line*255
        cv2.imwrite(os.path.join(self.dirname, os.path.join('LineImages', self.nameLineEdit.text() + '.png')), overlapped_img)

        self.image.lineInfo.name = self.nameLineEdit.text()
        relativeLine = np.zeros((self.image.img.shape[0], self.image.img.shape[1]))
        relativeLine[self.image.lineInfo.upperBound:self.image.lineInfo.lowerBound, 
                     self.image.lineInfo.leftBound:self.image.lineInfo.rightBound] = self.image.lineInfo.line
        
        np.save(os.path.join(self.dirname, os.path.join('LineData', self.nameLineEdit.text() + '.npy')), relativeLine)




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    imageLoader = ImageLoader()
    imageLoader.show()
    sys.exit(app.exec_())