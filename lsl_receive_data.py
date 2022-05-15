
from pylsl import StreamInlet, resolve_stream

print("looking for EMG stream...")
stream = resolve_stream('type', 'EMG')

inlet = StreamInlet(stream[0])

while True:
    sample, timestamp = inlet.pull_sample()
    print(timestamp, sample)