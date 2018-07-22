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
    updateStreamNames = pyqtSignal(list)
    counter = -1
    data = np.zeros(shape=(10, 20))
    streams = []
    streamMetadata = [None] * 2

    def __init__(self, parent, rect):
        super(dataThread, self).__init__(parent)
        self.rect = rect
 
    def updateRect(self, rect):
        self.rect = rect

    def updateStreams(self):
        # first resolve an EEG stream on the lab network
        print("looking for an EEG stream...")

        if not self.streams:
            self.streams = resolve_stream('name', 'ActiChamp-0')
            
            if self.streams:
                # create a new inlet to read from the stream
                self.inlet = StreamInlet(self.streams[0])

                streamName = self.streams[0].name()

                self.streamMetadata[0] = streamName
                self.streamMetadata[1] = self.streams[0].channel_count()
        
                self.updateStreamNames.emit(self.streamMetadata)

    def run(self):
        while True:
            self.update.emit(self.rect)
            for k in range(self.data.shape[0]):
                for m in range(self.data.shape[1]):
                    self.data[k, m] = random.randint(1, 20)

            if self.counter < 50:
                self.rect.translate(20, 0)
                self.counter += 1
            else:
                self.rect.translate(-1000, 0)
                self.counter = 0
            time.sleep(0.002)

class PaintWidget(QWidget):
    idx = 0
    # data = np.random.rand(1, 2000)
    counter = 1
    data = []

    def __init__(self, widget):
        super().__init__()
        pal = QPalette()
        pal.setColor(QPalette.Background, Qt.white)
        self.setAutoFillBackground(True);
        self.setPalette(pal)

        self.dataTr = dataThread(self, QRect(0, 0, 20, 800))
        self.dataTr.update.connect(self.updateRectRegion)
        self.dataTr.start()

    def updateRectRegion(self, rect):
        self.update(rect)

    def paintEvent(self, event):
        # qp = QPainter(self)
        # qbrush = QBrush(Qt.white)
        # qp.setBackground(qbrush)
        # qp.drawLine(100,100,500,500)

        # painter = QPainter(self.ui.widget)
        # painter.begin(self.ui.widget)
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

        painter = QPainter(self)
        if self.dataTr.counter == -1:
            painter.fillRect(0, 0, self.width(), self.height(), Qt.white)
        painter.setPen(QPen(QColor(79, 106, 25), 1, Qt.SolidLine,
                            Qt.FlatCap, Qt.MiterJoin))
        painter.setBrush(QColor(122, 163, 39))


        painter.fillRect(self.dataTr.counter * 20, 0, self.dataTr.counter * 20 + 20, self.height(), Qt.white)
        for k in range(self.dataTr.data.shape[0]):
            for m in range(self.dataTr.data.shape[1] - 1):
                painter.drawLine(m + self.dataTr.counter * 20, 
                self.dataTr.data[k, m] + k * 60,
                m + 1 + self.dataTr.counter * 20,
                self.dataTr.data[k, m+1] + k * 60)

        # painter.drawPath(path)
        self.idx += 1



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
