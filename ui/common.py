from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QSizePolicy, QHeaderView, QStyledItemDelegate, QStyleOptionProgressBar, QStyle,
                             QToolButton, QLabel, QApplication)

from models.files import FilesModel
from models.scenes import SceneModel
import datetime as dt


class ProgressDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        progress = index.data(Qt.DisplayRole)
        if type(progress) != str and progress < 100:
            opt = QStyleOptionProgressBar()
            opt.rect = option.rect
            opt.minimum = 0
            opt.maximum = 100
            opt.progress = int(progress)
            QApplication.style().drawControl(QStyle.CE_ProgressBar, opt, painter)
        else:
            super().paint(painter, option, index)


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
    horizontal_header.setStretchLastSection(True)
    horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)

    horizontal_header.swapSections(3,4)
    horizontal_header.swapSections(4,5)
    horizontal_header.swapSections(5,6)
    # horizontal_header.hide()
    vertical_header.hide()

    for i, f in enumerate(model.fields):
        if f not in SceneModel.COLUMNS:
            view.setColumnHidden(i, True)

def c_setup_video_files_toolbar(tb, *actions):
    tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    tb.addWidget(get_fixed_spacer())
    tb.addWidget(QLabel('<h3>Videos</h3>'))
    tb.addWidget(get_horizontal_spacer())
    tb.addAction(actions[0])
    tb.addAction(actions[1])
    tb.addWidget(get_fixed_spacer())
    tb.setIconSize(QSize(16, 16))
    tb.setMovable(False)
    actions[0].setDisabled(True)
    actions[1].setDisabled(True)

def c_setup_scenes_toolbar(tb, *actions):
    tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    tb.addWidget(get_fixed_spacer())
    tb.addWidget(QLabel('<h3>Scenes</h3>'))
    tb.addWidget(get_horizontal_spacer())
    for action in actions:
        tb.addAction(action)
        action.setDisabled(True)
    tb.addWidget(get_fixed_spacer())
    tb.setIconSize(QSize(16, 16))
    tb.setMovable(False)

def get_fixed_spacer():
    spacer = QToolButton()
    spacer.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    spacer.setEnabled(False)
    return spacer

def get_vertical_spacer():
    spacer = QToolButton()
    spacer.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
    spacer.setEnabled(False)
    return spacer

def get_horizontal_spacer():
    spacer = QToolButton()
    spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    spacer.setEnabled(False)
    return spacer

def timecode_to_seconds(tc:str):
    hms = tc[:8].split(':')
    t = float(hms[0]) * 3600 + float(hms[1]) * 60 + float(hms[2])
    return t
