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
    updateRect = pyqtSignal(int)
    updateStreamNames = pyqtSignal(dict)
    sendSignalChunk = pyqtSignal(list)
    chunkSize = 20
    streams = []
    streamMetadata = {}
    chunkIdx = 0

    def __init__(self, parent):
        super(dataThread, self).__init__(parent)
        self.data = [[0 for i in range(self.chunkSize)] for j in range(10)]
        self.chunksPerScreen = round(500 / len(self.data[0]))
 
    def updateStreams(self):
        if not self.streams:
            self.streams = resolve_stream('name', 'ActiChamp-0')
            
            if self.streams:
                # create a new inlet to read from the stream
                self.inlet = StreamInlet(self.streams[0])

                self.streamMetadata["streamName"] = self.streams[0].name()
                self.streamMetadata["channelCount"] = self.streams[0].channel_count()
        
                self.updateStreamNames.emit(self.streamMetadata)

                # while True:
                #     chunk, timestamps = self.inlet.pull_chunk(max_samples=self.chunkSize)
                #     if timestamps:
                #         print('Debug')

    def run(self):
        while True:
            for k in range(len(self.data)):
                for m in range(len(self.data[0])):
                    self.data[k][m] = random.randint(1, 20)

            self.updateRect.emit(self.chunkIdx)
            self.sendSignalChunk.emit(self.data)

            if self.chunkIdx < self.chunksPerScreen:
                self.chunkIdx += 1
            else:
                self.chunkIdx = 0
            time.sleep(1/self.chunksPerScreen)

class PaintWidget(QWidget):
    idx = 0
    channelHeight = 0
    interval = 0

    def __init__(self, widget):
        super().__init__()
        pal = QPalette()
        pal.setColor(QPalette.Background, Qt.white)
        self.setAutoFillBackground(True);
        self.setPalette(pal)

        self.dataTr = dataThread(self)
        self.dataTr.updateRect.connect(self.updateRectRegion)
        self.dataTr.sendSignalChunk.connect(self.getDataChunk)
        self.dataTr.start()

        self.dataBuffer = [[0 for i in range(self.dataTr.chunkSize)] for j in range(10)]

    def updateRectRegion(self, chunkIdx):
        self.idx = chunkIdx
        self.update(self.idx * (self.width() / self.dataTr.chunksPerScreen), 
        0,
        self.width() / self.dataTr.chunksPerScreen,
        self.height())

    def getDataChunk(self, buffer):
        self.dataBuffer = buffer

    def paintEvent(self, event):
        self.channelHeight = self.height() / len(self.dataBuffer)

        painter = QPainter(self)
        painter.setPen(QPen(QColor(79, 106, 25), 1, Qt.SolidLine,
                            Qt.FlatCap, Qt.MiterJoin))

        self.interval = self.width() / self.dataTr.chunksPerScreen / len(self.dataBuffer[0])

        for k in range(len(self.dataBuffer)):
            for m in range(len(self.dataBuffer[0]) - 1):
                painter.drawLine(m * self.interval + self.idx * (self.width() / self.dataTr.chunksPerScreen), 
                self.dataTr.data[k][m] + (k + 0.5) * self.channelHeight,
                (m + 1) * self.interval + self.idx * (self.width() / self.dataTr.chunksPerScreen),
                self.dataTr.data[k][m+1] + (k + 0.5) * self.channelHeight)


        # qp = QPainter(self)
        # qbrush = QBrush(Qt.white)
        # qp.setBackground(qbrush)
        # qp.drawLine(100,100,500,500)

        # painter = QPainter(self.ui.widget)
        # painter.begin(self.ui.widget)
        # painter.setBrush(QColor(122, 163, 39))
        # painter.setRenderHint(QPainter.Antialiasing, True)
        # painter.setPen(QPen(Qt.black, 12, Qt.DashDotLine, Qt.RoundCap))
        # painter.setBrush(QBrush(Qt.green, Qt.SolidPattern))
        # painter.drawEllipse(100, 100, 500, 500)
        # painter.end()

        # path = QPainterPath()
        # path.addRect(20, 20, 60, 60)

        # path.moveTo(0, 0)
        # path.cubicTo(99, 0,  50, 50,  99, 99)
        # path.cubicTo(0, 99,  50, 50,  0, 0)


        # painter.drawPath(path)



        # painter = QPainter(self)


        # if self.counter == 1:
        #     painter.fillRect(0, 0, self.width(), self.height(), Qt.white)
        #     # self.update(0, 0, self.width(), self.height())
        # elif self.counter % 2:
        #     painter.fillRect(0, 0, 299, 299, Qt.blue) # Fill with blue color
        #     # self.update(0, 0, 199, 199)
        # else:
        #     painter.fillRect(0, 0, 199, 199, Qt.green) # Fill with green color
        #     # self.update(0, 0, 199, 199)

        # self.counter += 1
