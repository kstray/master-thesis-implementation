
import numpy as np
from pylsl import StreamInlet, resolve_stream, local_clock
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGUI

plot_duration = 2.0

print("looking for EMG stream...")
stream = resolve_stream('type', 'EMG')

inlet = StreamInlet(stream[0])

window = pg.GraphicsWindow()
window.setWindowTitle('LSL Plot ' + inlet.info().name())
plt = window.addPlot()
plt.setLimits(xMin=0.0, xMax=plot_duration, yMin=-1.0 * (inlet.channel_count - 1), yMax=1.0)

t0 = [local_clock()] * inlet.channel_count
curves = []
for i in range(inlet.channel_count):
    curves += [plt.plot()]


def update():
    global inlet, curves, t0
    chunk, timestamps = inlet.pull_chunk(timeout=0.0, max_samples=32)
    if timestamps:
        timestamps = np.asarray(timestamps)
        y = np.asarray(chunk)

        for i in range(inlet.channel_count):
            old_x, old_y = curves[i].getData()
            if old_x is not None:
                old_x += t0[i]
                this_x = np.hstack((old_x, timestamps))
                this_y = np.hstack((old_y, y[:, i] - i))
            else:
                this_x = timestamps
                this_y = y[:, i] - i
            t0[i] = this_x[-1] - plot_duration
            this_x -= t0[i]
            b_keep = this_x >= 0
            curves[i].setData(this_x[b_keep], this_y[b_keep])


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()