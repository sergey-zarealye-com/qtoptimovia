from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy, QHeaderView, QStyledItemDelegate, QStyleOptionProgressBar, QApplication, \
    QStyle, QLCDNumber

from models.files import FilesModel
from models.scenes import SceneModel

from datetime import timedelta


class ProgressDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        progress = index.data(Qt.DisplayRole)
        opt = QStyleOptionProgressBar()
        opt.rect = option.rect
        opt.minimum = 0
        opt.maximum = 100
        opt.progress = int(progress)
        QApplication.style().drawControl(QStyle.CE_ProgressBar, opt, painter)


def setup_files_list_view(view, model):
    view.setModel(model)
    view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    # QTableView Headers
    horizontal_header = view.horizontalHeader()
    vertical_header = view.verticalHeader()
    horizontal_header.setSectionResizeMode(QHeaderView.Interactive)
    vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
    horizontal_header.setStretchLastSection(True)
    vertical_header.hide()

    proc_delegate = ProgressDelegate(view)
    view.setItemDelegateForColumn(model.get_progress_section(), proc_delegate)

    for i, f in enumerate(model.fields):
        if f not in FilesModel.COLUMNS:
            view.setColumnHidden(i, True)


def setup_scenes_view(view, model):
    view.setModel(model)
    view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    # QTableView Headers
    horizontal_header = view.horizontalHeader()
    vertical_header = view.verticalHeader()
    vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
    horizontal_header.setStretchLastSection(False)
    horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
    horizontal_header.hide()
    vertical_header.hide()

    for i, f in enumerate(model.fields):
        if f not in SceneModel.COLUMNS:
            view.setColumnHidden(i, True)