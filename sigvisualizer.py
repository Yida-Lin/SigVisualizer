import sys

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStatusBar,
                             QTreeWidgetItem)

from ui_sigvisualizer import Ui_MainWindow


class SigVisualizer(QMainWindow):
    panelHidden = False
    resized = pyqtSignal()
    update = pyqtSignal()
    streams = []

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Real Time Signal Visualizer')
        self.ui.treeWidget.setHeaderLabel('Streams')

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.ui.toggleButton.setIcon(QIcon("icons/chevron_left.svg"))
        self.ui.toggleButton.setIconSize(QSize(30, 30))

        self.ui.toggleButton.clicked.connect(self.togglePanel)
        self.ui.updateButton.clicked.connect(self.ui.widget.dataTr.updateStreams)
        self.ui.widget.dataTr.updateStreamNames.connect(self.updateMetadataWidget)

    def updateMetadataWidget(self, metadata, defaultIdx):
        for k in range(len(metadata)):
            item = QTreeWidgetItem(self.ui.treeWidget)
            item.setText(0, metadata[k]["streamName"])

            for m in range(metadata[k]["channelCount"]):
                channelItem = QTreeWidgetItem(item)
                channelItem.setText(0, 'Channel {}'.format(m+1))
                channelItem.setCheckState(0, Qt.Checked)

            item.setExpanded(True if k == defaultIdx else False)
            self.ui.treeWidget.addTopLevelItem(item)

        self.ui.treeWidget.setAnimated(True)
        self.statusBar.showMessage("Sampling rate: {}Hz".format(metadata[defaultIdx]["nominalSrate"]))

    def resizeEvent(self, event):
        self.resized.emit()
        return super(SigVisualizer, self).resizeEvent(event)

    def togglePanel(self):
        if self.panelHidden:
            self.panelHidden = False
            self.ui.treeWidget.show()
            self.ui.updateButton.show()
            self.ui.toggleButton.setIcon(QIcon("icons/chevron_left.svg"))
            self.ui.toggleButton.setIconSize(QSize(30, 30));
        else:
            self.panelHidden = True
            self.ui.treeWidget.hide()
            self.ui.updateButton.hide()
            self.ui.toggleButton.setIcon(QIcon("icons/chevron_right.svg"))
            self.ui.toggleButton.setIconSize(QSize(30, 30));

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SigVisualizer()
    window.showMaximized()
    sys.exit(app.exec_())
