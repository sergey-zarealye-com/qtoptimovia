from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDialog, QDialogButtonBox, QTabWidget, QLineEdit, QComboBox, \
    QFormLayout, QSizePolicy, QPushButton, QTreeView, QAbstractItemView, QTableView, QHeaderView

from models.preferences.MontageAlbumsListModel import MontageAlbumsListModel
from ui.windows.vertical_tabbar import VerticalTabWidget


class PreferencesWindow(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
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

        self.montage_albums_list_model = MontageAlbumsListModel()
        self.montage_albums_list = QTableView()

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

        self.main_window.managed_settings.add_handler('num_cpu_threads', self.num_cpu_threads)
        self.main_window.managed_settings.add_handler('num_gpu_threads', self.num_gpu_threads)

    def general_tab(self):
        self.num_cpu_threads.setValidator(QIntValidator(1, QThread.idealThreadCount(), self))
        self.num_gpu_threads.setValidator(QIntValidator(1, 8, self))
        form_layout = QFormLayout()
        form_layout.addRow('Threads number', self.num_cpu_threads)
        form_layout.addRow('AI threads number', self.num_gpu_threads)
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
        self.montage_albums_list.setModel(self.montage_albums_list_model)
        self.montage_albums_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        horizontal_header = self.montage_albums_list.horizontalHeader()
        vertical_header = self.montage_albums_list.verticalHeader()
        horizontal_header.setSectionResizeMode(QHeaderView.Interactive)
        vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        horizontal_header.setStretchLastSection(True)
        vertical_header.hide()

        for i, f in enumerate(self.montage_albums_list_model.fields):
            if f not in MontageAlbumsListModel.COLUMNS:
                self.montage_albums_list.setColumnHidden(i, True)

        layout = QVBoxLayout()
        layout.addWidget(self.montage_albums_list)
        groupBox = QWidget()
        groupBox.setLayout(layout)
        groupBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        return groupBox
