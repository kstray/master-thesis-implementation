import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
# import datetime
import hackeeg
from hackeeg import ads1299

SERIAL_PORT_PATH = "/dev/cu.usbmodem142201"
SAMPLES_PER_SECOND = ads1299.HIGH_RES_4k_SPS
GAIN = ads1299.GAIN_12X
CHANNELS = 8

# Configure ADS1299
hackeeg = hackeeg.HackEEGBoard(serial_port_path=SERIAL_PORT_PATH)
hackeeg.connect()
hackeeg.blink_board_led()
hackeeg.sdatac()
hackeeg.reset()
hackeeg.disable_all_channels()

# Set sampling rate
hackeeg.wreg(ads1299.CONFIG1, SAMPLES_PER_SECOND | ads1299.CONFIG1_const)

# Set internal voltage reference
hackeeg.wreg(ads1299.CONFIG3, ads1299.PD_REFBUF | ads1299.CONFIG3_const)

# Enable and configure channels for offset measurement
for i in range(1, 9):
    hackeeg.wreg(ads1299.CHnSET + i, ads1299.SHORTED | GAIN)


# Measure offset continuously for 5 seconds
hackeeg.blink_board_led()
hackeeg.messagepack_mode()
hackeeg.start()
hackeeg.rdatac()

print("Start")

offset = []
# timestamp = []
t_end = time.time() + 20
# start = datetime.datetime.now()
# last = start
while time.time() < t_end:
    result = hackeeg.read_rdatac_response()
    if result:
        offset.append(result)
        # now = datetime.datetime.now()
        # if ((now - last) > datetime.timedelta(seconds=3)):
        #     print("now")
        #     last = now
        #     timestamp.append(result.get('timestamp'))
    else:
        print("no data to decode")
        print(f"result: {result}")

print("Sampling complete")

hackeeg.sdatac()
# hackeeg.stop()


# Process offset data
channel_offset = np.empty((CHANNELS, len(offset)))
for i, s in enumerate(offset):
    dataKey = s.get(hackeeg.MpDataKey)
    if dataKey:
        data = s.get('channel_data')
        for channel in range(CHANNELS):
            channel_offset[channel, i] = data[channel]
channel_offset = channel_offset.astype(np.float64)
channel_offset = np.median(channel_offset, axis=1)
np.save('channel_offset.npy', channel_offset)