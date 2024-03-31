from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTreeView,
                             QSizePolicy, QTableView, QApplication,
                             QHeaderView, QStyledItemDelegate, QStyleOptionProgressBar, QStyle)
from PyQt5.QtCore import Qt, QSize

from models.files import FilesModel


class FilesUI:
    def __init__(self):
        self.tree = QTreeView()
        # self.model = FilesModel()
        self.files_list_view = QTableView()
        self.files_list_model = FilesModel()

    def setup_ui(self, win: QWidget, col: int) -> None:
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            layout.addWidget(QLabel('<h3>Local files</h3>'))
            self.tree.setModel(self.files_list_model.fs_model)
            layout.addWidget(self.tree)
            self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        elif col == 1:
            layout.addWidget(QLabel('<h3>Imported videos</h3>'))
            self.files_list_view.setModel(self.files_list_model)
            self.files_list_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            # QTableView Headers
            horizontal_header = self.files_list_view.horizontalHeader()
            vertical_header = self.files_list_view.verticalHeader()
            horizontal_header.setSectionResizeMode(QHeaderView.Interactive)
            vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
            horizontal_header.setStretchLastSection(True)
            vertical_header.hide()

            proc_delegate = ProgressDelegate(self.files_list_view)
            self.files_list_view.setItemDelegateForColumn(self.files_list_model.get_progress_section(), proc_delegate)

            for i, f in enumerate(self.files_list_model.fields):
                if f not in FilesModel.COLUMNS:
                    self.files_list_view.setColumnHidden(i, True)

            layout.addWidget(self.files_list_view)
        elif col == 2:
            layout.addWidget(QLabel('<h3>Scenes</h3>'))
        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(widget_container)

class ProgressDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        progress = index.data(Qt.DisplayRole)
        opt = QStyleOptionProgressBar()
        opt.rect = option.rect
        opt.minimum = 0
        opt.maximum = 100
        opt.progress = int(progress)
        QApplication.style().drawControl(QStyle.CE_ProgressBar, opt, painter)
