from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QSizePolicy, QAbstractItemView, QTableView, \
    QHeaderView
from models.albums import AlbumsModel
from models.files import FilesModel
from ui.files_ui import ProgressDelegate


class AlbumsUI:

    def __init__(self):
        self.tree = QTreeView()
        self.files_list_view = QTableView()
        self.files_list_model = FilesModel()

    def setup_ui(self, win: QWidget, col: int) -> None:
        """Set up ui."""
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            layout.addWidget(QLabel('<h3>Albums</h3>'))
            layout.addWidget(self.tree)
            self.tree_model = AlbumsModel()
            self.tree.setModel(self.tree_model)
            self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.tree.setHeaderHidden(True)
            self.tree.setColumnHidden(1, True)
            self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
            self.tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        elif col == 1:
            layout.addWidget(QLabel('<h3>Videos</h3>'))
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