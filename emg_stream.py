
import sys
import hackeeg
from hackeeg import ads1299

SERIAL_PORT_PATH = "/dev/cu.usbmodem143201"

hackeeg = hackeeg.HackEEGBoard(SERIAL_PORT_PATH)
hackeeg.connect()
hackeeg.blink_board_led()
hackeeg.sdatac()
hackeeg.reset()
hackeeg.disable_all_channels()

# Set sampling rate
hackeeg.wreg(ads1299.CONFIG1, ads1299.HIGH_RES_1k_SPS | ads1299.CONFIG1_const)

hackeeg.enable_all_channels()

# Configure channel input and gain
for channel in range(1, 9):
    hackeeg.wreg(ads1299.CHnSET + channel, ads1299.ELECTRODE_INPUT | ads1299.GAIN_1X)

# Bipolar mode - each channel is the differential voltage between adjacent electrodes
hackeeg.wreg(ads1299.MISC1, ads1299.MISC1_const)
# For unipolar mode, uncomment the following line to set the SRB1 bit,
# which sends mid-supply voltage to the N inputs
# hackeeg.wreg(ads1299.MISC1, ads1299.SRB1 | ads1299.MISC1_const)

# Choose bias as an average of the first three channels
#hackeeg.wreg(ads1299.BIAS_SENSP, ads1299.BIAS1P | ads1299.BIAS2P | ads1299.BIAS3P)
#hackeeg.wreg(ads1299.BIAS_SENSN, ads1299.BIAS1N | ads1299.BIAS2N | ads1299.BIAS3N)
# Use internal BIASREF signal source and turn on bias amplifier
# route BIASOUT to bias electrode: JP9: 2-3, JP6: NC (not connected)
#hackeeg.wreg(ads1299.CONFIG3, ads1299.BIASREF_INT | ads1299.PD_BIAS |ads1299.CONFIG3_const)

hackeeg.messagepack_mode()
#hackeeg.jsonlines_mode()

# Read data continuously
hackeeg.rdatac()
hackeeg.blink_board_led()
hackeeg.start()


while True:
    result = hackeeg.read_response()
    data = result.get(hackeeg.DataKey)
    if data:
        decoded_data = result.get(hackeeg.DecodedDataKey)
        if decoded_data:
            timestamp = decoded_data.get('timestamp')
            channel_data = decoded_data.get('channel_data')
            for channel_number, sample in enumerate(channel_data):
                print(f"{channel_number + 1}:{sample} ", end='')
            print()
        else:
            print(data)
        sys.stdout.flush()
