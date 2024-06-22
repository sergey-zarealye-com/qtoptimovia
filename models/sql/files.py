import os

from PyQt5.QtCore import QDate
from PyQt5.QtSql import QSqlQuery


class FilesModelSQL:

    @staticmethod
    def setup_db():
        create_table_query = QSqlQuery()
        create_table_query.exec(
            f"""
            CREATE TABLE IF NOT EXISTS video_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                import_name VARCHAR NOT NULL,
                import_dir VARCHAR NOT NULL,
                cache_path VARCHAR,
                archive_path VARCHAR,
                imported_at DATETIME NOT NULL,
                processed_at DATETIME,
                archived_at DATETIME,
                proc_progress FLOAT NOT NULL,
                description TEXT,
                fps FLOAT, 
                created_at DATETIME, 
                duration FLOAT,
                width INTEGER, 
                height INTEGER, 
                audio_depth FLOAT, 
                aac_rate FLOAT, 
                audio_channels INTEGER,
                aspect FLOAT, 
                rot FLOAT, 
                sar FLOAT, 
                dar FLOAT, 
                start FLOAT, 
                bitrate FLOAT
            )
            """
        )
        create_idx_query1 = QSqlQuery()
        create_idx_query1.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_video_files_import_dir ON video_files(import_dir)
            """
        )
        create_idx_query2 = QSqlQuery()
        create_idx_query2.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_video_files_import_name ON video_files(import_name)
            """
        )
        create_idx_query3 = QSqlQuery()
        create_idx_query3.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_video_files_created_at ON video_files(created_at)
            """
        )
        create_idx_query4 = QSqlQuery()
        create_idx_query4.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_video_files_imported_at ON video_files(imported_at)
            """
        )
        return ['id' ,
                'import_name' ,
                'import_dir' ,
                'cache_path' ,
                'archive_path' ,
                'imported_at' ,
                'processed_at' ,
                'archived_at' ,
                'proc_progress' ,
                'description',
                'fps' ,
                'created_at' ,
                'duration' ,
                'width' ,
                'height' ,
                'audio_depth' ,
                'aac_rate' ,
                'audio_channels' ,
                'aspect' ,
                'rot' ,
                'sar' ,
                'dar' ,
                'start' ,
                'bitrate'
                ]

    @staticmethod
    def is_file_imported(fn):
        select_query = QSqlQuery()
        select_query.prepare("SELECT id from video_files where import_dir=? AND import_name=?")
        path, fname = os.path.split(fn)
        select_query.addBindValue(path)
        select_query.addBindValue(fname)
        select_query.exec()
        return select_query.first()

    @staticmethod
    def import_files(flist: list):
            # select_query = QSqlQuery()
            # select_query.prepare("SELECT id from video_files where import_dir=? AND import_name=?")
            insert_query = QSqlQuery()
            insert_query.prepare(
                    """
                    INSERT INTO video_files (
                        import_name,
                        import_dir,
                        cache_path,
                        archive_path,
                        imported_at,
                        processed_at,
                        archived_at,
                        proc_progress,
                        description
                    ) 
                    VALUES (?, ?, NULL, NULL, DATETIME('now', 'localtime'), NULL, NULL, 0, ?)
                    """
            )
            fcount = 0
            for fn in flist:
                    path, fname = os.path.split(fn)
                    if not FilesModelSQL.is_file_imported(fn):
                            insert_query.addBindValue(fname)
                            insert_query.addBindValue(path)
                            insert_query.addBindValue(fname)
                            insert_query.exec()
                            fcount += 1

    @staticmethod
    def select_nonstarted_imports():
            select_query = QSqlQuery()
            select_query.exec("SELECT id from video_files where processed_at IS NULL AND proc_progress=0.0")
            out = []
            while select_query.next():
                    out.append(select_query.value(0))
            return out

    @staticmethod
    def select_file_path(id: int, fields=[]):
            select_query = QSqlQuery()
            if len(fields):
                    filders = ', ' + ', '.join(fields)
            else:
                    filders = ''
            select_query.prepare(f"SELECT import_name, import_dir {filders} FROM video_files WHERE id=?")
            select_query.addBindValue(id)
            if not select_query.exec():
                    print(select_query.lastError().text())
            if select_query.first():
                    file_path = os.path.join(select_query.value(1), select_query.value(0))
                    other_fields = [select_query.value(i + 2) for i in range(len(fields))]
                    return file_path, other_fields
            else:
                    return None, None

    @staticmethod
    def update_fields(id: int, data: dict):
            updates = [f"{k}=?" for k in data.keys()]
            if len(updates):
                    sql = f"UPDATE video_files SET {', '.join(updates)} WHERE id=?"
                    update_query = QSqlQuery()
                    update_query.prepare(sql)
                    for k in data.keys():
                            update_query.addBindValue(data[k])
                    update_query.addBindValue(id)
                    update_query.exec()
            else:
                    raise Exception('Program error: empty list of fields to update')

    @staticmethod
    def select_uniq_years_all(table_name, field):
            select_query = QSqlQuery()
            select_query.exec(f"SELECT STRFTIME('%Y', {field}) FROM {table_name} GROUP BY STRFTIME('%Y', {field})")
            out = []
            while select_query.next():
                    out.append(select_query.value(0))
            return out

    @staticmethod
    def select_uniq_months_by_year(table_name, field, year):
            select_query = QSqlQuery()
            select_query.prepare(
                    f"SELECT STRFTIME('%m', {field}) FROM {table_name} WHERE STRFTIME('%Y', {field})=? GROUP BY STRFTIME('%m', {field})")
            select_query.addBindValue(year)
            select_query.exec()
            out = []
            while select_query.next():
                    out.append(select_query.value(0))
            return out

    @staticmethod
    def get_rotation(id):
            select_query = QSqlQuery()
            select_query.prepare("SELECT rot FROM video_files WHERE id=?")
            select_query.addBindValue(id)
            if not select_query.exec():
                    print(select_query.lastError().text())
            if select_query.first():
                    return select_query.value(0)
            else:
                    return None

    @staticmethod
    def get_minmax_dates():
            select_query = QSqlQuery()
            q = "SELECT STRFTIME('%Y-%m-%d', MIN(imported_at)), " + \
                "STRFTIME('%Y-%m-%d', MAX(imported_at)), " \
                "STRFTIME('%Y-%m-%d', MIN(created_at)), " \
                "STRFTIME('%Y-%m-%d', MAX(created_at)) " \
                "FROM video_files"
            select_query.exec(q)
            if select_query.first():
                    created_at_min = QDate.fromString(select_query.value(2), 'yyyy-MM-dd')
                    created_at_max = QDate.fromString(select_query.value(3), 'yyyy-MM-dd')
                    imported_at_min = QDate.fromString(select_query.value(0), 'yyyy-MM-dd')
                    imported_at_max = QDate.fromString(select_query.value(1), 'yyyy-MM-dd')
                    if created_at_min == created_at_max:
                            created_at_max = created_at_max.addDays(1)
                    if imported_at_min == imported_at_max:
                            imported_at_max = imported_at_max.addDays(1)
                    return imported_at_min, imported_at_max, created_at_min, created_at_max
            else:
                    return [None] * 4

    @staticmethod
    def get_thumb_height(video_file_id, THUMB_W, THUMB_H):
        w, h = FilesModelSQL.get_frame_size(video_file_id)
        if h > w:
            return THUMB_H
        else:
            return THUMB_W / w * h

    @staticmethod
    def get_frame_size(video_file_id):
        select_query = QSqlQuery()
        select_query.prepare(f"SELECT width, height FROM video_files WHERE id=?")
        select_query.addBindValue(video_file_id)
        select_query.exec()
        if select_query.first():
            width = select_query.value(0)
            height = select_query.value(1)
            return width, height