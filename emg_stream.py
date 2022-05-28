#!/usr/bin/env python


import sys
import time
import hackeeg
from hackeeg import ads1299
from pylsl import StreamInfo, StreamOutlet
import numpy as np


SERIAL_PORT_PATH = "/dev/cu.usbmodem143301"
SAMPLES_PER_SECOND = ads1299.HIGH_RES_1k_SPS
CHANNELS = 8

hackeeg = hackeeg.HackEEGBoard(serial_port_path=SERIAL_PORT_PATH, debug=False)
hackeeg.connect()
hackeeg.blink_board_led()
hackeeg.sdatac()
hackeeg.reset()
hackeeg.disable_all_channels()

# Set sampling rate
hackeeg.wreg(ads1299.CONFIG1, SAMPLES_PER_SECOND | ads1299.CONFIG1_const)

hackeeg.enable_all_channels()

# Configure channel input and gain
for channel in range(1, 9):
    hackeeg.wreg(ads1299.CHnSET + channel, ads1299.ELECTRODE_INPUT | ads1299.GAIN_24X)

# Bipolar mode - each channel is the differential voltage between adjacent electrodes
# hackeeg.wreg(ads1299.MISC1, ads1299.MISC1_const)
# For unipolar mode, uncomment the following line to set the SRB1 bit,
# which sends mid-supply voltage to the N inputs
hackeeg.wreg(ads1299.MISC1, ads1299.SRB1 | ads1299.MISC1_const)

# Choose bias as an average of the first three channels
hackeeg.wreg(ads1299.BIAS_SENSP, ads1299.BIAS1P | ads1299.BIAS2P | ads1299.BIAS3P)
hackeeg.wreg(ads1299.BIAS_SENSN, ads1299.BIAS1N | ads1299.BIAS2N | ads1299.BIAS3N)
# Use internal BIASREF signal source and turn on bias amplifier
# route BIASOUT to bias electrode: JP9: 2-3, JP6: NC (not connected)
hackeeg.wreg(ads1299.CONFIG3, ads1299.BIASREF_INT | ads1299.PD_BIAS |ads1299.CONFIG3_const)

hackeeg.messagepack_mode()

# Stream data to OpenBCI GUI via Lab Streaming Layer (LSL)
lsl_info = StreamInfo('EMG-stream', 'EEG', CHANNELS, SAMPLES_PER_SECOND, 'int32')
lsl_outlet = StreamOutlet(lsl_info)

# Read data continuously
hackeeg.blink_board_led()
hackeeg.start()
hackeeg.rdatac()


samples = []
t_end = time.time() + 5
channel_1 = np.empty((1, 5000))
while time.time() < t_end:
    result = hackeeg.read_rdatac_response()
    if result:
        samples.append(result)
        data = result.get(hackeeg.MpDataKey)
        if data:
            timestamp = result.get('timestamp')
            channel_data = result.get('channel_data')
            


        
    else:
        print("no data to decode")
        print(f"result: {result}")






        

