import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import datetime
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

# Enable and configure channels
for i in range(1, 9):
   hackeeg.wreg(ads1299.CHnSET + i, ads1299.ELECTRODE_INPUT | GAIN)

# Differential mode - each channel is the differential voltage between adjacent electrodes
# hackeeg.wreg(ads1299.MISC1, ads1299.MISC1_const)
# For single-ended mode, uncomment the following line to set the SRB1 bit,
# which sends mid-supply voltage to the N inputs
hackeeg.wreg(ads1299.MISC1, ads1299.SRB1 | ads1299.MISC1_const)

# Choose bias as an average of all channels but channel 8
hackeeg.wreg(ads1299.BIAS_SENSP, 0b11111111)
hackeeg.wreg(ads1299.BIAS_SENSN, 0b11111111)
# Use internal BIASREF signal source and turn on bias amplifier
# route BIASOUT to bias electrode: JP9: 1-2, JP6: NC (not connected)
# route BIASOUT to BIASIN: JP9: 2-3
hackeeg.wreg(ads1299.CONFIG3, ads1299.PD_REFBUF | ads1299.BIASREF_INT | ads1299.PD_BIAS | ads1299.BIAS_LOFF_SENS | ads1299.CONFIG3_const)
# hackeeg.wreg(ads1299.CONFIG3, ads1299.PD_REFBUF | ads1299.CONFIG3_const)


# Read data continuously for 20 seconds
hackeeg.blink_board_led()
hackeeg.messagepack_mode()
hackeeg.start()
hackeeg.rdatac()

print("Start")
samples = []
timestamp = []
t_end = time.time() + 20
start = datetime.datetime.now()
last = start
while time.time() < t_end:
    result = hackeeg.read_rdatac_response()
    if result:
        samples.append(result)
        now = datetime.datetime.now()
        if ((now - last) > datetime.timedelta(seconds=3)):
            print("now")
            last = now
            timestamp.append(result.get('timestamp'))
    else:
        print("no data to decode")
        print(f"result: {result}")


print("Sampling complete")

hackeeg.sdatac()
# hackeeg.stop()


# Process samples
channel_data = np.empty((CHANNELS+1, len(samples)))
for i, s in enumerate(samples):
    dataKey = s.get(hackeeg.MpDataKey)
    if dataKey:
        timestamp = s.get('timestamp')
        data = s.get('channel_data')
        channel_data[0, i] = timestamp
        for channel in range(1,9):
            channel_data[channel, i] = data[channel-1]
channel_data = channel_data.astype(np.float64)

channel_offset = np.load('channel_offset.npy')
channel_data[1:] = channel_data[1:] - channel_offset[...,np.newaxis]
np.save('channel_data_single_biassense.npy', channel_data)