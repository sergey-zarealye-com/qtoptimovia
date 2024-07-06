from PyQt5.QtSql import QSqlQuery
import numpy as np


class SceneModelSQL:

    @staticmethod
    def setup_db():
        create_table_query = QSqlQuery()
        create_table_query.exec(
            f"""
            CREATE TABLE IF NOT EXISTS scenes (
                id INTEGER PRIMARY KEY UNIQUE NOT NULL,
                video_file_id INTEGER NOT NULL,
                scene_num INTEGER NOT NULL,
                scene_start FLOAT NOT NULL,
                scene_end FLOAT NOT NULL,
                scene_embedding BLOB,
                aesthetic_score FLOAT,
                FOREIGN KEY(video_file_id) REFERENCES video_files(id)
            )
            """
        )
        create_idx_query1 = QSqlQuery()
        create_idx_query1.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_scenes_video_file_id ON scenes(video_file_id)
            """
        )
        create_idx_query2 = QSqlQuery()
        create_idx_query2.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_scenes_video_file_id_scene_start ON scenes(video_file_id, scene_start)
            """
        )
        create_idx_query3 = QSqlQuery()
        create_idx_query3.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_scenes_scene_start ON scenes(scene_start)
            """
        )
        create_idx_query4 = QSqlQuery()
        create_idx_query4.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_scenes_duration ON scenes(scene_end-scene_start)
            """
        )
        create_idx_query5 = QSqlQuery()
        create_idx_query5.exec(
            f"""
                    CREATE INDEX IF NOT EXISTS idx_scenes_video_file_id_scene_num ON scenes(video_file_id, scene_num)
                    """
        )
        return ['id',
                'video_file_id',
                'scene_num',
                'scene_start',
                'scene_end',
                'scene_embedding',
                'aesthetic_score'
                ]

    @staticmethod
    def insert(video_file_id, scene_num, scene_start, scene_end, scene_embedding, aesthetic_score):
        insert_query = QSqlQuery()
        insert_query.prepare(
            """
            INSERT INTO scenes (
                video_file_id,
                scene_num,
                scene_start,
                scene_end,
                scene_embedding,
                aesthetic_score
            ) 
            VALUES (?, ?, ?, ?, ?, ?)
            """
        )
        insert_query.addBindValue(video_file_id)
        insert_query.addBindValue(scene_num)
        insert_query.addBindValue(scene_start)
        insert_query.addBindValue(scene_end)
        insert_query.addBindValue(scene_embedding)
        insert_query.addBindValue(aesthetic_score)
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

    @staticmethod
    def select_style_template_scenes():
        create_table_query = QSqlQuery()
        create_table_query.exec("""
            SELECT scenes.id, video_file_id, scene_start, scene_end-scene_start AS duration
            FROM scenes
            JOIN albums_video_files ON albums_video_files.video_files_id=scenes.video_file_id
            JOIN albums ON albums.id = albums_video_files.albums_id
            WHERE 
                albums.is_visible = 1 AND
                duration > 1 AND scene_start > 10
            ORDER BY video_file_id, scene_start
        """)

    @staticmethod
    def get_thumbnail_timestamp(video_file_id: int, limit: int) -> list:
        select_query = QSqlQuery()
        select_query.prepare(f"SELECT scene_start, scene_end FROM scenes WHERE video_file_id=? ORDER BY scene_start ASC LIMIT ?")
        select_query.addBindValue(video_file_id)
        select_query.addBindValue(limit)
        select_query.exec()
        out = []
        while select_query.next():
            scene_start = select_query.value(0)
            scene_end = select_query.value(1)
            out.append((scene_end - scene_start) / 2)
        return out

    @staticmethod
    def scene_view_query(video_file_id):
        return f"""
            SELECT id, video_file_id, scene_num, 
                    COUNT(id) AS sub_scenes_number,
                    MIN(scene_start) AS _scene_start,
                    MAX(scene_end) AS _scene_end,
                    (MIN(scene_start) * 5 + MAX(scene_end)) / 6 AS thumbnail1, 
                    (MIN(scene_start) + MAX(scene_end)) / 2 AS thumbnail2, 
                    (MAX(scene_end) * 5 + MIN(scene_start)) / 6 AS thumbnail3
            FROM scenes 
            WHERE video_file_id={video_file_id}
            GROUP BY video_file_id, scene_num
            ORDER BY scene_num
        """

    @staticmethod
    def get_score(scene_id):
        select_query = QSqlQuery()
        select_query.prepare(f"SELECT aesthetic_score from scenes where id=?")
        select_query.addBindValue(scene_id)
        select_query.exec()
        if select_query.first():
            aesthetic_score = select_query.value(0)
            if type(aesthetic_score) != str:
                return aesthetic_score
        return 0.
