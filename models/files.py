import os

from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QPixmapCache, QPixmap, QColor
from PyQt5.QtSql import QSqlTableModel

from models.ColoredQFileSystemModel import ColoredQFileSystemModel
from models.base import PixBaseModel
from models.sql.files import FilesModelSQL
from models.sql.scenes import SceneModelSQL
from workers.thumbnails_worker import ThumbnailsWorker


class FilesModel(PixBaseModel):
    FILE_FILTERS = ['*.mov', '*.avi', '*.mp4', '*.mkv']
    FILE_EXTS = ['.mov', '.avi', '.mp4', '.mkv']
    COLUMNS = dict([
        ("description", "Description"),
        ("created_at", "Created at"),
        ("proc_progress", "Processed"),
    ])
    THUMB_HEIGHT = 196#96
    THUMB_WIDTH = 160#96


    def __init__(self, page:int):
        super().__init__()
        self.page = page
        self.fs_model = ColoredQFileSystemModel()
        self.fs_model.setRootPath(QDir.currentPath())
        self.fs_model.setNameFilters(FilesModel.FILE_FILTERS)
        self.fs_model.setNameFilterDisables(False)
        self.fields = FilesModelSQL.setup_db()
        self.selected_dir = None
        self.db_model = QSqlTableModel()
        self.db_model.setTable("video_files")
        self.db_model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.cpu_threadpool = None

    def filename_from_index(self, index):
        video_file_idx = index.siblingAtColumn(0)
        video_file_id = self.db_model.data(video_file_idx)
        fname, _ = FilesModelSQL.select_file_path(video_file_id)
        return fname, video_file_id

    def data(self, index, role):
        row = index.row()
        col= index.column()
        data = self.db_model.data(self.db_model.index(row, col))
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if col == self.get_progress_section() and data >= 100:
                fname, video_file_id = self.filename_from_index(index)
                if fname != None:
                    file_status = ColoredQFileSystemModel.get_file_status(fname)
                    if file_status == ColoredQFileSystemModel.STATUS_MISSING:
                        return "FILE MISSING"
                return ''
            else:
                return data
        if role == Qt.DecorationRole:
            if col == self.get_progress_section():
                if data >= 100:
                    fname, video_file_id = self.filename_from_index(index)
                    if fname != None:
                        file_status = ColoredQFileSystemModel.get_file_status(fname)
                        if file_status == ColoredQFileSystemModel.STATUS_MISSING:
                            return QPixmap('icons/exclamation.png')
                    timestamps = SceneModelSQL.get_thumbnail_timestamp(video_file_id, 1)
                    if len(timestamps):
                        timestamp = timestamps[0]
                        cache_key = f"mini_{video_file_id}_{timestamp:.2f}"
                        pix = QPixmapCache.find(cache_key)
                        if not pix:
                            QPixmapCache.insert(cache_key, QPixmap())
                            worker = ThumbnailsWorker(id=video_file_id,
                                                      ts=timestamp,
                                                      video_file_path=fname,
                                                      cache_key=cache_key,
                                                      )
                            worker.signals.result.connect(self.frame_extracted)
                            self.cpu_threadpool.start(worker)
                        return pix
        if role == Qt.BackgroundColorRole:
            path, video_file_id = self.filename_from_index(index)
            if path != None:
                file_status = ColoredQFileSystemModel.get_file_status(path)
                if file_status == ColoredQFileSystemModel.STATUS_MISSING:
                    return QColor('#ff8a80')

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            col = index.column()
            if col in self.get_editable_columns():
                ok = self.db_model.setData(index, value, role)
                return ok
            else:
                return False
        return True

    def flags(self, index):
        col = index.column()
        if col in self.get_editable_columns():
            return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if self.fields[section] in FilesModel.COLUMNS:
                return FilesModel.COLUMNS[self.fields[section]]
        return super().headerData(section, orientation, role)

    def get_progress_section(self):
        return self.fields.index('proc_progress')
    #
    def get_editable_columns(self):
        return [self.fields.index('description')]



    def get_file_path(self, idx):
        self.selected_dir = self.fs_model.filePath(idx)
        return self.selected_dir

    def get_video_files(self, dir_path):
        files = os.listdir(dir_path)
        return [os.path.join(dir_path, fn) for fn in files
                if os.path.splitext(os.path.join(dir_path, fn))[1].lower() in FilesModel.FILE_EXTS
        ]

