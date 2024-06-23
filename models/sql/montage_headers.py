from PyQt5.QtSql import QSqlQuery


class MontageHeadersModelSQL:

    @staticmethod
    def setup_db():
        create_table_query = QSqlQuery()
        create_table_query.exec(
            """
            CREATE TABLE IF NOT EXISTS montage_headers (
                id INTEGER PRIMARY KEY UNIQUE NOT NULL,
                video_file_id INTEGER NOT NULL UNIQUE,
                FOREIGN KEY(video_file_id) REFERENCES video_files(id)
            )
            """
        )

        return ['id',
                'video_file_id',
                ]

    @staticmethod
    def insert(video_file_id):
        insert_query = QSqlQuery()
        insert_query.prepare(
            """
            INSERT INTO montage_headers (
                video_file_id
            ) 
            VALUES (?)
            """
        )
        insert_query.addBindValue(video_file_id)
        insert_query.exec()
        if insert_query.lastError().number() == 19:
            return -1 #already exists: unique constrain violated
        else:
            return insert_query.lastInsertId()

    @staticmethod
    def erase():
        insert_query = QSqlQuery()
        insert_query.exec(
            """
            DELETE FROM montage_headers WHERE 1
            """
        )

    @staticmethod
    def get_videos():
        select_query = QSqlQuery()
        select_query.exec("""
                    SELECT video_files.id, video_files.description, video_files.width, video_files.height 
                    FROM video_files
                    JOIN montage_headers ON montage_headers.video_file_id=video_files.id
                    ORDER BY video_files.created_at
                """)
        out = []
        while select_query.next():
            out.append(dict(
                video_file_id=select_query.value(0),
                description=select_query.value(1),
                width=select_query.value(2),
                height=select_query.value(3)
            ))
        return out
