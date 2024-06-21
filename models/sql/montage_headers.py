from PyQt5.QtSql import QSqlQuery
import datetime as dt


class MontageHeadersModelSQL:

    @staticmethod
    def setup_db():
        create_table_query = QSqlQuery()
        create_table_query.exec(
            f"""
            CREATE TABLE IF NOT EXISTS montage_headers (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                created_at DATETIME,
                name TEXT,
                params TEXT,
                is_current SMALLINT DEFAULT 1
            )
            """
        )

        return ['id',
                'created_at',
                'name',
                'params',
                'is_current',
                ]

    @staticmethod
    def insert(name, params, is_current):
        insert_query = QSqlQuery()
        insert_query.prepare(
            """
            INSERT INTO montage_headers (
                created_at,
                name,
                params,
                is_current
            ) 
            VALUES (DATETIME('now', 'localtime'), ?, ?, ?)
            """
        )
        insert_query.addBindValue(name)
        insert_query.addBindValue(params)
        insert_query.addBindValue(is_current)
        insert_query.exec()
        return insert_query.lastInsertId()

    @staticmethod
    def get_current():
        select_query = QSqlQuery()
        select_query.exec("SELECT id FROM montage_headers WHERE is_current=1 LIMIT 1")
        if select_query.first():
            return select_query.value(0)
        else:
            return MontageHeadersModelSQL.insert(dt.datetime.now().isoformat(), "{}", 1)

    @staticmethod
    def get_videos():
        select_query = QSqlQuery()
        select_query.exec("""
                    SELECT video_files.id, video_files.description, video_files.width, video_files.height from video_files
                    JOIN montage_materials ON montage_materials.video_file_id=video_files.id
                    JOIN montage_headers ON montage_headers.id=montage_materials.montage_header_id
                    WHERE montage_headers.is_current=1 
                    ORDER BY montage_materials.position, video_files.created_at
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
