import sys, os

from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QAction, QActionGroup,
    QLabel, QToolBar, QStatusBar, QDesktopWidget,
    QWidget, QHBoxLayout, QVBoxLayout, QMenuBar, QToolButton,
    QSizePolicy, QLineEdit, QSplitter, QStackedWidget, QMessageBox, QProgressBar)
from PyQt5.QtGui import QIcon, QPixmapCache
from PyQt5.QtCore import Qt, QSize, QModelIndex, QThreadPool, QTimer
from PyQt5.QtSql import QSqlDatabase

from models.albums import AlbumsModel
from models.scenes import SceneModel
from ui.albums_ui import AlbumsUI
from ui.common import get_fixed_spacer, get_vertical_spacer, get_horizontal_spacer
from ui.files_ui import FilesUI
from ui.archive_ui import ArchiveUI
from ui.montage_ui import MontageUI
from ui.ext_search_ui import ExtSearchUI
from models.files import FilesModel
from workers.metadata_parser import MetadataWorker
from workers.video_import import VideoImportWorker

IS_USE_QDARKTHEME = False
if IS_USE_QDARKTHEME:
    import qdarktheme
else:
    import qtmodern.styles
    import qtmodern.windows


class MainWindowUI:

    def __init__(self, main_win: QMainWindow):

        self.main_win = main_win

        # Actions
        sep1 = QAction()
        sep1.setSeparator(True)
        self.actions_sidebar = (
            QAction(QIcon("icons/command.svg"), "Your albums"),
            QAction(QIcon("icons/disk.svg"), "Your local video files"),
            QAction(QIcon("icons/binoculars.svg"), "Your archive storage"),
            QAction(QIcon("icons/clip.svg"), "Video montage"),
            sep1,
            QAction(QIcon("icons/find.svg"), "Extended search"),
        )

        action_group_toolbar = QActionGroup(main_win)

        # Widgets
        self.central_window = QMainWindow()
        self.col1_stack_widget = QStackedWidget()
        self.col2_stack_widget = QStackedWidget()
        self.col3_stack_widget = QStackedWidget()

        sidebar = QToolBar("Sidebar")
        self.statusbar = QStatusBar()
        menubar = QMenuBar()
        tool_btn_settings = QToolButton()

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
        sidebar.addWidget(tool_btn_settings)

        tool_btn_settings.setIcon(QIcon("icons/hammer.svg"))

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
        # content_layout.addWidget(self.toolbar)

        splitter = QSplitter()
        splitter.addWidget(self.col1_stack_widget)
        splitter.addWidget(self.col2_stack_widget)
        splitter.addWidget(self.col3_stack_widget)

        content_layout.addWidget(splitter)
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        self.central_window.setCentralWidget(content_widget)

        layout = QHBoxLayout()
        sb_widget = QWidget()
        sb_widget.setLayout(layout)

        self.timeit_label = QLabel('Timeit:')

        self.ffmpeg_threads_pb = QProgressBar()
        self.ffmpeg_threads_pb.setMinimum(0)
        self.ffmpeg_threads_pb.setTextVisible(False)
        self.ffmpeg_threads_pb.setFixedHeight(5)
        self.ffmpeg_threads_pb.setFixedWidth(100)

        layout.addWidget(self.ffmpeg_threads_pb)
        layout.addWidget(self.timeit_label)
        self.statusbar.addWidget(sb_widget)

        # TODO resume paused files import from the position of scene
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_statusbar)
        self.timer.start(500)

        main_win.setCentralWidget(self.central_window)
        main_win.addToolBar(Qt.ToolBarArea.LeftToolBarArea, sidebar)
        main_win.setMenuBar(menubar)
        main_win.setStatusBar(self.statusbar)

    def update_statusbar(self):
        self.ffmpeg_threads_pb.setMaximum(self.main_win.ffmpeg_threadpool.maxThreadCount())
        cnt = self.main_win.ffmpeg_threadpool.activeThreadCount()
        self.ffmpeg_threads_pb.setValue(cnt)
        if self.pages[0].scenes_list_model.timeit_cnt > 0:
            mtime = self.pages[0].scenes_list_model.time_sum / self.pages[0].scenes_list_model.timeit_cnt
            self.timeit_label.setText(f"Timeit: {mtime / 1e6:.2f}")


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = MainWindowUI(self)

        self.setWindowTitle("Optimovia")
        geometry = QDesktopWidget().availableGeometry(screen = -1)
        self.resize(int(geometry.width() * 0.8), int(geometry.height() * 0.7))

        for action in self.ui.actions_sidebar:
            action.triggered.connect(self.change_page)

        # Import tool button
        self.ui.pages[1].import_action.triggered.connect(self.import_video_files)
        self.ui.pages[1].import_action.triggered.connect(self.init_importing_workers)

        # Files tree signals:
        self.ui.pages[1].tree.expanded.connect(self.show_files_in_dir)
        self.ui.pages[1].tree.clicked.connect(self.show_files_in_dir)
        self.ui.pages[1].tree.collapsed.connect(self.collapse_files)
        self.ui.pages[1].files_list_view.clicked.connect(self.show_scenes)

        # Albums tree signals:
        self.ui.pages[0].tree.clicked.connect(self.show_files_for_date)
        self.ui.pages[0].files_list_view.clicked.connect(self.show_scenes)

        # Stubs
        self.video_files_in_directory = None

        # Workers
        self.ffmpeg_threadpool = QThreadPool()
        self.ffmpeg_threadpool.setMaxThreadCount(4) #4
        self.gpu_threadpool = QThreadPool()
        self.gpu_threadpool.setMaxThreadCount(1) #1

        self.ui.pages[0].scenes_list_model.ffmpeg_threadpool = self.ffmpeg_threadpool
        self.ui.pages[1].scenes_list_model.ffmpeg_threadpool = self.ffmpeg_threadpool

    def progress_fn(self, id:int, progress:float):
        FilesModel.update_fields(id, dict(proc_progress=progress))
        self.update_layout(self.ui.pages[0].files_list_model) #
        self.update_layout(self.ui.pages[1].files_list_model)

    def print_output(self, s):
        print(s)

    def update_metadata(self, id:int, metadata:dict):
        FilesModel.update_fields(id, metadata)
        self.update_layout(self.ui.pages[1].files_list_model)

    def insert_scene(self, video_file_id:int, obj:dict):
        scene_start = obj['scene_start']
        scene_end = obj['scene_end']
        scene_embedding = obj['scene_embedding']
        scene_id = SceneModel.insert(video_file_id, scene_start, scene_end, scene_embedding)

    def metadata_thread_complete(self, id:int, metadata:dict):
        fname, _ = FilesModel.select_file_path(id)
        worker = VideoImportWorker(id=id,
                                   video_file_path=fname,
                                   metadata=metadata,
                                )
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.import_thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.partial_result.connect(self.insert_scene)
        self.gpu_threadpool.start(worker)

    def import_thread_complete(self, id: int):
        print('finished import id:', id)
        self.ui.pages[0].tree_model = AlbumsModel()
        self.ui.pages[0].tree.setModel(self.ui.pages[0].tree_model)

    def init_importing_workers(self):
        for id in FilesModel.select_nonstarted_imports():
            fname, _ = FilesModel.select_file_path(id)
            worker = MetadataWorker(id=id,
                                   video_file_path=fname
                                   )
            worker.signals.result.connect(self.print_output)
            worker.signals.finished.connect(self.metadata_thread_complete)
            worker.signals.progress.connect(self.progress_fn)
            worker.signals.metadata_result.connect(self.update_metadata)
            self.ffmpeg_threadpool.start(worker)

    def update_layout(self, model, set_filter=None):
        if set_filter != None:
            model.db_model.setFilter(set_filter)
        model.db_model.select()
        model.layoutChanged.emit()

    def show_scenes(self, signal):
        video_file_id_idx = signal.siblingAtColumn(0)
        video_file_id = signal.model().db_model.data(video_file_id_idx)
        page = signal.model().page
        self.update_layout(self.ui.pages[page].scenes_list_model, set_filter=f"video_file_id='{video_file_id}'")

    def import_video_files(self, signal):
        FilesModel.import_files(self.video_files_in_directory)
        self.update_layout(self.ui.pages[1].files_list_model)

    def show_files_in_dir(self, signal):
        if self.ui.pages[1].tree.isExpanded(signal):
            dir_path = self.ui.pages[1].files_list_model.get_file_path(signal)
            self.video_files_in_directory = self.ui.pages[1].files_list_model.get_video_files(dir_path)
            self.update_layout(self.ui.pages[1].files_list_model, set_filter=f"import_dir='{dir_path}'")
            self.update_layout(self.ui.pages[1].scenes_list_model, set_filter="0")
            # Import tool button
            self.ui.pages[1].import_action.setEnabled(len(self.video_files_in_directory) > 0)
        else:
            self.collapse_files(signal)
            selected_path = self.ui.pages[1].files_list_model.fs_model.filePath(signal)
            if os.path.isfile(selected_path):
                dir_path, file_name = os.path.split(selected_path)
                self.video_files_in_directory = [selected_path]
                self.update_layout(self.ui.pages[1].files_list_model, set_filter=f"import_dir='{dir_path}' AND import_name='{file_name}'")
                self.update_layout(self.ui.pages[1].scenes_list_model, set_filter="0")
                self.ui.pages[1].import_action.setEnabled(True)

    def show_files_for_date(self, signal):
        r = signal.row()
        c = signal.column()
        p = signal.parent()
        rr = self.ui.pages[0].tree_model.index(r, c+1, p)
        date = self.ui.pages[0].tree_model.itemFromIndex(rr).text()
        date = date.split()
        if len(date) == 3:
            field = date[0]
            year = int(date[1])
            month = int(date[2])
            self.update_layout(self.ui.pages[0].files_list_model, set_filter=f"strftime('%Y', {field})='{year}' AND strftime('%m', {field})='{month:02d}'")
            self.update_layout(self.ui.pages[0].scenes_list_model, set_filter="0")

    def collapse_files(self, signal):
        # Import tool button
        self.ui.pages[1].import_action.setEnabled(False)
        self.update_layout(self.ui.pages[1].files_list_model, set_filter='0')
        self.update_layout(self.ui.pages[1].scenes_list_model, set_filter="0")

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
        else:
            index = 4
        self.ui.col1_stack_widget.setCurrentIndex(index)
        self.ui.col2_stack_widget.setCurrentIndex(index)
        self.ui.col3_stack_widget.setCurrentIndex(index)


if __name__ == "__main__":
    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName("data/optimovia.db")

    QPixmapCache.setCacheLimit(20 * 1024)

    app = QApplication(sys.argv)

    if IS_USE_QDARKTHEME:
        if sys.platform == 'darwin':
            app.setStyle("Fusion")
        else:
            qdarktheme.setup_theme('auto')

    if not con.open():
        QMessageBox.critical(
            None,
            "Optimovia - Error!",
            "Database Error: %s" % con.lastError().databaseText(),
        )
        sys.exit(1)

    w = MainWindow()

    if IS_USE_QDARKTHEME:
        w.setDocumentMode(True)
        w.show()
    else:
        qtmodern.styles.dark(app)
        mw = qtmodern.windows.ModernWindow(w)
        mw.show()

    app.exec()
