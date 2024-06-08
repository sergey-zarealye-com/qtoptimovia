import os
from collections import defaultdict
import calendar
from PyQt5.QtCore import QDate
from PyQt5.QtSql import QSqlQuery


class AlbumsModelSQL:

    @staticmethod
    def setup_db():
        # select video_files_id, albums_id, albums.name as album_name, video_files.name as file_name
        # from albums_video_files
        # join video_files on video_files.id=albums_video_files.video_files_id
        # left join albums on albums.id=albums_video_files.albums_id
        create_table_query = QSqlQuery()
        create_table_query.exec(
            f"""
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                name VARCHAR NOT NULL UNIQUE,
                created_at DATETIME NOT NULL,
                position INT NOT NULL,
                is_visible SMALLINT DEFAULT 1
             )
            """
        )
        create_table_query1 = QSqlQuery()
        create_table_query1.exec(
            f"""
            CREATE TABLE IF NOT EXISTS albums_video_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                video_files_id INT NOT NULL,
                albums_id INT NOT NULL
             )
            """
        )
        create_idx_query1 = QSqlQuery()
        create_idx_query1.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_albums_video_files_video_files_id ON albums_video_files(video_files_id)
            """
        )
        create_idx_query2 = QSqlQuery()
        create_idx_query2.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_albums_video_files_albums_id ON albums_video_files(albums_id)
            """
        )
        return [
            'id',
            'name',
            'created_at',
            'position',
            'is_visible'
        ]

    @staticmethod
    def select_files_for_album(album_id):
        select_query = QSqlQuery()
        select_query.exec(f"SELECT video_files_id FROM albums_video_files WHERE albums_id={album_id}")
        out = []
        while select_query.next():
            out.append(str(select_query.value(0)))
        return out

    @staticmethod
    def add_file_to_album(album_id, video_file_id):
        select_query = QSqlQuery()
        select_query.exec(
            f"SELECT id FROM albums_video_files WHERE video_files_id={video_file_id} AND albums_id={album_id}")
        if select_query.first():
            # file already in an album
            return
        insert_query = QSqlQuery()
        insert_query.prepare("""
                        INSERT INTO albums_video_files (video_files_id, albums_id)
                        VALUES (?, ?)
                    """)
        insert_query.addBindValue(video_file_id)
        insert_query.addBindValue(album_id)
        insert_query.exec()

    @staticmethod
    def select_albums():
        select_query = QSqlQuery()
        select_query.exec("SELECT id, name, position FROM albums WHERE is_visible>0 ORDER BY position")
        out = []
        while select_query.next():
            album_id = select_query.value(0)
            name = select_query.value(1)
            out.append((album_id, name))
        return out

    @staticmethod
    def select_dates(field):
        #SELECT strftime('%Y', created_at) as year, strftime('%m', created_at) as month from video_files GROUP by year, month  order by created_at DESC
        select_query = QSqlQuery()
        select_query.exec(f"SELECT strftime('%Y', {field}) as year, strftime('%m', {field}) as month from video_files GROUP by year, month  order by {field} DESC")
        out = defaultdict(dict)
        while select_query.next():
            year = select_query.value(0)
            month = select_query.value(1)
            if year is None or month is None or len(year) == 0 or len(month) == 0:
                continue
            month_name = calendar.month_name[int(month)]
            out[year][month_name] = "%s %s %s" %(field, year, int(month))
        return out

    @staticmethod
    def select_albums_2dict():
        albums = AlbumsModelSQL.select_albums()
        out = defaultdict(dict)
        for album_id, name in albums:
            out[name] = "album id %d" % album_id
        return out