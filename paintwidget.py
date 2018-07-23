from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QPalette, QPainter, QPen
from PyQt5.QtWidgets import QWidget
from pylsl import StreamInlet, resolve_streams


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
                    self.downSamplingFactor = round(self.nominal_srate / 1000)
                    self.downSamplingBuffer = [[0 for m in range(int(self.streams[self.defaultIdx].channel_count()))]
                    for n in range(round(self.chunkSize/self.downSamplingFactor))]

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
                            for m in range(round(self.chunkSize/self.downSamplingFactor)):
                                if m != round(self.chunkSize/self.downSamplingFactor):
                                    endIdx = (m+1) * self.downSamplingFactor

                                    buf = [chunk[n][k] for n in range(m * self.downSamplingFactor, endIdx)]
                                else:
                                    buf = [chunk[n][k] for n in range(m * self.downSamplingFactor, len(chunk))]

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
