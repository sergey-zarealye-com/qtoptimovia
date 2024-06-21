from PyQt5.QtSql import QSqlQuery


class MontageMaterialsModelSQL:

    @staticmethod
    def setup_db():
        create_table_query = QSqlQuery()
        create_table_query.exec(
            f"""
            CREATE TABLE IF NOT EXISTS montage_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                montage_header_id INTEGER NOT NULL,
                video_file_id INTEGER NOT NULL,
                position INTEGER DEFAULT 0,
                FOREIGN KEY(montage_header_id) REFERENCES montage_headers(id)
                FOREIGN KEY(video_file_id) REFERENCES video_files(id)
            )
            """
        )

        return ['id',
                'montage_header_id',
                'video_file_id',
                'position',
                ]

    @staticmethod
    def insert(montage_header_id, video_file_id, position):
        insert_query = QSqlQuery()
        insert_query.prepare(
            """
            INSERT INTO montage_materials (
                montage_header_id,
                video_file_id,
                position
            ) 
            VALUES (?, ?, ?)
            """
        )
        insert_query.addBindValue(montage_header_id)
        insert_query.addBindValue(video_file_id)
        insert_query.addBindValue(position)
        insert_query.exec()
        return insert_query.lastInsertId()

    @staticmethod
    def add_to_montage(montage_header_id, video_file_id):
        if not MontageMaterialsModelSQL.is_video_in_montage(video_file_id):
            return MontageMaterialsModelSQL.insert(montage_header_id, video_file_id, 0)

    @staticmethod
    def is_video_in_montage(video_file_id):
        select_query = QSqlQuery()
        select_query.prepare("""
            SELECT montage_materials.id FROM montage_materials 
            JOIN montage_headers ON montage_headers.id=montage_materials.montage_header_id
            WHERE montage_headers.is_current=1 
            AND montage_materials.video_file_id=?
            LIMIT 1
        """)
        select_query.addBindValue(video_file_id)
        select_query.exec()
        return select_query.first()



