from datetime import timedelta

from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QPixmap, QPixmapCache
from PyQt5.QtSql import QSqlTableModel

from models.base import PixBaseModel
from models.sql.files import FilesModelSQL
from models.sql.scenes import SceneModelSQL
from workers.thumbnails_worker import ThumbnailsWorker


class SceneModel(PixBaseModel):
    COLUMNS = dict([
        ("thumbnail1", ""),
        ("thumbnail2", ""),
        ("thumbnail3", ""),
        ("scene_end", "Duration"),
        ("scene_start", "Timecode")
    ])
    THUMB_HEIGHT = 196
    THUMB_WIDTH = 160

    def __init__(self, ui, page, _scenes_list_view):
        super().__init__()
        self.table_name = 'scenes'
        self.fields = SceneModelSQL.setup_db()
        self.db_model = QSqlTableModel()
        self.db_model.setTable(self.table_name)
        self.cpu_threadpool = None
        self.ui = ui
        self.page = page
        self.time_sum = 0.
        self.timeit_cnt = 0
        self._scenes_list_view = _scenes_list_view

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        row = index.row()
        col= index.column()
        duration_col = self.fields.index('scene_end')
        start_col = self.fields.index('scene_start')
        if role == Qt.DisplayRole:
            if col == duration_col:
                end = self.db_model.data(self.db_model.index(row, col))
                start = self.db_model.data(self.db_model.index(
                    row, self.fields.index('scene_start')))
                t = end - start + 0.00001 #this is to fix str representation of timedelta when exact number of seconds
                timecode = str(timedelta(seconds=t))[:-3]
                return timecode
            if col == start_col:
                start = self.db_model.data(self.db_model.index(row, col))
                t = start + 0.00001 #this is to fix str representation of timedelta when exact number of seconds
                timecode = str(timedelta(seconds=t))[:-3]
                return timecode
        if role == Qt.DecorationRole \
                and col != duration_col \
                and col != start_col:
            visible_row_start = self._scenes_list_view.rowAt(0)
            visible_row_end = self._scenes_list_view.rowAt(self._scenes_list_view.height())
            if self.page == 4 or \
                    not self.slider_moved and (
                    visible_row_end <= 0 and  visible_row_start <= row
                    or visible_row_start <= row <= visible_row_end):
                timestamp = self.db_model.data(self.db_model.index(row, col))
                video_file_idx = index.siblingAtColumn(self.get_video_file_id_column())
                video_file_id = self.db_model.data(video_file_idx)
                fname, _ = FilesModelSQL.select_file_path(video_file_id)
                cache_key = f"{video_file_id}_{timestamp:.2f}"
                pix = QPixmapCache.find(cache_key)
                if not pix:
                    QPixmapCache.insert(cache_key, QPixmap())
                    worker = ThumbnailsWorker(id=video_file_id,
                                            ts=timestamp,
                                            video_file_path=fname,
                                            cache_key=cache_key,
                                            )
                    worker.signals.error.connect(self.print_error)
                    worker.signals.result.connect(self.frame_extracted)
                    worker.signals.finished.connect(self.timeit)
                    self.cpu_threadpool.start(worker)
                return pix

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if self.fields[section] in SceneModel.COLUMNS:
                return SceneModel.COLUMNS[self.fields[section]]
        return super().headerData(section, orientation, role)

    def get_video_file_id_column(self):
        return self.fields.index('video_file_id')

    def timeit(self, id, t):
        self.time_sum += t
        self.timeit_cnt += 1




