import sys

from serial_thread import SerialThread, State
import numpy as np
import json

from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, pyqtSlot

from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QFileDialog, QButtonGroup, QErrorMessage)

import pyqtgraph as pg


def load_profiles():
    with open('profiles.json', 'r') as f:
        profiles = json.load(f)
    for k in profiles.keys():
        arr = np.array(profiles[k], dtype='float')
        profiles[k] = {'time': arr[:,0], 'power': arr[:,1]}
    return profiles


class Window(QDialog):

    connectToPortSignal = pyqtSignal(str)
    #signalStartCom =
    runTestSignal = pyqtSignal(dict)

    def __init__(self, parent=None):

        super(Window, self).__init__(parent)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle("Motor Test")

        self.comportCombo = QComboBox()
        self.connectButton = QPushButton('Connect')
        self.refreshButton = QPushButton('Refresh')
        self.statusLabel = QLabel('Not connected')
        self.connectButton.setDefault(True)

        pg.setConfigOption('antialias', True)
        pg.setConfigOption('background', 'w')
        self.graphRpm = pg.PlotWidget()
        self.graphRpm.setTitle('E-RPM / 1000')
        self.graphProfile = pg.PlotWidget()
        self.graphProfile.setTitle('Profile')
        self.plotAutoUpdateEnabled = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.plotTimeout)
        self.timer.start(50)

        self.graphRpm.setMouseEnabled(x=False, y=False)
        self.graphProfile.setMouseEnabled(x=False, y=False)
        self.graphRpm.showGrid(1, 2, 0.5)
        self.graphProfile.showGrid(1, 2, 0.5)

        self.clearButton = QPushButton('Clear')
        self.motorCombo = QComboBox()
        motorList = ['Motor {0}'.format(i+1) for i in range(4)] + ['All motors']
        self.motorCombo.addItems(motorList)

        self.profiles = load_profiles()
        self.profileCombo = QComboBox()
        self.profileCombo.addItems(self.profiles.keys())
        self.activeProfile = None

        self.runButton = QPushButton('Run')

        fullLayout = QGridLayout()
        fullLayout.addWidget(self.comportCombo, 0, 0, 1, 2)
        fullLayout.addWidget(self.refreshButton, 0, 2)
        fullLayout.addWidget(self.connectButton, 0, 3)
        fullLayout.addWidget(self.statusLabel, 1, 0, 1, 4)
        fullLayout.addWidget(self.graphRpm, 2, 0, 1, 4)
        fullLayout.addWidget(self.graphProfile, 3, 0, 1, 4)
        fullLayout.addWidget(self.clearButton, 4, 0)
        fullLayout.addWidget(self.motorCombo, 4, 1)
        fullLayout.addWidget(self.profileCombo, 4, 2)
        fullLayout.addWidget(self.runButton, 4, 3)


        self.clearButton.clicked.connect(self.clearAllLogs)
        self.refreshButton.clicked.connect(self.comportRefreshList)
        self.connectButton.clicked.connect(self.comportConnect)
        self.runButton.clicked.connect(self.runTest)
        self.profileCombo.currentIndexChanged.connect(self.profileApply)

        self.setLayout(fullLayout)

        self.serialThread = SerialThread()

        self.comportRefreshList()
        self.runTestSignal.connect(self.serialThread.runTest)
        self.serialThread.infoUpdateSignal.connect(self.infoUpdate)
        self.serialThread.guiUpdateSignal.connect(self.guiUpdate)
        self.connectToPortSignal.connect(self.serialThread.connectToPort)

        self.profileApply(0)
        self.serialThread.start()

    def profileApply(self, idx):
        self.activeProfile = self.profiles[self.profileCombo.currentText()]
        self.plotActiveProfile()
        print('Profile:', self.profileCombo.currentText())
        self.graphRpm.setXRange(0, self.activeProfile['time'][-1])
        self.graphProfile.setXRange(0, self.activeProfile['time'][-1])

    def plotActiveProfile(self):
        x = self.activeProfile['time']
        y = self.activeProfile['power']
        self.graphProfile.clear()
        self.graphProfile.plot(x, y, pen=pg.mkPen({'color': [0, 0, 0], 'width': 3}),
                               symbol='o', symbolSize=5, symbolBrush='k')

    def guiUpdate(self, state):
        if state == State.DISCONNECTED:
            self.connectButton.setText('Connect')
            self.connectButton.clicked.disconnect(self.comportDisconnect)
            self.connectButton.clicked.connect(self.comportConnect)
        elif state == State.CONNECTED:
            self.connectButton.setText('Disconnect')
            self.connectButton.clicked.disconnect(self.comportConnect)
            self.connectButton.clicked.connect(self.comportDisconnect)
        elif state == State.RUNNING:
            self.runButton.setEnabled(False)
        elif state == State.FINISHED:
            self.runButton.setEnabled(True)
            self.plotAutoUpdateEnabled = False
            self.graphUpdate()

    def runTest(self):
        motorNumber = self.motorCombo.currentIndex()
        if motorNumber == 4:
            motorList = [0, 1, 2, 3]
        else:
            motorList = [motorNumber]
        self.runTestSignal.emit({'motors': motorList, 'profile': self.activeProfile})
        self.plotAutoUpdateEnabled = True
        print('START!!!', motorNumber)

    def infoUpdate(self, info):
        line = ' | '.join([info['target'], info['firmware'], info['version'], info['api']])
        self.statusLabel.setText(line)

    def clearAllLogs(self):
        if self.serialThread.isRunning:
            return
        self.serialThread.rpmLogger.clear()
        self.graphUpdate()

    def comportConnect(self):
        portName = self.comportCombo.currentText()
        self.connectToPortSignal.emit(portName)

    def comportDisconnect(self):
        self.connectToPortSignal.emit(None)

    def comportRefreshList(self):
        selectedItem = 0
        self.comportCombo.clear()
        available_ports = self.serialThread.getAvailablePortsList()

        for i, port in enumerate(available_ports):
            if 'modem' in port:
                selectedItem = i
            self.comportCombo.addItem(port)
        self.comportCombo.setCurrentIndex(selectedItem)

    def plotTimeout(self):
        if self.plotAutoUpdateEnabled:
            self.graphUpdate()

    def graphUpdate(self):
        rpmLog = self.serialThread.rpmLogger.get()
        self.graphRpm.clear()
        palette = [(255, 0, 0), (0, 192, 0), (0, 64, 255), (192, 160, 0)]

        for rpmLogPart in rpmLog:
            if rpmLogPart:
                x = rpmLogPart['time']
                y = rpmLogPart['rpm']
                c = rpmLogPart['motor']
                self.graphRpm.plot(x, y, pen=pg.mkPen({'color': palette[c], 'width': 3}))
                                   # symbol='o', symbolSize=5, symbolBrush='k')

if __name__ == '__main__':
    load_profiles()
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec_()
    # window.closeEvent(0)
    sys.exit(0)
