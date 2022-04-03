import enum
import serial
import serial.tools.list_ports
import time
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal, QMutex


class Msp(enum.Enum):
    MSP_API_VERSION = 1
    MSP_FC_VARIANT = 2
    MSP_FC_VERSION = 3
    MSP_BOARD_INFO = 4
    MSP_MOTOR_TELEMETRY = 139
    MSP_SET_MOTOR = 214


class State(enum.Enum):
    CONNECTED = 1
    DISCONNECTED = 2
    RUNNING = 3
    FINISHED = 4


class LoggerRPM:
    def __init__(self):
        self.rmpLog = []
        self.logPointers = [0, 0, 0, 0]
        self.mutex = QMutex()
        return

    def newLog(self, n):
        res = {'motor': n, 'time': [], 'rpm': []}
        self.rmpLog.append(res)
        self.logPointers[n] = len(self.rmpLog) - 1

    def clear(self, mask=None):
        self.mutex.lock()
        self.rmpLog = []
        self.logPointers = [0, 0, 0, 0]
        self.mutex.unlock()

    def put(self, timestamp,  mask, values):
        for motor in mask:
            idx = self.logPointers[motor]
            self.mutex.lock()
            self.rmpLog[idx]['time'].append(timestamp)
            self.rmpLog[idx]['rpm'].append(values[motor] / 1000)
            self.mutex.unlock()

    def get(self):
        self.mutex.lock()
        result = self.rmpLog.copy()
        self.mutex.unlock()
        return result

class SerialThread(QThread):
    infoUpdateSignal = pyqtSignal(dict)
    guiUpdateSignal = pyqtSignal(State)

    port = None
    isConnected = False
    isRunning = False
    motorList = []
    profile = None

    def __init__(self):
        QThread.__init__(self)
        self.rpmLogger = LoggerRPM()

    def connectToPort(self, portName):
        if not portName:  # disconnect
            self.port.close()
            print('Disconnected')
            self.guiUpdateSignal.emit(State.DISCONNECTED)
        else:
            print('Connecting to', portName)
            try:
                self.port = serial.Serial(portName, timeout=1)
            except Exception:
                print('Cannot connect')
                self.isConnected = False
                self.port.close()
            else:
                self.isConnected = True
                info = self.getInfo()
                self.infoUpdateSignal.emit(info)
                self.guiUpdateSignal.emit(State.CONNECTED)

    def run(self):
        while True:
            if self.isRunning:
                self.guiUpdateSignal.emit(State.RUNNING)
                motors = self.motorList
                for mot in motors:
                    self.rpmLogger.newLog(mot)

                timeProfile = self.profile['time']
                powerProfile = self.profile['power']
                startTime = time.time()
                while True:
                    currentTime = time.time() - startTime
                    currentPower = np.interp(currentTime, timeProfile, powerProfile)
                    m = int(1000 + currentPower / 100.0 * 1000)
                    rpm = self.sendMotorValue(motors, m)
                    self.rpmLogger.put(currentTime, motors, rpm)
                    if currentTime > timeProfile[-1]:
                        break

                self.sendMotorValue(motors, 950)
                self.isRunning = False
                self.guiUpdateSignal.emit(State.FINISHED)

                intervals = np.diff(np.array(self.rpmLogger.rmpLog[-1]['time']))
                intervalMean = np.median(intervals)
                print('Frequency: {0:.2f}Hz'.format(1 / intervalMean))

    def sendMotorValue(self, motorIdx, value):
        packet = [0] * 8
        for m in motorIdx:
            packet[m * 2] = value % 256
            packet[m * 2 + 1] = value // 256

        self.mspSend(Msp.MSP_SET_MOTOR, packet)  # TODO: Speed-up exchange
        motorTelemetry = self.mspSend(Msp.MSP_MOTOR_TELEMETRY, [])
        rpm = self.decodeRpm(motorTelemetry)
        return rpm

    def mspSend(self, code, data):
        msg = self.encodeMessage(code, data)
        self.sendMessage(msg)
        response = self.readMessage()
        return response

    def decodeRpm(self, msg):
        lsb = msg[1::13]
        msb = msg[2::13]
        rpm = [l + m * 256 for l, m in zip(lsb, msb)]
        return rpm

    def runTest(self, arg):
        if not self.isConnected:
            return
        if self.isRunning:
            return
        self.motorList = arg['motors']
        self.profile = arg['profile']
        self.isRunning = True
        return

    def getInfo(self):
        info = {}
        boardInfo = self.mspSend(Msp.MSP_BOARD_INFO, [])
        info['target'] = self.decodeTargetName(boardInfo)

        apiVersion = self.mspSend(Msp.MSP_API_VERSION, [])
        info['api'] = '{0}.{1}'.format(apiVersion[1], apiVersion[2])

        fcVariant = self.mspSend(Msp.MSP_FC_VARIANT, [])
        info['firmware'] = fcVariant.decode()

        fcVersion = self.mspSend(Msp.MSP_FC_VERSION, [])
        info['version'] = '{0}.{1}.{2}'.format(fcVersion[0], fcVersion[1], fcVersion[2])

        return info

    def encodeMessage(self, code, data):
        buf = [ord('$'), ord('M'), ord('<'), len(data), code.value]
        checksum = buf[3] ^ buf[4]
        for d in data:
            buf.append(d)
            checksum ^= d
        buf.append(checksum)
        return buf

    def decodeTargetName(self, msg):
        mcu_length_pos = 8
        target_name_start = mcu_length_pos + msg[mcu_length_pos] + 1
        target_name_length = msg[target_name_start]
        result = msg[target_name_start + 1:target_name_start + 1 + target_name_length]
        return result.decode()

    def sendMessage(self, msg):
        self.port.write(bytes(msg))

    def readMessage(self):
        header = '$M>'
        header_counter = 0
        while True:  # TODO: timeout
            b = self.port.read(1)
            if b.decode() == header[header_counter]:
                header_counter += 1
                if header_counter == len(header):
                    break
            else:
                header_counter = 0
        length = int.from_bytes(self.port.read(1), 'big')
        tag = int.from_bytes(self.port.read(1), 'big')
        payload = self.port.read(length)
        crc = int.from_bytes(self.port.read(1), 'big')
        crc_check = length ^ tag
        for i in range(length):
            crc_check ^= payload[i]
        if crc_check != crc:
            payload = b''
        return payload

    def getAvailablePortsList(self):
        result = [c.device for c in serial.tools.list_ports.comports()]
        return result
