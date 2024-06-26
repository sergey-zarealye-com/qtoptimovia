from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTreeView,
                             QSizePolicy, QTableView, QToolBar, QAction)

from models.files import FilesModel
from models.scenes import SceneModel
from ui.common import setup_scenes_view, setup_files_list_view, c_setup_video_files_toolbar, c_setup_scenes_toolbar, \
    get_fixed_spacer, get_horizontal_spacer
from ui.ui_base import UiBase


class FilesUI(UiBase):
    def __init__(self):
        super().__init__()
        self.tree = QTreeView()
        self.files_list_view = QTableView()
        self.files_list_model = FilesModel(1)
        self.scenes_list_view = QTableView()
        self.scenes_list_model = SceneModel(self, 1, self.scenes_list_view)

        self.tree_toolbar = QToolBar()
        self.import_action = QAction(QIcon("icons/film--plus.png"), "Import")

        self.video_files_toolbar = QToolBar()
        self.to_album_action = QAction(QIcon("icons/folder--arrow.png"), "To album")
        self.to_montage_action = QAction(QIcon("icons/clapperboard--plus.png"), "To montage")

        self.scenes_toolbar = QToolBar()
        self.play_action = QAction(QIcon("icons/film--arrow.png"), "Play video")
        self.info_action = QAction(QIcon("icons/information.png"), "Info")

        self.setup_context_menu(self.scenes_list_view)
        self.context_index = None

    def setup_ui(self, win: QWidget, col: int) -> None:
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            self.setup_tree_toolbar()
            layout.setMenuBar(self.tree_toolbar)
            self.tree.setModel(self.files_list_model.fs_model)
            layout.addWidget(self.tree)
            self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.tree.setColumnWidth(0, 200)
        elif col == 1:
            self.setup_video_files_toolbar()
            layout.setMenuBar(self.video_files_toolbar)
            setup_files_list_view(self.files_list_view, self.files_list_model)
            layout.addWidget(self.files_list_view)
        elif col == 2:
            self.setup_scenes_toolbar()
            layout.setMenuBar(self.scenes_toolbar)
            setup_scenes_view(self.scenes_list_view, self.scenes_list_model)
            layout.addWidget(self.scenes_list_view)

        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(widget_container)

    def setup_tree_toolbar(self):
        self.tree_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tree_toolbar.addWidget(get_fixed_spacer())
        self.tree_toolbar.addWidget(QLabel('<h3>Your PC</h3>'))
        self.tree_toolbar.addWidget(get_horizontal_spacer())
        self.tree_toolbar.addAction(self.import_action)
        self.tree_toolbar.addWidget(get_fixed_spacer())
        self.tree_toolbar.setIconSize(QSize(16, 16))
        self.tree_toolbar.setMovable(False)
        self.import_action.setDisabled(True)

    def setup_video_files_toolbar(self):
        c_setup_video_files_toolbar(self.video_files_toolbar, self.to_album_action, self.to_montage_action)

    def setup_scenes_toolbar(self):
        c_setup_scenes_toolbar(self.scenes_toolbar, self.info_action, self.play_action)

