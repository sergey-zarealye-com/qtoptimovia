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
        insert_query.addBindValue(created_at)
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
