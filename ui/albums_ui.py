from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QSizePolicy, QAbstractItemView, QTableView, \
    QHeaderView, QToolBar, QAction
from models.albums import AlbumsModel
from models.files import FilesModel
from models.scenes import SceneModel
from ui.common import setup_scenes_view, setup_files_list_view, get_horizontal_spacer, get_fixed_spacer, \
    c_setup_video_files_toolbar, c_setup_scenes_toolbar


class AlbumsUI:

    def __init__(self):
        self.tree_model = AlbumsModel()
        self.tree = QTreeView()
        self.files_list_view = QTableView()
        self.files_list_model = FilesModel(0)
        self.scenes_list_view = QTableView()
        self.scenes_list_model = SceneModel(self)

        self.albums_toolbar = QToolBar()
        self.add_album_action = QAction(QIcon("icons/plus-button.png"), "Add album")
        self.del_album_action = QAction(QIcon("icons/minus-button.png"), "Remove album")

        self.video_files_toolbar = QToolBar()
        self.to_album_action = QAction(QIcon("icons/folder--arrow.png"), "Add video to album")
        self.to_montage_action = QAction(QIcon("icons/clapperboard--plus.png"), "Add video to montage")

        self.scenes_toolbar = QToolBar()
        self.play_action = QAction(QIcon("icons/film--arrow.png"), "Play video")

    def setup_ui(self, win: QWidget, col: int) -> None:
        """Set up ui."""
        widget_container = QWidget()



        layout = QVBoxLayout(widget_container)

        if col == 0:
            self.setup_alb_toolbar()
            layout.setMenuBar(self.albums_toolbar)
            layout.addWidget(self.tree)
            self.tree.setModel(self.tree_model)
            self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.tree.setHeaderHidden(True)
            self.tree.setColumnHidden(1, True)
            self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
            self.tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
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

    def setup_alb_toolbar(self):
        self.albums_toolbar.addWidget(get_fixed_spacer())
        self.albums_toolbar.addWidget(QLabel('<h3>Albums</h3>'))
        self.albums_toolbar.addWidget(get_horizontal_spacer())
        self.albums_toolbar.addAction(self.add_album_action)
        self.albums_toolbar.addAction(self.del_album_action)
        self.albums_toolbar.addWidget(get_fixed_spacer())
        self.albums_toolbar.setIconSize(QSize(16, 16))
        self.albums_toolbar.setMovable(False)
        self.add_album_action.setDisabled(True)
        self.del_album_action.setDisabled(True)

    def setup_video_files_toolbar(self):
        c_setup_video_files_toolbar(self.video_files_toolbar, self.to_album_action, self.to_montage_action)

    def setup_scenes_toolbar(self):
        c_setup_scenes_toolbar(self.scenes_toolbar, self.play_action)

