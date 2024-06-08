from PyQt5.QtSql import QSqlQuery
import numpy as np


class SceneModelSQL:

    @staticmethod
    def setup_db():
        create_table_query = QSqlQuery()
        create_table_query.exec(
            f"""
            CREATE TABLE IF NOT EXISTS scenes (
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
            CREATE INDEX IF NOT EXISTS idx_scenes_video_file_id ON scenes(video_file_id)
            """
        )
        return ['id',
                'video_file_id',
                'scene_start',
                'scene_end',
                'thumbnail1',
                'thumbnail2',
                'thumbnail3',
                'scene_embedding',
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
            return SceneModelSQL.frombuffer(buff)

    @staticmethod
    def frombuffer(buff):
        return np.frombuffer(buff, dtype=np.float16)