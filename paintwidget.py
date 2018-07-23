import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random
from math import *
import time
import threading
import numpy as np
from pylsl import StreamInlet, resolve_stream, resolve_streams
from Ui_SigVisualizer import Ui_MainWindow

class dataThread(QThread):
    updateStreamNames = pyqtSignal(dict, int)
    sendSignalChunk = pyqtSignal(int, list)
    chunksPerScreen = 50
    streams = []
    streamMetadata = {}
    chunkIdx = 0

    def __init__(self, parent):
        super(dataThread, self).__init__(parent)
 
    def updateStreams(self):
        if not self.streams:
            self.streams = resolve_streams(wait_time=1.0)
            
            if self.streams:
                self.defaultIdx = -1

                for k in range(len(self.streams)):
                    self.streamMetadata[k] = {
                        "streamName": self.streams[k].name(),
                        "channelCount": self.streams[k].channel_count(),
                        "channelFormat": self.streams[k].channel_format(),
                        "nominalSrate":self.streams[k].nominal_srate()
                    }
                    
                    if self.streams[k].channel_format() != "String" and self.defaultIdx == -1:
                        self.defaultIdx = k

                self.nominal_srate = int(self.streams[self.defaultIdx].nominal_srate())
                self.downSampling = False if self.nominal_srate <= 1000 else True
                self.chunkSize = round(self.nominal_srate / self.chunksPerScreen)

                if self.downSampling:
                    self.downSamplingRatio = 10
                    self.downSamplingBuffer = [[0 for m in range(int(self.streams[self.defaultIdx].channel_count()))] 
                    for n in range(round(self.chunkSize/self.downSamplingRatio))]

                self.inlet = StreamInlet(self.streams[self.defaultIdx])
                self.updateStreamNames.emit(self.streamMetadata, self.defaultIdx)
                self.start()

    def run(self):
        if self.streams:
            while True:
                chunk, timestamps = self.inlet.pull_chunk(max_samples=self.chunkSize, timeout=1)
                if timestamps:

                    if self.downSampling:
                        for k in range(int(self.streams[self.defaultIdx].channel_count())):
                            for m in range(round(self.chunkSize/self.downSamplingRatio)):
                                if m != round(self.chunkSize/self.downSamplingRatio):
                                    endIdx = (m+1) * self.downSamplingRatio

                                    buf = [chunk[n][k] for n in range(m * self.downSamplingRatio, endIdx)]
                                else:
                                    buf = [chunk[n][k] for n in range(m * self.downSamplingRatio, len(chunk))]

                                self.downSamplingBuffer[m][k] = sum(buf) / len(buf)

                        self.sendSignalChunk.emit(self.chunkIdx, self.downSamplingBuffer)
                    else:
                        self.sendSignalChunk.emit(self.chunkIdx, chunk)

                    if self.chunkIdx < self.chunksPerScreen:
                        self.chunkIdx += 1
                    else:
                        self.chunkIdx = 0

class PaintWidget(QWidget):
    idx = 0
    channelHeight = 0
    interval = 0
    dataBuffer = []
    lastY = []
    scaling = []
    mean = []

    def __init__(self, widget):
        super().__init__()
        pal = QPalette()
        pal.setColor(QPalette.Background, Qt.white)
        self.setAutoFillBackground(True);
        self.setPalette(pal)

        self.dataTr = dataThread(self)
        self.dataTr.sendSignalChunk.connect(self.getDataChunk)


    def getDataChunk(self, chunkIdx, buffer):
        if not self.mean:
            self.mean= [0 for k in range(len(buffer[0]))]
            self.scaling = [0 for k in range(len(buffer[0]))]
        self.dataBuffer = buffer

        self.idx = chunkIdx
        self.update(self.idx * (self.width() / self.dataTr.chunksPerScreen) - self.interval, 
        0,
        self.width() / self.dataTr.chunksPerScreen,
        self.height())

    def paintEvent(self, event):
        if self.dataBuffer:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.blue))
            # painter.setPen(QPen(QColor(79, 106, 25), 1, Qt.SolidLine,
            #                     Qt.FlatCap, Qt.MiterJoin))

            self.channelHeight = self.height() / len(self.dataBuffer[0])
            self.interval = self.width() / self.dataTr.chunksPerScreen / len(self.dataBuffer)

            # ======================================================================================================
            # Calculate Trend and Scaling
            # ======================================================================================================
            if self.idx == 0 or not self.mean:
                for k in range(len(self.dataBuffer[0])):
                    column = [row[k] for row in self.dataBuffer]
                    self.mean[k] = sum(column) / len(column)

                    for m in range(len(column)):
                        column[m] -= self.mean[k]

                    self.scaling[k] = self.channelHeight * 0.7 / (max(column) - min(column) + 0.0000000000001)

            # ======================================================================================================
            # Trend Removal and Scaling 
            # ======================================================================================================
            for k in range(len(self.dataBuffer[0])):
                for m in range(len(self.dataBuffer)):
                    self.dataBuffer[m][k] -= self.mean[k]
                    self.dataBuffer[m][k] *= self.scaling[k]

            # ======================================================================================================
            # Plot 
            # ======================================================================================================
            for k in range(len(self.dataBuffer[0])):
                if self.lastY:
                    painter.drawLine(self.idx * (self.width() / self.dataTr.chunksPerScreen) - self.interval, 
                    -self.lastY[k] + (k + 0.5) * self.channelHeight,
                    self.idx * (self.width() / self.dataTr.chunksPerScreen),
                    -self.dataBuffer[0][k] + (k + 0.5) * self.channelHeight)

                for m in range(len(self.dataBuffer) - 1):
                    painter.drawLine(m * self.interval + self.idx * (self.width() / self.dataTr.chunksPerScreen), 
                    -self.dataBuffer[m][k] + (k + 0.5) * self.channelHeight,
                    (m + 1) * self.interval + self.idx * (self.width() / self.dataTr.chunksPerScreen),
                    -self.dataBuffer[m+1][k] + (k + 0.5) * self.channelHeight)

            self.lastY = self.dataBuffer[-1]

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
