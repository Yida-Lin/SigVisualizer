import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random
from math import *
import time
import numpy as np
from pylsl import StreamInlet, resolve_stream
from Ui_SigVisualizer import Ui_MainWindow


class SigVisualizer(QMainWindow):
    panelHidden = False
    resized = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Real Time Signal Visualizer')        
        self.ui.treeWidget.setHeaderLabel('Streams')

        self.ui.toggleButton.setIcon(QIcon("icons/baseline-chevron_left-24px.svg"))
        self.ui.toggleButton.setIconSize(QSize(30, 30));

        self.ui.updateButton.clicked.connect(self.updateStreams)
        self.ui.toggleButton.clicked.connect(self.togglePanel)
        self.resized.connect(self.paint)
        self.paint()

    def resizeEvent(self, event):
        self.resized.emit()
        return super(SigVisualizer, self).resizeEvent(event)

    def paint(self):
        self.scene = QGraphicsScene(self)
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        bluePen = QPen(Qt.blue)

        channelCount = 10
        channelHeight = self.ui.graphicsView.size().width() / channelCount

        for k in range(channelCount):
            text = self.scene.addText("Channel {}".format(k + 1))
            text.setDefaultTextColor(Qt.blue)
            text.setPos(20, channelHeight * k + channelHeight / 2);




        # x1 = 50
        # y1 = 1
        # x2 = 51
        # y2 = 1


        # self.scene.addLine(QLineF(0, 200, self.ui.graphicsView.width(), 400))
        # scaling = 20
        # for k in range(self.ui.graphicsView.width() - 200):
        #     for m in range(10):
        #         # self.scene.addText('Channel {}'.format(m))
        #         self.scene.addLine(QLineF(x1, random.randint(m * scaling, m * scaling + 50), x2, random.randint(m * scaling, m * scaling + 50)), bluePen)
        #     x1 = x2
        #     x2 += 1


        # for k in range(10):
        #     x1 += k * 10
        #     y1 += k * 10
        #     x2 -= k * 10
        #     y2 -+ k * 10
        #     self.scene.addLine(QLineF(x1, y1, x2, y2))


    def updateStreams(self):
        # first resolve an EEG stream on the lab network
        print("looking for an EEG stream...")
        streams = resolve_stream('name', 'ActiChamp-0')

        # create a new inlet to read from the stream
        inlet = StreamInlet(streams[0])

        streamName = streams[0].name()
        item = QTreeWidgetItem(self.ui.treeWidget)
        item.setText(0, streamName)

        for k in range(streams[0].channel_count()):
            channelItem = QTreeWidgetItem(item)
            channelItem.setText(0, 'Channel {}'.format(k+1))
            channelItem.setCheckState(0, Qt.Checked)

        self.ui.treeWidget.addTopLevelItem(item)
        self.ui.treeWidget.expandAll()

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
