from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTreeView,
                             QSizePolicy, QTableView, QApplication,
                             QHeaderView, QStyledItemDelegate, QStyleOptionProgressBar, QStyle)
from PyQt5.QtCore import Qt, QSize

from models.files import FilesModel
from models.scenes import SceneModel
from ui.common import scenes_view, files_list_view


class FilesUI:
    def __init__(self):
        self.tree = QTreeView()
        self.files_list_view = QTableView()
        self.files_list_model = FilesModel(1)
        self.scenes_list_view = QTableView()
        self.scenes_list_model = SceneModel()

    def setup_ui(self, win: QWidget, col: int) -> None:
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            layout.addWidget(QLabel('<h3>Local files</h3>'))
            self.tree.setModel(self.files_list_model.fs_model)
            layout.addWidget(self.tree)
            self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.tree.setColumnWidth(0, 200)
        elif col == 1:
            layout.addWidget(QLabel('<h3>Imported videos</h3>'))
            files_list_view(self.files_list_view, self.files_list_model)
            self.files_list_view.setModel(self.files_list_model)
            layout.addWidget(self.files_list_view)
        elif col == 2:
            layout.addWidget(QLabel('<h3>Scenes</h3>'))
            scenes_view(self.scenes_list_view, self.scenes_list_model)
            layout.addWidget(self.scenes_list_view)

        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(widget_container)

