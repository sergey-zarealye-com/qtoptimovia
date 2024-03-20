from PySide6.QtCore import QDir
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFileSystemModel, QTreeView, QSizePolicy


class FilesUI:

    def setup_ui(self, win: QWidget, col: int) -> None:
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            layout.addWidget(QLabel('<h2>Local files</h2>'))
            model = QFileSystemModel()
            model.setRootPath(QDir.currentPath())
            model.setNameFilters(['*.mov', '*.avi', '*.mp4'])
            model.setNameFilterDisables(False)
            tree = QTreeView()
            tree.setModel(model)
            print(tree.sizeHint())
            layout.addWidget(tree)
            tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        elif col == 1:
            layout.addWidget(QLabel('<h2>Videos</h2>'))
        elif col == 2:
            layout.addWidget(QLabel('<h2>Scenes</h2>'))
        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(widget_container)