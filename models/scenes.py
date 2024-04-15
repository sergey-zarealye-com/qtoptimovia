from PyQt5.QtCore import Qt, QDir, QAbstractTableModel
from PyQt5.QtSql import QSqlQuery, QSqlTableModel
import numpy as np

import os


class SceneModel(QAbstractTableModel):
    COLUMNS = dict([
        ("scene_start", "Start"),
        ("scene_end", "End"),
    ])


    def __init__(self):
        super().__init__()
        self.table_name = 'scenes'
        self.fields = self.setup_db()
        self.db_model = QSqlTableModel()
        self.db_model.setTable(self.table_name)
        self.db_model.setEditStrategy(QSqlTableModel.OnFieldChange)

    def setup_db(self):
        create_table_query = QSqlQuery()
        create_table_query.exec(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                video_file_id INTEGER NOT NULL,
                scene_start FLOAT NOT NULL,
                scene_end FLOAT NOT NULL,
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
                'scene_embedding' ,
                ]

    @staticmethod
    def insert(video_file_id, scene_start, scene_end, scene_embedding):
        insert_query = QSqlQuery()
        insert_query.prepare(
            """
            INSERT INTO scenes (
                video_file_id,
                scene_start,
                scene_end,
                scene_embedding
            ) 
            VALUES (?, ?, ?, ?)
            """
        )
        insert_query.addBindValue(video_file_id)
        insert_query.addBindValue(scene_start)
        insert_query.addBindValue(scene_end)
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
