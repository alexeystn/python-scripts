import sys

from serial_thread import SerialThread, State
import numpy as np
import json

from PyQt5.QtCore import Qt, QTimer, QSettings, pyqtSignal

from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,  QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QPushButton, QRadioButton, QVBoxLayout)

import pyqtgraph as pg


def load_profiles():
    with open('profiles.json', 'r') as f:
        profiles = json.load(f)
    for k in profiles.keys():
        arr = np.array(profiles[k], dtype='float')
        profiles[k] = {'time': arr[:, 0], 'power': arr[:, 1]}
    return profiles


class Window(QDialog):

    connectToPortSignal = pyqtSignal(str)
    runTestSignal = pyqtSignal(dict)

    def load_settings(self):
        settings = QSettings("AlexeyStn", "MotorTest")
        p = settings.value("comport")
        displayed_ports = [self.comportCombo.itemText(i) for i in range(self.comportCombo.count())]
        if p in displayed_ports:
            self.comportCombo.setCurrentText(p)
        else:
            print("Cannot find port")
        p = settings.value("profile")
        self.profileCombo.setCurrentText(p)
        t = settings.value("type")
        self.testTypeCombo.setCurrentText(t)
        p = settings.value("parallel")
        self.radioSimultaneous.setChecked(p)
        m = settings.value("motor")
        self.radioMotor[m].setChecked(True)

    def save_settings(self):
        settings = QSettings("AlexeyStn", "MotorTest")
        settings.setValue("comport", self.comportCombo.currentText())
        settings.setValue("profile", self.profileCombo.currentText())
        settings.setValue("type", self.testTypeCombo.currentText())
        settings.setValue("parallel", int(self.radioSimultaneous.isChecked()))
        m = [ch.isChecked() for ch in self.radioMotor].index(True)
        settings.setValue("motor", m)
        print("Settings saved")

    def __init__(self, parent=None):

        super(Window, self).__init__(parent)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle("Motor Test")
        self.palette = [(230, 0, 0), (0, 192, 0), (0, 128, 255), (192, 160, 0)]
        self.profiles = load_profiles()
        self.activeProfile = None

        connectionGroup = QGroupBox("Connection")
        connectionGrid = QVBoxLayout()
        connectionGroup.setLayout(connectionGrid)
        self.comportCombo = QComboBox()
        self.comportCombo.setSizeAdjustPolicy(2)
        self.refreshButton = QPushButton('Refresh')
        self.connectButton = QPushButton('Connect')
        connectionGrid.addWidget(self.comportCombo)
        connectionGrid.addWidget(self.connectButton)
        connectionGrid.addWidget(self.refreshButton)

        motorsGroup = QGroupBox("Motors")
        motorsGrid = QGridLayout()
        motorsGroup.setLayout(motorsGrid)
        pos = [[1, 1], [0, 1], [1, 0], [0, 0]]
        self.radioMotor = [QRadioButton('{0}'.format(i + 1)) for i in range(5)]
        for i in range(4):
            label = QLabel(' ')
            s = ','.join([str(c) for c in self.palette[i]])
            label.setStyleSheet("background-color: rgb({0})".format(s))
            motorsGrid.addWidget(label, pos[i][0], pos[i][1]*2)
            motorsGrid.addWidget(self.radioMotor[i], pos[i][0], pos[i][1]*2+1)
        self.radioMotor[4].setText('All motors')
        self.radioMotor[4].setChecked(True)
        motorsGrid.addWidget(self.radioMotor[4], 2, 0, 1, 4)

        profileGroup = QGroupBox("Profile")
        profileGrid = QVBoxLayout()
        profileGroup.setLayout(profileGrid)
        self.profileCombo = QComboBox()
        self.profileCombo.addItems(self.profiles.keys())
        self.radioOneByOne = QRadioButton('One-by-one')
        self.radioSimultaneous = QRadioButton('Simultaneous')
        self.radioOneByOne.setChecked(True)
        profileGrid.setSpacing(18)
        profileGrid.addWidget(self.profileCombo)
        profileGrid.addWidget(self.radioOneByOne)
        profileGrid.addWidget(self.radioSimultaneous)

        testGroup = QGroupBox("Test")
        testGrid = QVBoxLayout()
        testGroup.setLayout(testGrid)
        self.testTypeCombo = QComboBox()
        self.testTypeCombo.addItems(['RPM', 'Vibro'])
        self.clearButton = QPushButton('Clear')
        self.runButton = QPushButton('Run')
        testGrid.addWidget(self.testTypeCombo)
        testGrid.addWidget(self.clearButton)
        testGrid.addWidget(self.runButton)

        controlGrid = QHBoxLayout()
        controlGrid.addWidget(connectionGroup)
        controlGrid.addWidget(motorsGroup)
        controlGrid.addWidget(profileGroup)
        controlGrid.addWidget(testGroup)

        pg.setConfigOption('antialias', True)
        pg.setConfigOption('background', 'w')
        self.graphRpm = pg.PlotWidget()
        self.graphProfile = pg.PlotWidget()
        self.graphProfile.setTitle('Profile')
        self.plotAutoUpdateEnabled = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.plotTimeout)
        self.timer.start(200)

        # TODO: Fix MSP freezes

        self.graphRpm.setMouseEnabled(x=False, y=False)
        self.graphProfile.setMouseEnabled(x=False, y=False)
        self.graphRpm.showGrid(1, 2, 0.5)
        self.graphProfile.showGrid(1, 2, 0.5)

        fullLayout = QVBoxLayout()
        fullLayout.addWidget(self.graphRpm)
        fullLayout.addWidget(self.graphProfile)
        fullLayout.addLayout(controlGrid)
        self.setLayout(fullLayout)

        self.clearButton.clicked.connect(self.clearAllLogs)
        self.connectButton.clicked.connect(self.comportConnect)
        self.refreshButton.clicked.connect(self.comportRefreshList)
        self.runButton.clicked.connect(self.runTest)
        self.profileCombo.currentIndexChanged.connect(self.profileApply)
        self.testTypeCombo.currentIndexChanged.connect(self.testTypeApply)

        self.serialThread = SerialThread()
        self.comportRefreshList()
        self.runTestSignal.connect(self.serialThread.runTest)
        self.serialThread.infoUpdateSignal.connect(self.infoUpdate)
        self.serialThread.guiUpdateSignal.connect(self.guiUpdate)
        self.connectToPortSignal.connect(self.serialThread.connectToPort)

        try:
            self.load_settings()
        except Exception as e:
            print('Cannot load settings')
            print(e)

        self.profileApply()
        self.testTypeApply()
        self.serialThread.start()

    def profileApply(self):
        self.activeProfile = self.profiles[self.profileCombo.currentText()]
        self.plotActiveProfile()
        self.graphRpm.setXRange(0, self.activeProfile['time'][-1])
        self.graphProfile.setXRange(0, self.activeProfile['time'][-1])

    def testTypeApply(self):
        testType = self.testTypeCombo.currentText()
        self.clearAllLogs()
        if testType == "RPM":
            self.graphRpm.setTitle('E-RPM / 1000')
        else:
            self.graphRpm.setTitle('Vibration')

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
        self.save_settings()
        motorNumber = 0
        for i, radio in enumerate(self.radioMotor):
            if radio.isChecked():
                motorNumber = i
                break
        if motorNumber == 4:
            motorList = [0, 1, 2, 3]
        else:
            motorList = [motorNumber]
        runArg = {'motors': motorList,
                  'profile': self.activeProfile,
                  'parallel': self.radioSimultaneous.isChecked(),
                  'type': self.testTypeCombo.currentText()
                  }
        self.runTestSignal.emit(runArg)
        self.plotAutoUpdateEnabled = True

    def infoUpdate(self, info):
        line = ' | '.join([info['target'], info['firmware'], info['version'], info['api']])
        self.setWindowTitle(line)

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
        if self.serialThread.isConnected:
            return
        selectedItem = 0
        available_ports = self.serialThread.getAvailablePortsList()
        self.comportCombo.clear()
        for i, port in enumerate(available_ports):
            self.comportCombo.addItem(port)
            if 'modem' in port:
                selectedItem = i
        self.comportCombo.setCurrentIndex(selectedItem)

    def plotTimeout(self):
        if self.plotAutoUpdateEnabled:
            self.graphUpdate()

    def graphUpdate(self):
        rpmLog = self.serialThread.rpmLogger.get()
        self.graphRpm.clear()

        for rpmLogPart in rpmLog:
            if rpmLogPart:
                x = rpmLogPart['time']
                y = rpmLogPart['rpm']
                c = rpmLogPart['motor']
                self.graphRpm.plot(x, y, pen=pg.mkPen({'color': self.palette[c], 'width': 3}))
                # symbol='o', symbolSize=5, symbolBrush='k')


if __name__ == '__main__':
    load_profiles()
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec_()
    # window.closeEvent(0)
    sys.exit(0)
