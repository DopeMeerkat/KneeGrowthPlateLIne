import sys
import os
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from psd_tools import PSDImage
from PIL import Image, ImageDraw



Image.MAX_IMAGE_PIXELS = 200000000
IMAGE_HEIGHT = 1024 
IMAGE_WIDTH = 1024  
JSON_FILENAME = 'RoI_coordinates.json'
MIN_PIXELS = 128

REFERENCE_SCALE = 1

imageNames = ['cfo','ap','dapi', 'trap', 'ac', 'cal', 'am']

class Line():
    def __init__(self, name, line):
        self.name = name # name of stain
        self.line = line # npy ndarray line


class ROI():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


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
        self.ROIList = []
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


        self.scene.addRect(self.selectedRegion['x'],self.selectedRegion['y'],self.selectedRegion['w'],self.selectedRegion['h'], pen = QtGui.QPen(QtCore.Qt.red, 4))
        self.ROIList.append(ROI(self.selectedRegion['x'],self.selectedRegion['y'],self.selectedRegion['w'],self.selectedRegion['h']))
        self.rubberBand.hide()
        # print('mouse released', self.selectedRegion)

class ImageLoader(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QGridLayout(self)

        # self.label = QtWidgets.QLabel()
        self.label = GraphicView()
        self.label.setAlignment(QtCore.Qt.AlignTop)
        self.label.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.label, 1, 0, 1, 4)
        self.label.setMinimumSize(IMAGE_WIDTH, IMAGE_HEIGHT)
        self.label.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.label.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.label.ensureVisible(0,0,IMAGE_WIDTH, IMAGE_HEIGHT, xMargin = 0, yMargin = 0)
                                                        
        self.setWindowTitle('RoI selection')

        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.loadImageButton = QtWidgets.QPushButton('Load Image')
        layout.addWidget(self.loadImageButton, 0, 0, 1, 1)

        self.clearButton = QtWidgets.QPushButton('Clear Canvas')
        layout.addWidget(self.clearButton, 0, 1, 1, 1)

        self.undoButton = QtWidgets.QPushButton('Undo')
        layout.addWidget(self.undoButton, 0, 2, 1, 1)

        self.saveAllROIButton = QtWidgets.QPushButton('Save and Crop All')
        layout.addWidget(self.saveAllROIButton, 0, 3, 1, 1)

        # self.nextImageButton = QtWidgets.QPushButton('>')
        # layout.addWidget(self.nextImageButton, 1, 3)
        # self.nextImageButton.setMinimumSize(20,IMAGE_HEIGHT)


        self.loadImageButton.clicked.connect(self.loadImage)
        # self.nextImageButton.clicked.connect(self.nextImage)
        self.clearButton.clicked.connect(self.clearScene)
        self.undoButton.clicked.connect(self.undo)
        self.saveAllROIButton.clicked.connect(self.saveROI)
        

        self.filename = ''
        self.psdName = ''
        self.baseName = ''
        self.dirname = ''
        self.dirIterator = None
        self.fileList = []
        self.pixmap = QtGui.QPixmap()
    
    def loadJSON(self, json_path):
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
            # print(data)
            self.label.ROIList = []
            imagePath = os.path.join(os.path.dirname(json_path), self.baseName + '_A.jpg')
            # print(imagePath)
            im = Image.open(imagePath)

            width, _ = im.size
            ratio = self.pixmap.width() / width
            for roi in data['annotations']:
                # print(roi)
                self.label.ROIList.append(ROI(int(roi['x_left'] * ratio), 
                                              int(roi['y_up'] * ratio), 
                                              int((roi['x_right'] - roi['x_left']) * ratio), 
                                              int((roi['y_low'] - roi['y_up'])* ratio)))
            # print(self.label.ROIList)

            # 
            if self.label.ROIList: #if not empty
                for roi in self.label.ROIList:
                    self.label.scene.addRect(roi.x, roi.y, roi.w, roi.h, pen = QtGui.QPen(QtCore.Qt.red, 4))


    def loadImage(self):
        self.clearScene()
        # self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(
        #     self, 'Select Image', '', 'Image Files (*.png *.jpg *.jpeg *.psd)')
        self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select Image', '', 'Image Files (*.psd)')
        self.psdName = self.filename
        self.baseName = os.path.basename(self.filename)[:-4]
        self.dirname = os.path.dirname(self.filename) 
        layersDir = os.path.join(self.dirname, self.baseName + '_Layers')
        otherDir = os.path.join(layersDir, 'Other Images')

        # newFilename =  self.baseName + '_A.jpg'
        
        if not os.path.exists(layersDir):
            os.mkdir(layersDir)
            if not os.path.exists(otherDir):
                os.mkdir(otherDir)
            psd = PSDImage.open(self.filename)
            # psd.composite().convert('RGB').save(os.path.join(layersDir, newFilename), format = 'JPEG', dpi = (300,300))
            for layer in psd:
                # print(layer.name)
                if layer.name in imageNames:
                    layer_image = layer.composite()
                    layer_image = layer_image.convert('RGB')
                    layer_image.save(os.path.join(layersDir, self.baseName + '_%s.jpg' % layer.name), format = 'JPEG', dpi = (300,300))
                else:
                    layer_image = layer.composite()
                    layer_image = layer_image.convert('RGB')
                    layer_image.save(os.path.join(otherDir, self.baseName + '_%s.jpg' % layer.name), format = 'JPEG', dpi = (300,300))

        # self.filename = os.path.join(layersDir, newFilename)
        # if self.filename:
        #     self.setWindowTitle(self.filename)
        #     self.pixmap = QtGui.QPixmap(self.filename).scaled(self.label.size(), QtCore.Qt.KeepAspectRatio)
        #     if self.pixmap.isNull():
        #         return
        #     # self.label.setPixmap(self.pixmap)
        #     im = Image.open(self.filename)
        #     width, _ = im.size
        #     ratio = self.pixmap.width() / width
        #     # print(ratio)
        #     self.label.minPixels = MIN_PIXELS * ratio

        #     self.label.graphicsPixmapItem = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(self.pixmap))
        #     self.label.scene.addItem(self.label.graphicsPixmapItem)


        #     dirpath = os.path.dirname(self.filename)
        #     self.fileList = []
        #     for f in os.listdir(dirpath):
        #         fpath = os.path.join(dirpath, f)
        #         if os.path.isfile(fpath) and f.endswith(('.png', '.jpg', '.jpeg')):
        #             self.fileList.append(fpath)



        #     self.fileList.sort()
        #     self.dirIterator = iter(self.fileList)
          
        #     while True:
        #         # cycle through the iterator until the current file is found
        #         if next(self.dirIterator) == self.filename:
        #             break


    def clearScene(self):
        # print(self.label.ROIList)
        self.label.scene.clear()
        self.label.ROIList = []
        self.label.graphicsPixmapItem = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(self.pixmap))
        self.label.scene.addItem(self.label.graphicsPixmapItem)
        # print(self.label.ROIList)

    def undo(self):
        # print(self.label.ROIList)
        self.label.scene.clear()
        self.label.graphicsPixmapItem = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(self.pixmap))
        self.label.scene.addItem(self.label.graphicsPixmapItem)
        if self.label.ROIList: #if not empty
            self.label.ROIList.pop()
            # print(self.label.ROIList)
            for roi in self.label.ROIList:
                # print(roi.x, roi.y)
                self.label.scene.addRect(roi.x, roi.y, roi.w, roi.h, pen = QtGui.QPen(QtCore.Qt.red, 4))


    def save_region_and_update_json(self, x_left, y_up, width, height, json_path):
        # Check if JSON file exists
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
        else:
            data = {'annotations': []}

        # Get the ID
        if data['annotations']:
            id = max([item['id'] for item in data['annotations']]) + 1
        else:
            id = 1

        # # Save the selected region as an image file
        # region_image_path = f'patches/{id}.jpg'
        # cv2.imwrite(region_image_path, selected_region)

        # Create the new annotation
        new_annotation = {
            'id': id,
            'x_left': x_left,
            'x_right': x_left + width,
            'y_up': y_up,
            'y_low': y_up + height
        }

        data['annotations'].append(new_annotation)

        # Save the updated JSON file
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)

    def saveROI(self):
        # dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Directory', '.', QtWidgets.QFileDialog.ShowDirsOnly)
        dir = self.dirname    

        imagePath = os.path.join(dir, os.path.join(self.baseName + '_Layers',self.baseName + '_A.jpg'))
        refImage = Image.open(imagePath)
        # REFERENCE_SCALE = int(650/refImage.size[0]) 
        if REFERENCE_SCALE > 1:
            refImage = refImage.resize((refImage.size[0] * REFERENCE_SCALE, refImage.size[1] * REFERENCE_SCALE), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(refImage)

        width, _ = refImage.size
        ratio = width / self.pixmap.width()
        for i, roi in enumerate(self.label.ROIList):
            draw.rectangle([int(roi.x * ratio), int(roi.y * ratio), int((roi.w + roi.x) * ratio), int((roi.h + roi.y) * ratio)], outline="red", width=10)
            draw.rectangle([int(roi.x * ratio), int(roi.y * ratio), int((roi.x + 12) * ratio), int((roi.y + 12) * ratio)], fill="white", width=10)
            # font_path = os.path.join(cv2.__path__[0], 'qt','fonts','DejaVuSans.ttf')
            # font = ImageFont.truetype(font_path, size=5)
            # draw.text((int(roi.x * ratio) + 15, int(roi.y * ratio) + 15), str(i + 1), font=font, fill="red")
            draw.text((int(roi.x * ratio) + 15, int(roi.y * ratio) + 15), str(i + 1), fill="red")

        # refImage.show()
        refImage.save(os.path.join(dir, os.path.join(self.baseName + '_Layers', self.baseName + '__Reference.png')))

        # pic = self.pixmap
        # painter = QtGui.QPainter(pic)
        # self.label.scene.render(painter)
        # painter.setPen(QtCore.Qt.darkRed)
        # pic.save(os.path.join(dir, os.path.join(self.baseName + '_Layers', self.baseName + '__Reference.png')))


        if os.path.exists(os.path.join(dir, os.path.join(self.baseName + '_Layers', JSON_FILENAME))):
            os.remove(os.path.join(dir, os.path.join(self.baseName + '_Layers', JSON_FILENAME)))

        for i, roi in enumerate(self.label.ROIList):
            
            roiDir = os.path.join(dir, self.baseName + '_ROI' + str(i + 1))
            if not os.path.exists(roiDir):
                os.mkdir(roiDir)
                # print(roiDir)
                srcDir = os.path.dirname(self.filename)
                # print(srcDir)
                # psdImg = Image.open(self.psdName)
                # psdWidth, _ = psdImg.size
                # psdRatio = psdWidth / self.pixmap.width()
                
                for f in os.listdir(srcDir):
                    if f.endswith(('.jpg')):
                        imgName= os.path.join(srcDir, f)
                        im = Image.open(imgName)
                        width, _ = im.size
                        ratio = width / self.pixmap.width()
                        # print(ratio)
                        # print(roi.x, roi.y, roi.w, roi.h)
                        # print((int(roi.x * ratio), int(roi.y * ratio), int(roi.w * ratio), int(roi.h * ratio)))
                        ind = f.find('_')
                        roiFilename = f[:ind] + '_ROI' + str(i + 1) + f[ind:]
                        im1 = im.crop((int(roi.x * ratio), int(roi.y * ratio), int((roi.w + roi.x) * ratio), int((roi.h + roi.y) * ratio)))
                        im1.save(os.path.join(roiDir, roiFilename), format = 'JPEG', dpi = im1.info['dpi'])
                        # im2 = psdImg.crop((int(roi.x * psdRatio), int(roi.y * psdRatio), int((roi.w + roi.x) * psdRatio), int((roi.h + roi.y) * psdRatio)))
                        # im2.save(os.path.join(roiDir, self.baseName + '_psd.psd'), format = 'PSD')

            jsonPath = os.path.join(dir, os.path.join(self.baseName + '_Layers', JSON_FILENAME))
            # print(jsonPath)
            self.save_region_and_update_json(int(roi.x * ratio), int(roi.y * ratio), int(roi.w * ratio), int(roi.h  * ratio), jsonPath)

        

        



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    imageLoader = ImageLoader()
    imageLoader.show()
    sys.exit(app.exec_())