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

class PaintWidget(QWidget):

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

        path = QPainterPath()
        path.addRect(20, 20, 60, 60)

        path.moveTo(0, 0)
        path.cubicTo(99, 0,  50, 50,  99, 99)
        path.cubicTo(0, 99,  50, 50,  0, 0)

        painter = QPainter(self)
        painter.fillRect(0, 0, 100, 100, Qt.white)
        painter.setPen(QPen(QColor(79, 106, 25), 1, Qt.SolidLine,
                            Qt.FlatCap, Qt.MiterJoin))
        painter.setBrush(QColor(122, 163, 39))

        painter.drawPath(path)
        # self.ui.widget.update()