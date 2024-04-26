from datetime import timedelta

from PyQt5.QtCore import Qt, QDir, QAbstractTableModel, QVariant, QByteArray
from PyQt5.QtSql import QSqlQuery, QSqlTableModel
from PyQt5.QtGui import QPixmap, QImage, QPixmapCache, QColor

import numpy as np

import os

from PyQt5.QtWidgets import QMessageBox

from models.files import FilesModel
from workers.thumbnails_worker import ThumbnailsWorker


class SceneModel(QAbstractTableModel):
    COLUMNS = dict([
        ("thumbnail1", ""),
        ("thumbnail2", ""),
        ("thumbnail3", ""),
        ("scene_end", "Duration"),
        ("scene_start", "Timecode")
    ])
    THUMB_HEIGHT = 196
    THUMB_WIDTH = 160

    def __init__(self, ui):
        super().__init__()
        self.table_name = 'scenes'
        self.fields = self.setup_db()
        self.db_model = QSqlTableModel()
        self.db_model.setTable(self.table_name)
        self.cpu_threadpool = None
        self.ui = ui
        self.time_sum = 0.
        self.timeit_cnt = 0

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
            timestamp = self.db_model.data(self.db_model.index(row, col))
            video_file_idx = index.siblingAtColumn(self.get_video_file_id_column())
            video_file_id = self.db_model.data(video_file_idx)
            fname, _ = FilesModel.select_file_path(video_file_id)
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

    def rowCount(self, index):
        if index.isValid():
            0
        else:
            return self.db_model.rowCount()

    def columnCount(self, index):
        if index.isValid():
            0
        else:
            return self.db_model.columnCount()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if self.fields[section] in SceneModel.COLUMNS:
                return SceneModel.COLUMNS[self.fields[section]]
        return super().headerData(section, orientation, role)

    def get_video_file_id_column(self):
        return self.fields.index('video_file_id')

    def print_error(self, e):
        exctype, value, traceback_ = e
        QMessageBox.critical(
            None,
            "Optimovia - Error!",
            "Database Error: %s\n%s" % (value, traceback_),
        )

    def frame_extracted(self, id, obj):
        frm = obj['frame']
        h, w = frm.shape[:2]
        im = QImage(QByteArray(frm.tobytes()), w, h, QImage.Format_RGB888)
        if h > w:
            im = im.scaledToHeight(self.THUMB_HEIGHT)
        else:
            im = im.scaledToWidth(self.THUMB_WIDTH)
        pix = QPixmap.fromImage(im)
        QPixmapCache.insert(obj['cache_key'], pix)
        self.layoutChanged.emit()

    def timeit(self, id, t):
        self.time_sum += t
        self.timeit_cnt += 1

    def setup_db(self):
        create_table_query = QSqlQuery()
        create_table_query.exec(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                video_file_id INTEGER NOT NULL,
                scene_start FLOAT NOT NULL,
                scene_end FLOAT NOT NULL,
                thumbnail1 FLOAT NOT NULL,
                thumbnail2 FLOAT NOT NULL,
                thumbnail3 FLOAT NOT NULL,
                scene_embedding BLOB
            )
            """
        )
        create_idx_query1 = QSqlQuery()
        create_idx_query1.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{self.table_name}_video_file_id ON {self.table_name}(video_file_id)
            """
        )
        return ['id' ,
                'video_file_id',
                'scene_start' ,
                'scene_end' ,
                'thumbnail1',
                'thumbnail2',
                'thumbnail3',
                'scene_embedding' ,
                ]

    @staticmethod
    def insert(video_file_id, scene_start, scene_end, scene_embedding):
        duration = scene_end - scene_start
        thumbnail1 = scene_start + duration / 6
        thumbnail2 = scene_start + duration / 2
        thumbnail3 = scene_end - duration / 6
        insert_query = QSqlQuery()
        insert_query.prepare(
            """
            INSERT INTO scenes (
                video_file_id,
                scene_start,
                scene_end,
                thumbnail1,
                thumbnail2,
                thumbnail3,
                scene_embedding
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
        )
        insert_query.addBindValue(video_file_id)
        insert_query.addBindValue(scene_start)
        insert_query.addBindValue(scene_end)
        insert_query.addBindValue(thumbnail1)
        insert_query.addBindValue(thumbnail2)
        insert_query.addBindValue(thumbnail3)
        insert_query.addBindValue(scene_embedding)
        insert_query.exec()
        return insert_query.lastInsertId()

    @staticmethod
    def select_embedding(scene_id):
        select_query = QSqlQuery()
        select_query.prepare(f"SELECT scene_embedding from scenes where id=?")
        select_query.addBindValue(scene_id)
        select_query.exec()
        if select_query.first():
            buff = select_query.value(0)
            return np.frombuffer(buff, dtype=np.float32)


