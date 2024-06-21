from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QAction, QTableView, QToolBar, QHeaderView, QListWidget

from models.montage_headers import MontageHeadersModel
from models.montage_materials import MontageMaterialsModel
from models.scenes import SceneModel
from models.sql.montage_headers import MontageHeadersModelSQL
from ui.common import get_fixed_spacer, setup_scenes_view, get_horizontal_spacer
from ui.ui_base import UiBase


class MontageUI(UiBase):

    def __init__(self):
        super().__init__()
        self.montage_headers_model = MontageHeadersModel()
        self.montage_headers_widget = QListWidget()

        self.montage_materials_view = QTableView()
        self.montage_materials_model = MontageMaterialsModel(self, 3, self.montage_materials_view)
        self.montage_materials_toolbar = QToolBar()

        self.montage_params_toolbar = QToolBar()
        self.clear_montage_action = QAction(QIcon("icons/cross-button.png"), "Clear")

    def setup_ui(self, win: QWidget, col: int) -> None:
        """Set up ui."""
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            self.setup_montage_params_toolbar()
            layout.setMenuBar(self.montage_params_toolbar)
            self.setup_params_ui()
        elif col == 1:
            self.setup_montage_materials_toolbar()
            layout.setMenuBar(self.montage_materials_toolbar)
            setup_scenes_view(self.montage_materials_view, self.montage_materials_model)
            vheader = self.montage_materials_view.verticalHeader()
            vheader.setSectionResizeMode(QHeaderView.Fixed)
            vheader.setDefaultSectionSize(SceneModel.THUMB_HEIGHT)
            layout.addWidget(self.montage_materials_view)
            self.montage_materials_model.set_results()
        elif col == 2:
            layout.addWidget(QLabel('<h3>Storyboard</h3>'))

        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(widget_container)

    def setup_montage_materials_toolbar(self):
        self.montage_materials_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.montage_materials_toolbar.addWidget(get_fixed_spacer())
        self.montage_materials_toolbar.addWidget(QLabel('<h3>Footage</h3>'))
        self.montage_materials_toolbar.setIconSize(QSize(16, 16))
        self.montage_materials_toolbar.setMovable(False)

    def setup_montage_params_toolbar(self):
        return
        self.montage_params_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.montage_params_toolbar.addWidget(get_fixed_spacer())
        self.montage_params_toolbar.addWidget(QLabel('<h3>Montage</h3>'))
        self.albums_toolbar.addWidget(get_horizontal_spacer())
        self.albums_toolbar.addAction(self.clear_montage_action)
        self.montage_params_toolbar.setIconSize(QSize(16, 16))
        self.montage_params_toolbar.setMovable(False)

    def setup_params_ui(self):
        return
        videos = MontageHeadersModelSQL.get_videos()
        self.montage_headers_widget = QListWidget()
        self.montage_headers_widget.insertItem(0, [o.description for o in videos])