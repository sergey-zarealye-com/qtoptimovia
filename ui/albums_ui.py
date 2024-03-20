from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QTreeView, QSizePolicy
from PySide6.QtGui import QStandardItemModel
from models.albums import AlbumsModel

class AlbumsUI:

    def setup_ui(self, win: QWidget, col: int) -> None:
        """Set up ui."""
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            layout.addWidget(QLabel('<h2>Albums</h2>'))
            tree = QTreeView()
            layout.addWidget(tree)
            root_model = QStandardItemModel()
            tree.setModel(root_model)
            tree.model().setHorizontalHeaderLabels([''])
            AlbumsModel.fill_model_from_dict(root_model.invisibleRootItem(), AlbumsModel.albums_tree)
            tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        elif col == 1:
            layout.addWidget(QLabel('<h2>Videos</h2>'))
        elif col == 2:
            layout.addWidget(QLabel('<h2>Scenes</h2>'))

        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(widget_container)