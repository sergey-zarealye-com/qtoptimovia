from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtCore import Qt

from models.base import PixBaseModel
from models.scenes import SceneModel
from models.sql.montage_materials import MontageMaterialsModelSQL


class MontageMaterialsModel(SceneModel):
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
        super().__init__(ui, page, _scenes_list_view)
        self.table_name = 'montage_materials'
        MontageMaterialsModelSQL.setup_db()
        self.fields = ['scenes.id',
                       'video_file_id',
                       'scene_start',
                       'scene_end',
                       'thumbnail1',
                       'thumbnail2',
                       'thumbnail3',
                       ]
        self.ui = ui
        self.page = page
        self._scenes_list_view = _scenes_list_view
        self.db_model = QSqlQueryModel()
        self.q_tpl = """
        SELECT scenes.id, scenes.video_file_id as video_file_id, scene_start, scene_end, thumbnail1, thumbnail2, thumbnail3 FROM scenes 
        JOIN montage_materials ON montage_materials.video_file_id=scenes.video_file_id
        JOIN montage_headers ON montage_headers.id=montage_materials.montage_header_id
        JOIN video_files ON video_files.id=montage_materials.video_file_id
        WHERE montage_headers.is_current=1 
        ORDER BY montage_materials.position, video_files.created_at
        """

    def columnCount(self, index):
        if index.isValid():
            0
        else:
            return len(self.fields)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if self.fields[section] in MontageMaterialsModel.COLUMNS:
                return MontageMaterialsModel.COLUMNS[self.fields[section]]
        return super(MontageMaterialsModel, self).headerData(section, orientation, role)

    def set_results(self):
        self.db_model.setQuery(self.q_tpl)