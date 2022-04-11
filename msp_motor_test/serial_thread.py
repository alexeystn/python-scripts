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
    MSP_RAW_IMU = 102
    MSP_MOTOR_TELEMETRY = 139
    MSP_SET_MOTOR = 214


class State(enum.Enum):
    CONNECTED = 1
    DISCONNECTED = 2
    RUNNING = 3
    FINISHED = 4


class Performance:

    log = None

    def __init__(self, num_records=500):
        self.reset(num_records)

    def tic(self, func_id, enabled=True):
        if not enabled:
            return
        self.time_tic[func_id] = time.perf_counter()

    def toc(self, func_id, enabled=True):
        if not enabled:
            return
        time_toc = time.perf_counter()
        res = time_toc - self.time_tic[func_id]
        if self.pointer[func_id] < len(self.log):
            self.log[self.pointer[func_id], func_id] = res * 1000
            self.pointer[func_id] += 1

    def reset(self, num_records, num_func=2):
        self.log = np.zeros((num_records, num_func))
        self.time_tic = np.zeros((num_func, ))
        self.pointer = [0] * num_func

    def output(self):
        for i in range(len(self.log)):
            t = self.log[i, :]
            if t[0] == 0:
                break
            print('{0:.0f}\t{1:.0f}'.format(t[0], t[1]))


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

    def clear(self):
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
    parallel = False
    type = None
    prevAccValue = None

    def __init__(self):
        QThread.__init__(self)
        self.perf = Performance(500)
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
            except Exception as e:
                print('Cannot connect')
                self.isConnected = False
                self.port.close()
                print(e)
            else:
                self.isConnected = True
                info = self.getInfo()
                self.infoUpdateSignal.emit(info)
                self.guiUpdateSignal.emit(State.CONNECTED)

    def run(self):
        while True:
            if self.isRunning:
                self.guiUpdateSignal.emit(State.RUNNING)
                self.perf = Performance()

                motors = self.motorList
                for mot in motors:
                    self.rpmLogger.newLog(mot)

                if self.parallel:
                    motorSets = [motors]
                else:
                    motorSets = [[m] for m in motors]

                for motors in motorSets:
                    timeProfile = self.profile['time']
                    powerProfile = self.profile['power']
                    startTime = time.time()
                    while True:
                        currentTime = time.time() - startTime
                        currentPower = np.interp(currentTime, timeProfile, powerProfile)
                        m = int(1000 + currentPower / 100.0 * 1000)
                        response = self.sendMotorValue(motors, m, self.type)
                        self.rpmLogger.put(currentTime, motors, response)
                        if currentTime > timeProfile[-1]:
                            break
                    self.sendMotorValue(motors, 950, self.type)
                    self.perf.output()

                self.isRunning = False

                self.guiUpdateSignal.emit(State.FINISHED)

                intervals = np.diff(np.array(self.rpmLogger.rmpLog[-1]['time']))
                intervalMean = np.median(intervals)
                print('Frequency: {0:.2f}Hz'.format(1 / intervalMean))

    def sendMotorValue(self, motorIdx, value, testType):
        packet = [0] * 8
        for m in motorIdx:
            packet[m * 2] = value % 256
            packet[m * 2 + 1] = value // 256
        self.perf.tic(0)
        self.mspSend(Msp.MSP_SET_MOTOR, packet)
        self.perf.toc(0)
        self.perf.tic(1)
        if testType == 'RPM':
            motorTelemetry = self.mspSend(Msp.MSP_MOTOR_TELEMETRY, [])
            response = self.decodeRpm(motorTelemetry)
        else:  # Vibro
            imuTelemetry = self.mspSend(Msp.MSP_RAW_IMU, [])
            response = self.decodeImu(imuTelemetry)
        self.perf.toc(1)
        return response

    def mspSend(self, code, data):
        msg = self.encodeMessage(code, data)
        self.sendMessage(msg)
        response = self.readMessage()
        return response

    @staticmethod
    def decodeRpm(msg):
        lsb = msg[1::13]
        msb = msg[2::13]
        rpm = [l + m * 256 for (l, m) in zip(lsb, msb)]
        return rpm

    def decodeImu(self, msg):
        lsb = msg[0:6:2]
        msb = msg[1:6:2]
        imuCurrent = [np.int16(l + m * 256) for (l, m) in zip(lsb, msb)]
        if not self.prevAccValue:
            self.prevAccValue = imuCurrent
            result = 0
        else:
            dx = float(imuCurrent[0] - self.prevAccValue[0])
            dy = float(imuCurrent[1] - self.prevAccValue[1])
            #dz = imuCurrent[0] - self.prevAccValue[0]
            dXY = np.sqrt(dx*dx+dy*dy)
            result = dXY
            self.prevAccValue = imuCurrent
        return [result] * 4

    def runTest(self, arg):
        if not self.isConnected:
            return
        if self.isRunning:
            return
        self.motorList = arg['motors']
        self.profile = arg['profile']
        self.parallel = arg['parallel']
        self.type = arg['type']
        self.prevAccValue = None
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

    @staticmethod
    def encodeMessage(code, data):
        buf = [ord('$'), ord('M'), ord('<'), len(data), code.value]
        checksum = buf[3] ^ buf[4]
        for d in data:
            buf.append(d)
            checksum ^= d
        buf.append(checksum)
        return buf

    @staticmethod
    def decodeTargetName(msg):
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

    @staticmethod
    def getAvailablePortsList():
        result = [c.device for c in serial.tools.list_ports.comports()]
        return result
