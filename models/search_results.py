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
        self.fields = [ 'scenes.id' ,
                        'video_file_id',
                        'scene_start' ,
                        'scene_end' ,
                        'thumbnail1',
                        'thumbnail2',
                        'thumbnail3',
                        'video_files.created_at',
                        'video_files.imported_at',
                        'video_files.width',
                        'video_files.height',
                       ]
        self.q_tpl = f"""SELECT {','.join(self.fields)} ,
                        INSTR(',%s,)', ',' || scenes.id || ',') AS sorter
                        FROM scenes 
                        JOIN video_files ON video_files.id = scenes.video_file_id
                        WHERE scenes.id IN (%s) """
        self.count_tpl = f"""SELECT COUNT(scenes.id) FROM scenes 
                                JOIN video_files ON video_files.id = scenes.video_file_id
                                WHERE scenes.id IN (%s)"""
        self.ui = ui
        self.page = page
        self.time_sum = 0.
        self.timeit_cnt = 0
        self.cpu_threadpool = None
        self.limit = 10
        self.offset = 0
        self.total_results = 0

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

    def set_results(self, scene_id_list, is_include_horizontal, is_include_vertical,
                    created_at_from, created_at_to, imported_at_from, imported_at_to):
        indexes = ','.join([str(i) for i in scene_id_list])
        q = self.q_tpl % (indexes, indexes)
        count = self.count_tpl % ','.join([str(i) for i in scene_id_list])
        if is_include_horizontal != is_include_vertical:
            if is_include_horizontal:
                q += " AND video_files.width > video_files.height "
                count += " AND video_files.width > video_files.height "
            if is_include_vertical:
                q += " AND video_files.width < video_files.height "
                count += " AND video_files.width < video_files.height "
        if created_at_from < created_at_to:
            q += f" AND video_files.created_at >= DATE('{created_at_from.toString('yyyy-MM-dd')}')" \
                 f" AND video_files.created_at <= DATE('{created_at_to.toString('yyyy-MM-dd')}') "
            count += f" AND video_files.created_at >= DATE('{created_at_from.toString('yyyy-MM-dd')}')" \
                 f" AND video_files.created_at <= DATE('{created_at_to.toString('yyyy-MM-dd')}') "
        if imported_at_from < imported_at_to:
            q += f" AND video_files.imported_at >= DATE('{imported_at_from.toString('yyyy-MM-dd')}')" \
                 f" AND video_files.imported_at <= DATE('{imported_at_to.toString('yyyy-MM-dd')}') "
            count += f" AND video_files.imported_at >= DATE('{imported_at_from.toString('yyyy-MM-dd')}')" \
                 f" AND video_files.imported_at <= DATE('{imported_at_to.toString('yyyy-MM-dd')}') "

        q += "AND sorter > 0 ORDER BY sorter "
        q += f"LIMIT {self.limit} OFFSET {self.offset}"

        count_q = QSqlQuery()
        count_q.exec(count)
        if count_q.first():
            self.total_results = count_q.value(0)

        self.db_model.setQuery(q)

    def goback(self):
        self.offset = max(0, self.offset - self.limit)
        page = self.offset // self.limit
        back_disable = page == 0
        fwd_disable = self.offset >= self.total_results - self.limit
        return page, back_disable, fwd_disable

    def gofwd(self):
        self.offset = max(0, min(self.total_results - self.limit, self.offset + self.limit))
        page = self.offset // self.limit
        back_disable = page == 0
        fwd_disable = self.offset >= self.total_results - self.limit
        return page, back_disable, fwd_disable





