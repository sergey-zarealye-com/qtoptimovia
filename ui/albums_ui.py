from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QSizePolicy, QAbstractItemView, QTableView, \
    QHeaderView
from models.albums import AlbumsModel
from models.files import FilesModel
from models.scenes import SceneModel
from ui.common import scenes_view, files_list_view


class AlbumsUI:

    def __init__(self):
        self.tree_model = AlbumsModel()
        self.tree = QTreeView()
        self.files_list_view = QTableView()
        self.files_list_model = FilesModel(0)
        self.scenes_list_view = QTableView()
        self.scenes_list_model = SceneModel()

    def setup_ui(self, win: QWidget, col: int) -> None:
        """Set up ui."""
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            layout.addWidget(QLabel('<h3>Albums</h3>'))
            layout.addWidget(self.tree)
            self.tree.setModel(self.tree_model)
            self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.tree.setHeaderHidden(True)
            self.tree.setColumnHidden(1, True)
            self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
            self.tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        elif col == 1:
            layout.addWidget(QLabel('<h3>Videos</h3>'))
            files_list_view(self.files_list_view, self.files_list_model)
            layout.addWidget(self.files_list_view)
        elif col == 2:
            layout.addWidget(QLabel('<h3>Scenes</h3>'))
            scenes_view(self.scenes_list_view, self.scenes_list_model)
            layout.addWidget(self.scenes_list_view)

        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(widget_container)