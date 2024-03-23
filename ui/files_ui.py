from PySide6.QtCore import QDir
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QTreeView, QSizePolicy
from models.files import FilesModel

class FilesUI:
    def __init__(self):
        self.tree = QTreeView()

    def setup_ui(self, win: QWidget, col: int) -> None:
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            layout.addWidget(QLabel('<h2>Local files</h2>'))
            self.model = FilesModel()
            self.tree.setModel(self.model.get_model())
            layout.addWidget(self.tree)
            self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            # self.tree.expanded.connect(lambda i: print(i))
        elif col == 1:
            layout.addWidget(QLabel('<h2>Videos</h2>'))
        elif col == 2:
            layout.addWidget(QLabel('<h2>Scenes</h2>'))
        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(widget_container)