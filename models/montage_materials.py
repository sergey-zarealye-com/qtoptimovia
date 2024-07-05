from datetime import timedelta

from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QPixmapCache, QPixmap, QColor
from PyQt5.QtSql import QSqlQueryModel

from models.base import PixBaseModel
from models.scenes import SceneModel
from models.sql.files import FilesModelSQL
from models.sql.montage_materials import MontageMaterialsModelSQL
from models.sql.scenes import SceneModelSQL
from workers.thumbnails_worker import ThumbnailsWorker


class MontageMaterialsModel(PixBaseModel):
    COLUMNS = dict([
        ("thumbnail1", ""),
        ("thumbnail2", ""),
        ("thumbnail3", ""),
        ("_scene_end", "Duration"),
        ("_scene_start", "Timecode")
    ])
    THUMB_HEIGHT = 196
    THUMB_WIDTH = 160

    def __init__(self, ui, page, _scenes_list_view):
        super().__init__()
        self.table_name = 'montage_materials'
        self.fields = MontageMaterialsModelSQL.setup_db()
        self.cpu_threadpool = None
        self.ui = ui
        self.page = page
        self.time_sum = 0.
        self.timeit_cnt = 0
        self._scenes_list_view = _scenes_list_view
        self.view_fields = [
            'id', 'video_file_id', 'scene_num',
            'sub_scenes_number', '_scene_start', '_scene_end',
            'thumbnail1', 'thumbnail2', 'thumbnail3', 'position'
        ]
        self.db_model = QSqlQueryModel()
        self.db_model.setQuery(MontageMaterialsModelSQL.footage_view_query_collapsed('WHERE 0'))
        self.expanded_scene_id = None
        self.expanded_scene_num, self.expanded_scene_file_id, self.expanded_scene_first_position, \
            self.expanded_scene_last_position = None, None, None, None

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        row = index.row()
        col = index.column()
        duration_col = self.view_fields.index('_scene_end')
        start_col = self.view_fields.index('_scene_start')
        sub_scenes_number = self.db_model.data(index.siblingAtColumn(3))
        scene_num = self.db_model.data(index.siblingAtColumn(2))
        position = self.db_model.data(index.siblingAtColumn(9))
        if role == Qt.DisplayRole:
            if col == duration_col:
                end = self.db_model.data(self.db_model.index(row, col))
                start = self.db_model.data(self.db_model.index(
                    row, self.view_fields.index('_scene_start')))
                t = end - start + 0.00001  # this is to fix str representation of timedelta when exact number of seconds
                timecode = str(timedelta(seconds=t))[:-3]
                return timecode
            if col == start_col:
                start = self.db_model.data(self.db_model.index(row, col))
                t = start + 0.00001  # this is to fix str representation of timedelta when exact number of seconds
                timecode = str(timedelta(seconds=t))[:-3]
                return timecode
        if role == Qt.DecorationRole \
                and col != duration_col \
                and col != start_col:
            visible_row_start = self._scenes_list_view.rowAt(0)
            visible_row_end = self._scenes_list_view.rowAt(self._scenes_list_view.height())
            if self.page == 4 or \
                    not self.slider_moved and (
                    visible_row_end <= 0 and visible_row_start <= row
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
        if role == Qt.DecorationRole \
                and col == start_col:
            print(position, self.expanded_scene_first_position, self.expanded_scene_id)
            if position == self.expanded_scene_first_position and self.expanded_scene_id is not None:
                return QPixmap("icons/control-270.png")
            if sub_scenes_number > 1:
                return QPixmap("icons/control.png")
        if role == Qt.BackgroundRole:
            if scene_num == self.expanded_scene_num:
                return QColor("#fbf7f5")

    def columnCount(self, index):
        if index.isValid():
            0
        else:
            return len(self.view_fields)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if self.view_fields[section] in MontageMaterialsModel.COLUMNS:
                return MontageMaterialsModel.COLUMNS[self.view_fields[section]]
        return super(MontageMaterialsModel, self).headerData(section, orientation, role)

    def set_results(self):
        self.db_model.setQuery(self.get_query())
        self.layoutChanged.emit()

    def get_video_file_id_column(self):
        return self.view_fields.index('video_file_id')

    def timeit(self, id, t):
        self.time_sum += t
        self.timeit_cnt += 1

    def get_query(self):
        if self.expanded_scene_id is None:
            return MontageMaterialsModelSQL.footage_view_query_collapsed()
        else:
            self.expanded_scene_num, self.expanded_scene_file_id, \
            self.expanded_scene_first_position, self.expanded_scene_last_position \
                = MontageMaterialsModelSQL.get_scenes_block(self.expanded_scene_id)
            return MontageMaterialsModelSQL.footage_view_query_expanded(self.expanded_scene_num,
                                                                        self.expanded_scene_file_id,
                                                                        self.expanded_scene_first_position,
                                                                        self.expanded_scene_last_position)
