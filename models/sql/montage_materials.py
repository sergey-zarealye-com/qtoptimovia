from PyQt5.QtSql import QSqlQuery


class MontageMaterialsModelSQL:

    @staticmethod
    def setup_db():
        create_table_query = QSqlQuery()
        create_table_query.exec(
            f"""
            CREATE TABLE IF NOT EXISTS montage_materials (
                id INTEGER PRIMARY KEY UNIQUE NOT NULL,
                scene_id INTEGER NOT NULL UNIQUE,
                position INTEGER DEFAULT 0,
                FOREIGN KEY(scene_id) REFERENCES scenes(id)
            )
            """
        )

        return ['id',
                'scene_id',
                'position',
                ]

    @staticmethod
    def insert(scene_id, position):
        insert_query = QSqlQuery()
        insert_query.prepare(
            """
            INSERT INTO montage_materials (
                scene_id,
                position
            ) 
            VALUES (?, ?)
            """
        )
        insert_query.addBindValue(scene_id)
        insert_query.addBindValue(position)
        insert_query.exec()
        print('Err:', insert_query.lastError().number())
        if insert_query.lastError().number() == 19:
            return -1  # already exists: unique constrain violated
        else:
            return insert_query.lastInsertId()

    @staticmethod
    def insert_from_montage_headers():
        del_query = QSqlQuery()
        del_query.exec("DELETE FROM montage_materials WHERE 1")
        insert_query = QSqlQuery()
        insert_query.exec("""
        INSERT INTO montage_materials (scene_id)

        SELECT scenes.id AS scene_id
        FROM scenes
        JOIN montage_headers ON scenes.video_file_id=montage_headers.video_file_id
        JOIN video_files ON video_files.id=montage_headers.video_file_id
        ORDER BY video_files.created_at, video_files.id, scenes.scene_start
        """)
        upd_query = QSqlQuery()
        upd_query.exec("UPDATE montage_materials SET position=id")

    @staticmethod
    def footage_view_query(condition=''):
        return f"""
            SELECT scenes.id, scenes.video_file_id AS video_file_id, scenes.scene_num AS scene_num,
                    COUNT(scenes.id) AS sub_scenes_number,
                    MIN(scene_start) AS _scene_start,
                    MAX(scene_end) AS _scene_end,
                    (MIN(scene_start) * 5 + MAX(scene_end)) / 6 AS thumbnail1, 
                    (MIN(scene_start) + MAX(scene_end)) / 2 AS thumbnail2, 
                    (MAX(scene_end) * 5 + MIN(scene_start)) / 6 AS thumbnail3 
            FROM scenes 
            JOIN montage_materials ON montage_materials.scene_id=scenes.id
            {condition}
            GROUP BY video_file_id, scenes.scene_num
            ORDER BY montage_materials.position ASC
            """

    @staticmethod
    def erase():
        insert_query = QSqlQuery()
        insert_query.exec(
            """
            DELETE FROM montage_materials WHERE 1
            """
        )

    @staticmethod
    def remove_by(**kwargs):
        if 'video_files_id' in kwargs:
            id_list = ','.join([str(i) for i in kwargs['video_files_id']])
            insert_query = QSqlQuery()
            insert_query.exec(
                f"""
                DELETE FROM montage_headers WHERE scene_id IN (
                    SELECT scene_id.id from scenes
                    JOIN video_files ON video_files.id=scenes.video_file_id
                )
                """
            )

    # @staticmethod
    # def is_video_in_montage(video_file_id, scene_id=None):
    #     scene_clause = ''
    #     if scene_id is not None:
    #         scene_clause = 'AND scene_id=?'
    #     q_tpl = f"""
    #         SELECT id FROM montage_materials
    #         WHERE video_file_id=?
    #         {scene_clause}
    #         LIMIT 1
    #     """
    #     select_query = QSqlQuery()
    #     select_query.prepare(q_tpl)
    #     select_query.addBindValue(video_file_id)
    #     if scene_id is not None:
    #         select_query.addBindValue(scene_id)
    #     select_query.exec()
    #     return select_query.first()



