from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel, QProgressBar, QLayout, QSizePolicy

from ui.common import get_horizontal_spacer


def setup_statusbar(obj):
    layout = QHBoxLayout()
    sb_widget = QWidget()
    sb_widget.setLayout(layout)

    obj.timeit_label = QLabel('Timeit:')

    obj.cpu_threads_pb.setMinimum(0)
    obj.cpu_threads_pb.setMaximum(obj.main_win.cpu_threadpool.maxThreadCount())
    obj.cpu_threads_pb.setTextVisible(False)
    obj.cpu_threads_pb.setFixedHeight(5)
    obj.cpu_threads_pb.setFixedWidth(100)

    obj.gpu_threads_pb.setMinimum(0)
    obj.gpu_threads_pb.setMaximum(obj.main_win.gpu_threadpool.maxThreadCount())
    obj.gpu_threads_pb.setTextVisible(False)
    obj.gpu_threads_pb.setFixedHeight(5)
    obj.gpu_threads_pb.setFixedWidth(100)

    l0 = QLabel()
    l0.setFixedWidth(70)
    l1 = QLabel()
    l1.setPixmap(QPixmap('icons/processor.png'))
    l1.setFixedWidth(16)
    l2 = QLabel()
    l2.setPixmap(QPixmap('icons/burn.png'))
    l2.setFixedWidth(16)
    layout.addWidget(l0)
    layout.addWidget(l1)
    layout.addWidget(obj.cpu_threads_pb)
    layout.addWidget(l2)
    layout.addWidget(obj.gpu_threads_pb)
    layout.addWidget(obj.timeit_label)

    return sb_widget