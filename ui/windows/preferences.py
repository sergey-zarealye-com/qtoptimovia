from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QDialog, QDialogButtonBox, QTabWidget, QLineEdit, QComboBox, \
    QFormLayout, QGroupBox, QSizePolicy, QPushButton
from PyQt5 import QtCore

from ui.windows.vertical_tabbar import VerticalTabWidget
import qtmodern.styles
import qtmodern.windows

class PreferencesWindow(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.theme_selector = QComboBox()
        self.num_cpu_threads = QLineEdit()
        self.num_gpu_threads = QLineEdit()
        self.reindex_button = QPushButton('Start...')

        self.main_window = main_window
        geometry = self.main_window.size()
        self.resize(int(geometry.width() * 0.6), int(geometry.height() * 0.6))

        self.setWindowTitle("Preferences")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        tabs = VerticalTabWidget()
        tabs.setTabPosition(QTabWidget.West)
        tabs.setMovable(False)
        tabs.setDocumentMode(False)
        tabs.addTab(self.general_tab(), 'General')
        tabs.addTab(self.archive_tab(), 'Archive')
        tabs.addTab(self.index_tab(), 'Indexing')
        tabs.addTab(self.montage_tab(), 'Montage')

        self.layout.addWidget(tabs)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def general_tab(self):
        self.num_cpu_threads.setValidator(QIntValidator(1, QThread.idealThreadCount(), self))
        self.num_gpu_threads.setValidator(QIntValidator(1, 8, self))
        self.theme_selector.addItems(['Light', 'Dark'])
        form_layout = QFormLayout()
        form_layout.addRow('Threads number', self.num_cpu_threads)
        form_layout.addRow('AI threads number', self.num_gpu_threads)
        form_layout.addRow('UI theme', self.theme_selector)
        groupBox = QWidget()
        groupBox.setLayout(form_layout)
        groupBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        return groupBox

    def archive_tab(self):
        form_layout = QFormLayout()
        form_layout.addRow('Some settings', QLineEdit())
        groupBox = QWidget()
        groupBox.setLayout(form_layout)
        groupBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        return groupBox

    def index_tab(self):
        form_layout = QFormLayout()
        form_layout.addRow('Reindex for search', self.reindex_button)
        groupBox = QWidget()
        groupBox.setLayout(form_layout)
        groupBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.reindex_button.clicked.connect(self.main_window.rebuild_scenes_index)
        return groupBox

    def montage_tab(self):
        form_layout = QFormLayout()
        form_layout.addRow('Some settings', QLineEdit())
        groupBox = QWidget()
        groupBox.setLayout(form_layout)
        groupBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        return groupBox
