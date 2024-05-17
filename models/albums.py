from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtGui import QStandardItemModel
from PyQt5 import QtCore

import calendar
from collections import defaultdict


class AlbumsModel(QStandardItemModel):

    def __init__(self):
        super().__init__()
        self.table_name = 'albums'
        self.fields = self.setup_db()
        albums_tree = {
            "By events": {},
            "By filming date": {},
            "By import date": {}
        }
        albums_tree['By events'] = self.select_albums_2dict()
        albums_tree['By filming date'] = self.select_dates('created_at')
        albums_tree['By import date'] = self.select_dates('imported_at')
        self.setColumnCount(2)
        self.fill_model_from_dict(self.invisibleRootItem(), albums_tree)
        

    def fill_model_from_dict(self, parent, d):
        if isinstance(d, dict):
            for key, value in d.items():
                it = QStandardItem(str(key))
                if isinstance(value, dict):
                    parent.appendRow([it, QStandardItem('')])
                    self.fill_model_from_dict(it, value)
                else:
                    it2 = QStandardItem(value)
                    parent.appendRow([it, it2])

    def select_dates(self, field):
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
    def select_albums():
        select_query = QSqlQuery()
        select_query.exec("SELECT id, name, position FROM albums WHERE is_visible>0 ORDER BY position")
        out = []
        while select_query.next():
            album_id = select_query.value(0)
            name = select_query.value(1)
            out.append((album_id, name))
        return out

    def select_albums_2dict(self):
        albums = AlbumsModel.select_albums()
        out = defaultdict(dict)
        for album_id, name in albums:
            out[name] = "album id %d" % album_id
        return out

    @staticmethod
    def add_file_to_album(album_id, video_file_id):
        insert_query = QSqlQuery()
        insert_query.prepare("""
                    INSERT INTO albums_video_files (video_files_id, albums_id)
                    VALUES (?, ?)
                """)
        insert_query.addBindValue(video_file_id)
        insert_query.addBindValue(album_id)
        insert_query.exec()

    def add_album(self, name):
        select_query = QSqlQuery()
        select_query.exec("SELECT position FROM albums WHERE is_visible>0 ORDER BY position DESC LIMIT 1")
        if select_query.first():
            new_pos = select_query.value(0) + 1
        else:
            new_pos = 0
        insert_query = QSqlQuery()
        insert_query.prepare("""
            INSERT INTO albums (name, created_at, position, is_visible)
            VALUES (?, DATETIME('now', 'localtime'), ?, 1)
        """)
        insert_query.addBindValue(name)
        insert_query.addBindValue(new_pos)
        insert_query.exec()
        parent = self.item(0, 0)
        parent.appendRow([QStandardItem(name), QStandardItem('')])
        return parent.index()

    def del_album(self, album_id):
        del_query1 = QSqlQuery()
        del_query1.exec(f"DELETE FROM albums_video_files WHERE albums_id={album_id}")
        del_query2 = QSqlQuery()
        del_query2.exec(f"DELETE FROM albums WHERE id={album_id}")
        parent = self.item(0, 0)
        return parent.index()
    
    @staticmethod
    def select_files_for_album(album_id):
        select_query = QSqlQuery()
        select_query.exec(f"SELECT video_files_id FROM albums_video_files WHERE albums_id={album_id}")
        out = []
        while select_query.next():
            out.append(str(select_query.value(0)))
        return out

    def setup_db(self):
        # select video_files_id, albums_id, albums.name as album_name, video_files.name as file_name 
        # from albums_video_files
        # join video_files on video_files.id=albums_video_files.video_files_id
        # left join albums on albums.id=albums_video_files.albums_id
        create_table_query = QSqlQuery()
        create_table_query.exec(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                name VARCHAR NOT NULL,
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
            CREATE INDEX IF NOT EXISTS idx_{self.table_name}_video_files ON {self.table_name}(video_files)
            """
        )
        return [
            'id',
            'name',
            'created_at',
            'position',
            'is_visible'
        ]
        