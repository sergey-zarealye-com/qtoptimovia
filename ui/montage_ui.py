from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QAction, QTableView, QToolBar, QHeaderView, QListWidget, \
    QTabWidget, QLineEdit, QCheckBox, QDateEdit, QPlainTextEdit, QGroupBox, QDialogButtonBox, QPushButton, QHBoxLayout, \
    QAbstractItemView

from models.montage_headers import MontageHeadersModel
from models.montage_materials import MontageMaterialsModel
from models.scenes import SceneModel
from models.sql.files import FilesModelSQL
from models.sql.montage_headers import MontageHeadersModelSQL
from ui.common import get_fixed_spacer, setup_scenes_view, get_horizontal_spacer, setup_search_form_layout
from ui.ui_base import UiBase


class MontageUI(UiBase):

    def __init__(self):
        super().__init__()
        self.montage_headers_model = MontageHeadersModel()
        self.montage_materials_view = QTableView()
        self.montage_materials_model = MontageMaterialsModel(self, 3, self.montage_materials_view)
        self.montage_materials_toolbar = QToolBar()

        self.montage_params_toolbar = QToolBar()
        self.clear_montage_action = QAction(QIcon("icons/cross-button.png"), "Clear")

        # Plot form fields
        imported_at_min, imported_at_max, created_at_min, created_at_max = FilesModelSQL.get_minmax_dates()
        self.description = QPlainTextEdit()
        self.include_horizontal = QCheckBox()
        self.include_vertical = QCheckBox()
        self.include_horizontal.setChecked(True)
        self.include_vertical.setChecked(True)
        self.created_at_from = QDateEdit(created_at_min)
        self.created_at_to = QDateEdit(created_at_max)
        self.imported_at_from = QDateEdit(imported_at_min)
        self.imported_at_to = QDateEdit(imported_at_max)

        #Selected form fields
        self.selected_video_files_list = QListWidget()

        #Footage group buttons
        self.load_footage_button = QPushButton("Load footage")
        self.remove_footage_button = QPushButton("Remove")

    def setup_ui(self, win: QWidget, col: int) -> None:
        """Set up ui."""
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            self.setup_montage_params_toolbar()
            layout.setMenuBar(self.montage_params_toolbar)
            layout.addWidget(self.setup_params_ui(win))
        elif col == 1:
            self.setup_montage_materials_toolbar()
            layout.setMenuBar(self.montage_materials_toolbar)
            setup_scenes_view(self.montage_materials_view, self.montage_materials_model)
            vheader = self.montage_materials_view.verticalHeader()
            vheader.setSectionResizeMode(QHeaderView.Fixed)
            vheader.setDefaultSectionSize(SceneModel.THUMB_HEIGHT)
            layout.addWidget(self.montage_materials_view)
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
        self.montage_params_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.montage_params_toolbar.addWidget(get_fixed_spacer())
        self.montage_params_toolbar.addWidget(QLabel('<h3>Video Editor</h3>'))
        self.montage_params_toolbar.addWidget(get_horizontal_spacer())
        self.montage_params_toolbar.addAction(self.clear_montage_action)
        self.montage_params_toolbar.setIconSize(QSize(16, 16))
        self.montage_params_toolbar.setMovable(False)

    def setup_params_ui(self, win):
        layout = QVBoxLayout()

        ## Footage group box
        footage_group = QGroupBox("Footage")
        footage_layout = QVBoxLayout()
        selected_tab = self.setup_selected_tab(win)
        plot_tab = setup_search_form_layout(self, win)
        tabs = QTabWidget()
        tabs.addTab(selected_tab, 'Selected')
        tabs.addTab(plot_tab, 'Plot')
        footage_layout.addWidget(tabs)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.remove_footage_button)
        buttons_layout.addWidget(self.load_footage_button)
        buttons_layout.insertStretch(1,0)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        footage_layout.addWidget(buttons_widget)

        footage_group.setLayout(footage_layout)

        ## Cut group box
        params_group = QGroupBox("Cut")
        params_layout = QVBoxLayout()
        params_layout.addWidget(QLabel("Cut parameters go here"))
        params_group.setLayout(params_layout)

        ## Production group box
        production_group = QGroupBox("Production")
        production_layout = QVBoxLayout()
        production_layout.addWidget(QLabel("Production parameters go here"))
        production_group.setLayout(production_layout)

        layout.addWidget(footage_group)
        layout.addWidget(params_group)
        layout.addWidget(production_group)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def setup_selected_tab(self, win):
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Video files selected for montage'))
        layout.addWidget(self.selected_video_files_list)
        self.selected_video_files_list.setSelectionMode(QAbstractItemView.MultiSelection)
        widget = QWidget()
        widget.setLayout(layout)
        return widget
