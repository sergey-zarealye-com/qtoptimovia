import sys

from PyQt5.QtCore import Qt, QSize, QThreadPool, QSettings, QByteArray
from PyQt5.QtGui import QIcon, QPixmapCache
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QAction, QActionGroup,
    QToolBar, QDesktopWidget,
    QWidget, QVBoxLayout, QMenuBar, QToolButton,
    QSplitter, QStackedWidget, QMessageBox, QProgressBar)

from models.sql.files import FilesModelSQL
from modules.pyqtconfig.pyqtconfig import QSettingsManager
from slots.albums import AlbumsSlots
from slots.ext_search import ExtSearchSlots
from slots.files import FilesSlots
from slots.files_import import FilesImportSlots
from slots.montage import MontageSlots
from ui.albums_ui import AlbumsUI
from ui.archive_ui import ArchiveUI
from ui.common import get_vertical_spacer
from ui.ext_search_ui import ExtSearchUI
from ui.files_ui import FilesUI
from ui.montage_ui import MontageUI
from ui.windows.preferences import PreferencesWindow
from workers.metadata_parser import MetadataWorker
from workers.scene_index_builder import SceneIndexBuilder
from workers.video_import import VideoImportWorker


class MainWindowUI:

    def __init__(self, main_win: QMainWindow):

        self.main_win = main_win

        # Actions
        sep1 = QAction()
        sep1.setSeparator(True)
        self.actions_sidebar = (
            QAction(QIcon("icons/blue-folder-horizontal-open.png"), "Your albums"),
            QAction(QIcon("icons/film.png"), "Your local video files"),
            QAction(QIcon("icons/inbox-film.png"), "Your archive storage"),
            QAction(QIcon("icons/magnifier.png"), "Extended search"),
            sep1,
            QAction(QIcon("icons/scissors-blue.png"), "Video montage"),

        )

        action_group_toolbar = QActionGroup(main_win)

        # Widgets
        self.central_window = QMainWindow()
        self.col1_stack_widget = QStackedWidget()
        self.col2_stack_widget = QStackedWidget()
        self.col3_stack_widget = QStackedWidget()

        sidebar = QToolBar("Sidebar")
        menubar = QMenuBar()
        self.tool_btn_settings = QToolButton()
        self.cpu_threads_pb = QProgressBar()
        self.gpu_threads_pb = QProgressBar()

        # Setup Actions
        for action in self.actions_sidebar:
            action.setCheckable(True)
            action_group_toolbar.addAction(action)
        self.actions_sidebar[0].setChecked(True)

        # Setup Widgets
        sidebar.setIconSize(QSize(44, 44))
        sidebar.setMovable(False)
        sidebar.addActions(self.actions_sidebar)
        sidebar.addWidget(get_vertical_spacer())
        sidebar.addWidget(self.tool_btn_settings)

        self.tool_btn_settings.setIcon(QIcon("icons/gear.png"))

        self.pages = []

        for ui in (AlbumsUI, FilesUI, ArchiveUI, MontageUI, ExtSearchUI):
            page = ui()
            for stack_idx, stack_widget in enumerate((self.col1_stack_widget,
                                                      self.col2_stack_widget,
                                                      self.col3_stack_widget)):
                container = QWidget()
                page.setup_ui(container, stack_idx)
                stack_widget.addWidget(container)
            self.pages.append(page)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.col1_stack_widget)
        self.splitter.addWidget(self.col2_stack_widget)
        self.splitter.addWidget(self.col3_stack_widget)

        content_layout.addWidget(self.splitter)
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        self.central_window.setCentralWidget(content_widget)

        # TODO resume paused files import from the position of scene
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_statusbar)
        # self.timer.start(500)

        main_win.setCentralWidget(self.central_window)
        main_win.addToolBar(Qt.ToolBarArea.LeftToolBarArea, sidebar)
        # main_win.setMenuBar(menubar)


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Workers
        self.cpu_threadpool = QThreadPool()
        self.gpu_threadpool = QThreadPool()

        self.ui = MainWindowUI(self)

        self.setWindowTitle("Optimovia")
        geometry = QDesktopWidget().availableGeometry(screen = -1)
        self.resize(int(geometry.width() * 0.8), int(geometry.height() * 0.7))

        self.search_slots = ExtSearchSlots(self)
        self.files_slots = FilesSlots(self)
        self.albums_slots = AlbumsSlots(self)
        self.import_slots = FilesImportSlots(self)
        self.montage_slots = MontageSlots(self)

        for action in self.ui.actions_sidebar:
            action.triggered.connect(self.change_page)

        self.ui.tool_btn_settings.clicked.connect(self.show_preferences_win)

        # Import tool button
        self.ui.pages[1].import_action.triggered.connect(self.import_slots.import_video_files)
        self.ui.pages[1].import_action.triggered.connect(self.init_importing_workers)
        # TODO ui freezes when ffprobe workers are running

        # Files tree signals:
        self.ui.pages[1].tree.expanded.connect(self.files_slots.show_files_in_dir)
        self.ui.pages[1].tree.clicked.connect(self.files_slots.show_files_in_dir)
        self.ui.pages[1].tree.collapsed.connect(self.files_slots.collapse_files)
        self.ui.pages[1].files_list_view.clicked.connect(self.files_slots.show_scenes)
        self.ui.pages[1].find_similar_action.triggered.connect(self.search_slots.find_similar_scenes)
        self.ui.pages[1].to_album_action.triggered.connect(self.files_slots.to_album)
        self.ui.pages[1].to_montage_action.triggered.connect(self.files_slots.to_montage)
        self.ui.pages[1].scenes_list_view.verticalScrollBar().sliderMoved.connect(self.files_slots.slider_moved)
        self.ui.pages[1].scenes_list_view.verticalScrollBar().sliderReleased.connect(self.files_slots.slider_released)

        # Albums tree signals:
        self.ui.pages[0].tree.clicked.connect(self.albums_slots.show_files_for_date)
        self.ui.pages[0].files_list_view.clicked.connect(self.albums_slots.show_scenes)
        self.ui.pages[0].find_similar_action.triggered.connect(self.search_slots.find_similar_scenes)
        self.ui.pages[0].add_album_action.triggered.connect(self.albums_slots.add_album)
        self.ui.pages[0].del_album_action.triggered.connect(self.albums_slots.del_album)
        self.ui.pages[0].to_album_action.triggered.connect(self.albums_slots.to_album)
        self.ui.pages[0].to_montage_action.triggered.connect(self.albums_slots.to_montage)
        self.ui.pages[0].scenes_list_view.verticalScrollBar().sliderMoved.connect(self.albums_slots.slider_moved)
        self.ui.pages[0].scenes_list_view.verticalScrollBar().sliderReleased.connect(self.albums_slots.slider_released)

        # Search form signals:
        self.ui.pages[4].search_action.triggered.connect(self.search_slots.search_scenes)
        self.ui.pages[4].description.returnPressed.connect(self.search_slots.search_scenes)
        self.ui.pages[4].search_results_view.clicked.connect(self.search_slots.show_scenes)
        self.ui.pages[4].goback_action.triggered.connect(self.search_slots.search_results_back)
        self.ui.pages[4].gofwd_action.triggered.connect(self.search_slots.search_results_fwd)
        self.ui.pages[4].find_similar_action.triggered.connect(self.search_slots.find_similar_scenes)
        self.ui.pages[4].find_similar_from_sr_action.triggered.connect(self.search_slots.find_similar_scenes)
        self.ui.pages[4].to_montage_action.triggered.connect(self.search_slots.to_montage)
        self.ui.pages[4].scenes_list_view.verticalScrollBar().sliderMoved.connect(self.search_slots.slider_moved)
        self.ui.pages[4].scenes_list_view.verticalScrollBar().sliderReleased.connect(self.search_slots.slider_released)

        # Montage signals:
        self.ui.pages[3].clear_montage_action.triggered.connect(self.montage_slots.clear_montage_headers)
        self.ui.pages[3].load_footage_button.clicked.connect(self.montage_slots.populate_footage)
        self.ui.pages[3].remove_footage_button.clicked.connect(self.montage_slots.remove_footage)
        self.ui.pages[3].montage_materials_view.doubleClicked.connect(self.montage_slots.toggle_sub_scene)
        self.ui.pages[3].do_cut_button.clicked.connect(self.montage_slots.do_cut)

        # Stubs
        self.video_files_in_directory = None
        self.found_scene_id_list = []

        self.ui.pages[0].scenes_list_model.cpu_threadpool = self.cpu_threadpool
        self.ui.pages[1].scenes_list_model.cpu_threadpool = self.cpu_threadpool
        self.ui.pages[0].files_list_model.cpu_threadpool = self.cpu_threadpool
        self.ui.pages[1].files_list_model.cpu_threadpool = self.cpu_threadpool
        self.ui.pages[4].search_results_model.cpu_threadpool = self.cpu_threadpool
        self.ui.pages[4].scenes_list_model.cpu_threadpool = self.cpu_threadpool
        self.ui.pages[3].montage_materials_model.cpu_threadpool = self.cpu_threadpool
        self.ui.pages[3].storyboard_model.cpu_threadpool = self.cpu_threadpool

        # Dialog windows
        self.preferences_win = None
        self.add_album_dialog = None
        self.to_album_dialog = None

        # Settings
        self.settings = QSettings("SergeyPo", "QtOptimoviaApp")
        self.read_settings()

        self.managed_settings = QSettingsManager()
        self.managed_settings.set_defaults(dict(
            num_cpu_threads='4',
            num_gpu_threads='1',
        ))

        self.cpu_threadpool.setMaxThreadCount(int(self.managed_settings.get('num_cpu_threads')))
        self.gpu_threadpool.setMaxThreadCount(int(self.managed_settings.get('num_gpu_threads')))

    def progress_fn(self, id:int, progress:float):
        FilesModelSQL.update_fields(id, dict(proc_progress=progress))
        self.files_slots.update_layout(self.ui.pages[1].files_list_model)
        self.albums_slots.update_layout(self.ui.pages[0].files_list_model)

    def print_output(self, s):
        print(s)

    # TODO call it automatically by some event
    def rebuild_scenes_index(self):
        worker = SceneIndexBuilder()
        self.cpu_threadpool.start(worker)

    def metadata_thread_complete(self, id:int, metadata:dict):
        fname, _ = FilesModelSQL.select_file_path(id)
        worker = VideoImportWorker(id=id,
                                   video_file_path=fname,
                                   metadata=metadata,
                                )
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.import_slots.import_thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.partial_result.connect(self.import_slots.insert_scene)
        self.gpu_threadpool.start(worker)

    def init_importing_workers(self):
        for id in FilesModelSQL.select_nonstarted_imports():
            fname, _ = FilesModelSQL.select_file_path(id)
            worker = MetadataWorker(id=id,
                                   video_file_path=fname
                                   )
            worker.signals.result.connect(self.print_output)
            worker.signals.finished.connect(self.metadata_thread_complete)
            worker.signals.progress.connect(self.progress_fn)
            worker.signals.metadata_result.connect(self.import_slots.update_metadata)
            self.cpu_threadpool.start(worker)

    def change_page(self) -> None:
        action_name = self.sender().text()  # type: ignore
        if "albums" in action_name:
            index = 0
        elif "files" in action_name:
            index = 1
        elif "archive" in action_name:
            index = 2
        elif "montage" in action_name:
            index = 3
            self.montage_slots.load_video_files_list()
            self.montage_slots.populate_footage()
        else:
            index = 4
        self.ui.col1_stack_widget.setCurrentIndex(index)
        self.ui.col2_stack_widget.setCurrentIndex(index)
        self.ui.col3_stack_widget.setCurrentIndex(index)

    def show_preferences_win(self, checked):

        if self.preferences_win is None:
            self.preferences_win = PreferencesWindow(self)
        self.preferences_win.montage_albums_list_model.update_layout()
        self.preferences_win.open()

    def write_settings(self):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("splitterState", self.ui.splitter.saveState())

    def read_settings(self):
        self.restoreGeometry(self.settings.value("geometry", QByteArray()))
        self.restoreState(self.settings.value("windowState", QByteArray()))
        self.ui.splitter.restoreState(self.settings.value("splitterState", QByteArray()))

    def closeEvent(self, event):
        self.write_settings()
        super().closeEvent(event)
        event.accept()

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == "__main__":
    sys.excepthook = except_hook

    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName("data/optimovia.db")

    QPixmapCache.setCacheLimit(20 * 1024)

    app = QApplication(sys.argv)
    app.setOrganizationName("SergeyPo")
    app.setApplicationName("QtOptimoviaApp")

    if sys.platform == 'darwin':
        app.setStyle("Fusion")

    if not con.open():
        QMessageBox.critical(
            None,
            "Optimovia - Error!",
            "Database Error: %s" % con.lastError().databaseText(),
        )
        sys.exit(1)

    w = MainWindow()
    w.setDocumentMode(True)
    w.show()

    app.exec()
