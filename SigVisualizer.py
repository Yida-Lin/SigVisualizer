import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random
from math import *
import time
import threading
import numpy as np
from pylsl import StreamInlet, resolve_stream
from Ui_SigVisualizer import Ui_MainWindow


class dataThread(QThread):
    update = pyqtSignal(QRect)
    x = 0
    y = x + 300
    rect = QRect(0,0, 20, 800)
    counter = 0

    def __init__(self, parent, rect):
        super(dataThread, self).__init__(parent)
        self.rect = rect
 
    def updateRect(self, rect):
        self.rect = rect

    def run(self):
        while True:
            self.update.emit(self.rect)
            if self.counter < 50:
                self.rect.translate(20, 0)
                self.counter += 1
            else:
                self.rect.translate(-1000, 0)
                self.counter = 0
            # self.x = (self.x + 200) % 800
            # self.y = self.x + 300
            # self.rect = QRect(self.x, self.x, self.y, self.y)
            print('Paint!!')
            time.sleep(0.001)

class SigVisualizer(QMainWindow):
    panelHidden = False
    resized = pyqtSignal()
    update = pyqtSignal()
    streams = []
    x = 0
    y = 0
    lines = np.empty((10,500), dtype=object)

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Real Time Signal Visualizer')        
        self.ui.treeWidget.setHeaderLabel('Streams')

        self.ui.toggleButton.setIcon(QIcon("icons/baseline-chevron_left-24px.svg"))
        self.ui.toggleButton.setIconSize(QSize(30, 30));

        self.bluePen = QPen(Qt.blue)

        self.ui.updateButton.clicked.connect(self.updateStreams)
        self.ui.toggleButton.clicked.connect(self.togglePanel)
        self.resized.connect(self.ui.widget.paint)
 
        self.dataTr = dataThread(self, QRect(0, 0, 20, 800))
        self.dataTr.update.connect(self.updateRectRegion)
        self.dataTr.start()

    def updateRectRegion(self, rect):
        self.ui.widget.update(rect)

    # def resizeRect(self, rect):
    #     self.ui.widget.update(rect)

    def resizeEvent(self, event):
        self.resized.emit()
        return super(SigVisualizer, self).resizeEvent(event)

    def paint(self, num = 0):
        if self.streams:
            channelCount = self.streams[0].channel_count()
            channelHeight = self.ui.widget.height() / channelCount

            # for k in range(channelCount):
            #     text = self.scene.addText("Channel {}".format(k + 1))
            #     text.setDefaultTextColor(Qt.blue)
            #     text.setPos(20, channelHeight * k + channelHeight / 2);
        else:
            # channelCount = 8
            # channelHeight = self.ui.graphicsView.size().height() / channelCount * 0.7

            # newY = random.randint(1, 20)
            # # newX = (self.x + 1) % self.ui.graphicsView.width()
            # newX = (self.x + 1) % 500
            # if newX != 0:
            #     for k in range(channelCount):
            #         if self.lines[k, newX]:
            #             self.scene.removeItem(self.lines[k, newX])
                    
            #         self.lines[k, newX] = self.scene.addLine(QLineF(self.x * 5, 
            #         self.y + k * channelHeight, newX * 5, newY + k * channelHeight), self.bluePen)
            #     else:
            #         print('here')
            # self.x = newX
            # self.y = newY

            # text = self.scene.addText("Channel {}".format(1))
            # text.setDefaultTextColor(Qt.blue)
            # text.setPos(random.randint(1, 1500), 
            # random.randint(1, 800));
            print('Thread 2')

    def updateStreams(self):
        # first resolve an EEG stream on the lab network
        print("looking for an EEG stream...")
        # self.streams = resolve_stream('name', 'ActiChamp-0')

        # # create a new inlet to read from the stream
        # self.inlet = StreamInlet(self.streams[0])

        # streamName = self.streams[0].name()
        # item = QTreeWidgetItem(self.ui.treeWidget)
        # item.setText(0, streamName)

        # for k in range(self.streams[0].channel_count()):
        #     channelItem = QTreeWidgetItem(item)
        #     channelItem.setText(0, 'Channel {}'.format(k+1))
        #     channelItem.setCheckState(0, Qt.Checked)

        # self.ui.treeWidget.addTopLevelItem(item)
        # self.ui.treeWidget.expandAll()
        
    def togglePanel(self):
        if self.panelHidden:
            self.panelHidden = False
            self.ui.treeWidget.show()
            self.ui.updateButton.show()
            self.ui.toggleButton.setIcon(QIcon("icons/baseline-chevron_left-24px.svg"))
            self.ui.toggleButton.setIconSize(QSize(30, 30));
        else:
            self.panelHidden = True
            self.ui.treeWidget.hide()
            self.ui.updateButton.hide()
            self.ui.toggleButton.setIcon(QIcon("icons/baseline-chevron_right-24px.svg"))
            self.ui.toggleButton.setIconSize(QSize(30, 30));


    # def __init__(self):
    #     super().__init__()
    #     self.title = 'PySigVisualizer'
    #     self.left = 10
    #     self.top = 20
    #     self.width = 1800
    #     self.height = 1000
    #     self.initUI()

    # def initUI(self):
    #     self.setWindowTitle(self.title)
    #     self.setGeometry(self.left, self.top, self.width, self.height)

    #     # Set window background color
    #     self.setAutoFillBackground(True)
    #     p = self.palette()
    #     p.setColor(self.backgroundRole(), Qt.white)
    #     self.setPalette(p)

    #     # Add paint widget and paint
    #     self.m = PaintWidget(self)
    #     self.m.move(0,0)
    #     self.m.resize(self.width,self.height)

    #     self.showMaximized()


# class PaintWidget(QWidget):
#     xMargin = 100
#     yMargin = 50
#     idx = 0
#     chunkSize = 100

#     # first resolve an EEG stream on the lab network
#     print("looking for an EEG stream...")
#     streams = resolve_stream('name', 'ActiChamp-0')
#     # streams = resolve_stream('name', 'BioSemi')

#     # create a new inlet to read from the stream
#     inlet = StreamInlet(streams[0])
#     samplingRate = int(streams[0].nominal_srate())
#     channelCount = int(streams[0].channel_count())
#     samplesPerScreen = 500
#     timeStampsBuffer = np.zeros(shape=(channelCount, samplesPerScreen))
#     dataBuffer = np.zeros(shape=(channelCount, samplesPerScreen))
#     trend = [0 for x in range(channelCount)]
#     yRange = [0 for x in range(channelCount)]
#     yScaling = [0 for x in range(channelCount)]
#     xScaling = 1600 // samplesPerScreen

#     def paintEvent(self, event):
#         qp = QPainter(self)
#         qp.setPen(Qt.blue)
#         channelHeight = (self.size().height() - 2 * self.yMargin) / self.channelCount
#         self.yOffset = self.size().height() / self.channelCount / 2
#         self.signalPanelWidth = self.size().width() - 2 * self.xMargin
#         self.signalPanelHeight = self.size().height()

#         # get a new sample (you can also omit the timestamp part if you're not
#         # interested in it)
#         chunk, timestamps = self.inlet.pull_chunk(max_samples=self.chunkSize)
#         if timestamps:
#             effectiveFS = float(len(timestamps) - 1) / (timestamps[-1] - timestamps[0])
#             qp.drawText(100, self.channelCount * channelHeight + self.yOffset + self.yMargin, 
#             'Effective sampling rate: {0:.5f}Hz'.format(round(effectiveFS, 5)))

#             if self.idx == 0:
#                 for m in range(self.channelCount):
#                     data_chunk = [row[m] for row in chunk]
#                     self.trend[m] =  np.mean(data_chunk)
#                     self.yRange[m] = np.max(data_chunk) - np.min(data_chunk)
#                     self.yScaling[m] = channelHeight * 1.2 / self.yRange[m]

#             for c in range(len(timestamps)):
#                 for m in range(self.channelCount):
#                     self.dataBuffer[m, self.idx] = (chunk[c][m] - self.trend[m]) * self.yScaling[m]
                
#                 self.idx = (self.idx + 1) % self.samplesPerScreen

#         for m in range(self.channelCount):
#             qp.drawText(10, m * channelHeight + self.yOffset + self.yMargin, 'Channel {}'.format(m+1))

#             for k in range(self.dataBuffer.shape[1]-1):
#                 qp.drawLine(k * self.xScaling + self.xMargin, 
#                 (-1) * self.dataBuffer[m, k] + m * channelHeight + self.yOffset / 2 + self.yMargin, 
#                 (k+1)* self.xScaling + self.xMargin, 
#                 (-1) * self.dataBuffer[m, k+1] + m * channelHeight + self.yOffset / 2 + self.yMargin)

#         self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SigVisualizer()
    window.showMaximized()
    sys.exit(app.exec_())
