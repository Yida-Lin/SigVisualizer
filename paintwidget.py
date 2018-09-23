from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QPalette, QPainter, QPen
from PyQt5.QtWidgets import QWidget
from pylsl import StreamInlet, resolve_streams
import math

class dataThread(QThread):
    updateStreamNames = pyqtSignal(list, int)
    sendSignalChunk = pyqtSignal(int, list)

    def __init__(self, parent):
        super().__init__(parent)
        self.chunksPerScreen = 50
        self.streams = []
        self.chunk_idx = 0
        self.seconds_per_screen = 2

    def updateStreams(self):
        if not self.streams:
            self.streams = resolve_streams(wait_time=1.0)

            if self.streams:
                self.stream_idx = -1
                self.metadata = [None] * len(self.streams) 

                for k in range(len(self.streams)):
                    self.metadata[k] = {
                        "name": self.streams[k].name(),
                        "ch_count": self.streams[k].channel_count(),
                        "ch_format": self.streams[k].channel_format(),
                        "srate": self.streams[k].nominal_srate()
                    }

                    if self.streams[k].channel_format() != "String" and self.stream_idx == -1:
                        self.stream_idx = k

                self.srate = int(self.streams[self.stream_idx].nominal_srate())
                self.downSampling = False if self.srate <= 1000 else True
                self.chunkSize = round(self.srate / self.chunksPerScreen * self.seconds_per_screen)

                if self.downSampling:
                    self.downSamplingFactor = round(self.srate / 1000)
                    self.downSamplingBuffer = [[0 for m in range(int(self.streams[self.stream_idx].channel_count()))]
                    for n in range(round(self.chunkSize/self.downSamplingFactor))]

                self.inlet = StreamInlet(self.streams[self.stream_idx])
                self.updateStreamNames.emit(self.metadata, self.stream_idx)
                self.start()

    def run(self):
        if self.streams:
            while True:
                chunk, timestamps = self.inlet.pull_chunk(max_samples=self.chunkSize, timeout=1)
                if timestamps:

                    if self.downSampling:
                        for k in range(int(self.streams[self.stream_idx].channel_count())):
                            for m in range(round(self.chunkSize/self.downSamplingFactor)):
                                endIdx = min((m+1) * self.downSamplingFactor, len(chunk))
                                buf = [chunk[n][k] for n in range(m * self.downSamplingFactor, endIdx)]
                                self.downSamplingBuffer[m][k] = sum(buf) / len(buf)

                        self.sendSignalChunk.emit(self.chunk_idx, self.downSamplingBuffer)
                    else:
                        self.sendSignalChunk.emit(self.chunk_idx, chunk)

                    if self.chunk_idx < self.chunksPerScreen:
                        self.chunk_idx += 1
                    else:
                        self.chunk_idx = 0

class PaintWidget(QWidget):

    def __init__(self, widget):
        super().__init__()
        self.idx = 0
        self.channelHeight = 0
        self.interval = 0
        self.dataBuffer = []
        self.lastY = []
        self.scaling = []
        self.mean = []

        pal = QPalette()
        pal.setColor(QPalette.Background, Qt.white)
        self.setAutoFillBackground(True)
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
                    if not math.isnan(self.lastY[k]) and not math.isnan(self.dataBuffer[0][k]):
                        painter.drawLine(self.idx * (self.width() / self.dataTr.chunksPerScreen) - self.interval,
                        -self.lastY[k] + (k + 0.5) * self.channelHeight,
                        self.idx * (self.width() / self.dataTr.chunksPerScreen),
                        -self.dataBuffer[0][k] + (k + 0.5) * self.channelHeight)

                for m in range(len(self.dataBuffer) - 1):
                    if not math.isnan(self.dataBuffer[m][k]) and not math.isnan(self.dataBuffer[m+1][k]):
                        painter.drawLine(m * self.interval + self.idx * (self.width() / self.dataTr.chunksPerScreen),
                        -self.dataBuffer[m][k] + (k + 0.5) * self.channelHeight,
                        (m + 1) * self.interval + self.idx * (self.width() / self.dataTr.chunksPerScreen),
                        -self.dataBuffer[m+1][k] + (k + 0.5) * self.channelHeight)

            self.lastY = self.dataBuffer[-1]
