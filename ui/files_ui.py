from PyQt5.QtCore import QDir, Qt, QAbstractListModel
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, QTreeView,
                               QSizePolicy, QListView
)

from models.files import FilesModel


class FilesUI:
    def __init__(self):
        self.tree = QTreeView()
        self.model = FilesModel()
        self.files_list_view = QListView()
        self.files_list_model = FilesModel()

    def setup_ui(self, win: QWidget, col: int) -> None:
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            layout.addWidget(QLabel('<h3>Local files</h3>'))
            self.tree.setModel(self.model.fs_model)
            layout.addWidget(self.tree)
            self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        elif col == 1:
            layout.addWidget(QLabel('<h3>VideosFFF</h3>'))
            self.files_list_view.setModel(self.files_list_model)
            self.files_list_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            layout.addWidget(self.files_list_view)
        elif col == 2:
            layout.addWidget(QLabel('<h3>Scenes</h3>'))
        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(widget_container)