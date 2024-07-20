# https://gist.github.com/spewil/c08c6da6c62243d832e94a942a86bec8
# pyqt with a background process updating shared memory block thanks to python 3.8

import time
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QPushButton
import multiprocessing
from multiprocessing import shared_memory
import numpy as np

DATA_SIZE = 2
DTYPE = np.int64


class DataPuller(multiprocessing.Process):
    def __init__(
            self,
            stop_event, reset_event,
            shared_mem_name,
    ):
        super().__init__()
        self.stop_event = stop_event
        self.reset_event = reset_event
        self.counter = 0
        self.shared_mem_name = shared_mem_name

    def run(self):
        self.shm = shared_memory.SharedMemory(name=self.shared_mem_name)
        self.sample = np.ndarray(
            shape=(DATA_SIZE, 1), dtype=DTYPE, buffer=self.shm.buf)
        print("child process started")
        while not self.stop_event.is_set():
            time.sleep(0.01)
            if self.reset_event.is_set():
                self.counter = self.sample[1, 0]
                self.reset_event.clear()
            self.sample[0, 0] = self.counter
            # print("child: ", self.sample[0, 0])
            self.counter += 1
            if self.counter >= 1000:
                self.counter = 0
        self.shm.close()
        print("child process finished")


class Window(QWidget):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(self)
        self.progressBar = QProgressBar(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.onTimer)
        self.progressBar.setRange(0, 1000)
        layout.addWidget(self.progressBar)
        layout.addWidget(QPushButton('Start', self, clicked=self.onStart))
        layout.addWidget(QPushButton('Reset', self, clicked=self.onReset))

        self.counter = 0
        self.shared_mem_name = "data2"
        self.base_array = np.zeros((DATA_SIZE, 1), dtype=DTYPE)
        self.shm = shared_memory.SharedMemory(
            create=True,
            size=self.base_array.nbytes,
            name=self.shared_mem_name)
        self.sample = np.ndarray(
            shape=self.base_array.shape,
            dtype=self.base_array.dtype,
            buffer=self.shm.buf)
        self.stop_event = multiprocessing.Event()
        self.reset_event = multiprocessing.Event()
        self._process = DataPuller(self.stop_event, self.reset_event, self.shared_mem_name)

    def onStart(self):
        if not self._process.is_alive():
            print("main starting process")
            self._process.start()
            self.timer.start(16)
        else:
            pass

    def onTimer(self):
        print("main: ", self.sample[0, 0])
        self.progressBar.setValue(self.sample[0, 0])

    def onReset(self):
        if self._process.is_alive():
            print('reset')
            self.sample[1, 0] = 333
            print(1111)
            self.reset_event.set()
            print(2222)

    def closeEvent(self, event):
        if self._process.is_alive():
            self.stop_event.set()
            self._process.join()
        self.shm.close()
        self.shm.unlink()
        self.close()
        print("main process finished")


if __name__ == '__main__':
    # need this to match OSX on Windows
    multiprocessing.set_start_method("spawn")
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())


"""from matplotlib import pyplot as plt

x1, x2, resps, thr = [],[],[],[]
sub_starts, sub_ends = [], []
scene_starts, scene_ends = [], []
with open('data/log.txt') as log:
    for row in log:
        data = row.split("\t")
        if data[0] == 'plot':
            current_pos, scene_end, resp, thresh = data[1:]
            x1.append(float(current_pos))
            x2.append(float(scene_end))
            resps.append(float(resp))
            thr.append(float(thresh))
        elif data[0] == 'sub':
            sub_scene_start, current_pos = data[1:]
            sub_starts.append(float(sub_scene_start))
            sub_ends.append(float(current_pos))
        elif data[0] == 'scene':
            scene_start, scene_end = data[1:]
            scene_starts.append(float(scene_start))
            scene_ends.append(float(scene_end))

plt.figure()
plt.plot(x1, resps)
plt.plot(x1, thr)
for i in range(len(sub_starts)):
    plt.plot([sub_starts[i], sub_ends[i]], [-0.5, -0.8])
for i in range(len(scene_starts)):
    plt.plot([scene_starts[i], scene_ends[i]], [-1.5, -1.8])

# plt.scatter(sub_ends, [.1]*len(sub_ends), label='sub_end')
# plt.scatter(scene_ends, [.2]*len(scene_ends), label='scene_end')
plt.legend()
plt.show()
"""






'''

# https://mountcreo.com/article/pyqtpyside-drag-and-drop-qtableview-reordering-rows/


from PyQt5.QtCore import (Qt)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QProxyStyle, QStyleOption,
                             QTableView, QHeaderView,
                             QItemDelegate,
                             QApplication, QLabel)


class customTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSelectionBehavior(self.SelectRows)  # Select whole rows
        self.setSelectionMode(self.SingleSelection)  # Only select/drag one row each time
        self.setDragDropMode(
            self.InternalMove)  # Objects can only be drag/dropped internally and are moved instead of copied
        self.setDragDropOverwriteMode(False)  # Removes the original item after moving instead of clearing it

        # Set our custom style - this draws the drop indicator across the whole row
        self.setStyle(customStyle())

        model = customModel()
        self.setModel(model)
        self.populate()

    def populate(self):
        set_enabled = True  # We'll change this value to show how to drag rows with disabled elements later
        model = self.model()
        for row in ['a', 'b', 'c', 'd', 'e', 'f', 'g']:
            data = []
            for column in range(5):
                item = QStandardItem(f'{row}-{column}')
                item.setDropEnabled(False)
                if column == 3:
                    item.setEnabled(set_enabled)
                data.append(item)
            model.appendRow(data)
        self.setColumnHidden(2, True)


class customModel(QStandardItemModel):
    def mimeData(self, indices):
        """
        Move all data, including hidden/disabled columns
        """
        index = indices[0]
        new_data = []

        for col in range(self.columnCount()):
            new_data.append(index.sibling(index.row(), col))

        item = self.item(index.row(), 3)
        self.was_enabled = item.isEnabled()
        item.setEnabled(True)  # Hack// Fixes copying instead of moving when item is disabled

        return super().mimeData(new_data)

    def dropMimeData(self, data, action, row, col, parent):
        """
        Always move the entire row, and don't allow column "shifting"
        """
        response = super().dropMimeData(data, Qt.CopyAction, row, 0, parent)
        if row == -1:  # Drop after last row
            row = self.rowCount() - 1
        item = self.item(row, 3)
        item.setEnabled(self.was_enabled)  # Hack// Fixes copying instead of moving when style column is disabled
        return response

class customStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget=None):
        """
        Draw a line across the entire row rather than just the column
        we're hovering over.  This may not always work depending on global
        style - for instance I think it won't work on OSX.
        """
        if element == self.PE_IndicatorItemViewItemDrop and not option.rect.isNull():
            option_new = QStyleOption(option)
            option_new.rect.setLeft(0)
            if widget:
                option_new.rect.setRight(widget.width())
            option = option_new
        super().drawPrimitive(element, option, painter, widget)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    table = customTableView()
    table.resize(600, 300)
    table.show()
    sys.exit(app.exec_())


'''