import numpy as np

def crc8(crc, a):
    crc ^= a
    for i in range(8):
        if crc & 128:
            crc = np.uint8((crc << 1) ^ 213)
        else:
            crc = np.uint8(crc << 1)
    return crc


def crc8_sbuf(buf):
    crc = 0
    for b in buf:
        crc = crc8(crc, b)
    return crc


def build_packet(rc_data):
    header = [int(h, 16) for h in ['C8', '18', '16']]
    # range from [-100;100] to [172;1811]
    rc_channels = [int(172 + (x+100)/200*(1811-172)) for x in rc_data]
    payload = [0] * 22
    for i in range(16):
        for j in range(11):
            if rc_channels[i] & (1<<j):
                pos = i*11 + j
                pbyte = pos // 8
                pbit = pos % 8
                payload[pbyte] |= 1 << pbit
    checksum = crc8_sbuf([header[2]] + payload)
    packet = header + payload + [int(checksum)]
    return packet
