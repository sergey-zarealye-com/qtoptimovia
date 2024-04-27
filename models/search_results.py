from datetime import timedelta

from PyQt5.QtCore import Qt, QDir, QAbstractTableModel, QVariant, QByteArray
from PyQt5.QtSql import QSqlQuery, QSqlTableModel, QSqlQueryModel
from PyQt5.QtGui import QPixmap, QImage, QPixmapCache, QColor

import numpy as np

import os

from PyQt5.QtWidgets import QMessageBox

from models.files import FilesModel
from models.scenes import SceneModel
from workers.thumbnails_worker import ThumbnailsWorker


class SearchResult(SceneModel):
    COLUMNS = dict([
        ("thumbnail1", ""),
        ("thumbnail2", ""),
        ("thumbnail3", ""),
        ("scene_end", "Duration"),
        ("scene_start", "Timecode")
    ])
    THUMB_HEIGHT = 196
    THUMB_WIDTH = 160

    def __init__(self, ui, page):
        super(SceneModel, self).__init__()
        self.table_name = 'scenes'
        self.db_model = QSqlQueryModel()
        self.fields = [ 'id' ,
                        'video_file_id',
                        'scene_start' ,
                        'scene_end' ,
                        'thumbnail1',
                        'thumbnail2',
                        'thumbnail3',
                       ]
        self.q_tpl = f"SELECT {','.join(self.fields)} FROM scenes where id IN (%s)"
        self.ui = ui
        self.page = page
        self.time_sum = 0.
        self.timeit_cnt = 0
        self.cpu_threadpool = None

    def columnCount(self, index):
        if index.isValid():
            0
        else:
            return len(self.fields)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if self.fields[section] in SearchResult.COLUMNS:
                return SearchResult.COLUMNS[self.fields[section]]
        return super(SceneModel, self).headerData(section, orientation, role)

    def frame_extracted(self, id, obj):
        frm = obj['frame']
        h, w = frm.shape[:2]
        im = QImage(QByteArray(frm.tobytes()), w, h, QImage.Format_RGB888)
        im = im.scaledToWidth(self.THUMB_WIDTH)
        pix = QPixmap.fromImage(im)
        QPixmapCache.insert(obj['cache_key'], pix)
        self.layoutChanged.emit()

    def set_results(self, scene_id_list):
        q = self.q_tpl % ','.join([str(i) for i in scene_id_list])
        self.db_model.setQuery(q)






