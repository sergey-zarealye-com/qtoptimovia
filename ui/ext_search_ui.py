from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                             QFormLayout, QLineEdit, QGroupBox, QSizePolicy,
                             QDateEdit, QCheckBox, QToolBar, QAction, QTableView)
from PyQt5.QtCore import QDate, Qt, QSize
import pyqtgraph as pg

from models.files import FilesModel
from models.scenes import SceneModel
from models.search_results import SearchResult
from ui.common import get_fixed_spacer, get_horizontal_spacer, c_setup_scenes_toolbar, setup_scenes_view


class ExtSearchUI:
    def __init__(self):

        imported_at_min, imported_at_max, created_at_min, created_at_max = FilesModel.get_minmax_dates()

        # Form fields
        self.description = QLineEdit()
        self.include_horizontal = QCheckBox()
        self.include_vertical = QCheckBox()
        self.include_horizontal.setChecked(True)
        self.include_vertical.setChecked(True)
        self.created_at_from = QDateEdit(created_at_min)
        self.created_at_to = QDateEdit(created_at_max)
        self.imported_at_from = QDateEdit(imported_at_min)
        self.imported_at_to = QDateEdit(imported_at_max)

        #Views
        self.search_results_view = QTableView()
        self.search_results_model = SearchResult(self, 4)
        self.scenes_list_view = QTableView()
        self.scenes_list_model = SceneModel(self)

        self.search_form_toolbar = QToolBar()
        self.search_action = QAction(QIcon("icons/magnifier-zoom.png"), "Search")

        self.search_results_toolbar = QToolBar()
        self.to_montage_action = QAction(QIcon("icons/clapperboard--plus.png"), "Add to montage")
        self.goback_action = QAction(QIcon("icons/arrow-180.png"), "Back")
        self.gofwd_action = QAction(QIcon("icons/arrow.png"), "Forward")
        self.pager = QLabel('1')

        self.scenes_toolbar = QToolBar()
        self.play_action = QAction(QIcon("icons/film--arrow.png"), "Play video")
        self.info_action = QAction(QIcon("icons/information.png"), "Info")

        self.plot_graph = pg.PlotWidget()


    def setup_ui(self, win: QWidget, col: int) -> None:
        """Set up ui."""
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            self.setup_search_form_toolbar()
            layout.setMenuBar(self.search_form_toolbar)
            form_layout = QFormLayout()
            form_layout.addRow(win.tr("Description:"), self.description)
            form_layout.addRow(QLabel(win.tr("Filming date")))
            form_layout.addRow(win.tr("From:"), self.created_at_from)
            form_layout.addRow(win.tr("To:"), self.created_at_to)
            form_layout.addRow(QLabel(win.tr("Import date")))
            form_layout.addRow(win.tr("From:"), self.imported_at_from)
            form_layout.addRow(win.tr("To:"), self.imported_at_to)
            form_layout.addRow(win.tr("Horizontal:"), self.include_horizontal)
            form_layout.addRow(win.tr("Vertical:"), self.include_vertical)

            groupBox = QGroupBox()
            groupBox.setLayout(form_layout)
            groupBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

            layout.addWidget(groupBox)

            self.plot_graph.showGrid(x=True, y=True)
            layout.addWidget(self.plot_graph)


        elif col == 1:
            self.setup_search_results_toolbar()
            layout.setMenuBar(self.search_results_toolbar)
            setup_scenes_view(self.search_results_view, self.search_results_model)
            layout.addWidget(self.search_results_view)
        elif col == 2:
            self.setup_scenes_toolbar()
            layout.setMenuBar(self.scenes_toolbar)
            setup_scenes_view(self.scenes_list_view, self.scenes_list_model)
            layout.addWidget(self.scenes_list_view)

        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(widget_container)

    def setup_search_form_toolbar(self):
        self.search_form_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.search_form_toolbar.addWidget(get_fixed_spacer())
        self.search_form_toolbar.addWidget(QLabel('<h3>Search form</h3>'))
        self.search_form_toolbar.addWidget(get_horizontal_spacer())
        self.search_form_toolbar.addAction(self.search_action)
        self.search_form_toolbar.addWidget(get_fixed_spacer())
        self.search_form_toolbar.setIconSize(QSize(16, 16))
        self.search_form_toolbar.setMovable(False)
        self.search_action.setDisabled(False)

    def setup_search_results_toolbar(self):
        self.search_results_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.search_results_toolbar.addWidget(get_fixed_spacer())
        self.goback_action.setDisabled(True)
        self.gofwd_action.setDisabled(True)
        self.goback_action.setText('')
        self.gofwd_action.setText('')
        self.goback_action.setToolTip('Previous page')
        self.gofwd_action.setToolTip('Next page')
        self.pager.setFixedWidth(20)
        self.search_results_toolbar.addAction(self.goback_action)
        self.search_results_toolbar.addWidget(self.pager)
        self.search_results_toolbar.addAction(self.gofwd_action)
        self.search_results_toolbar.addWidget(get_horizontal_spacer())
        self.search_results_toolbar.addAction(self.to_montage_action)
        self.search_results_toolbar.addWidget(get_fixed_spacer())
        self.search_results_toolbar.setIconSize(QSize(16, 16))
        self.search_results_toolbar.setMovable(False)
        self.to_montage_action.setDisabled(True)

    def setup_scenes_toolbar(self):
        c_setup_scenes_toolbar(self.scenes_toolbar, self.info_action, self.play_action)
