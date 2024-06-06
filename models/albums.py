from PyQt5.QtGui import QStandardItem
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtGui import QStandardItemModel

from models.sql.albums import AlbumsModelSQL


class AlbumsModel(QStandardItemModel):

    def __init__(self):
        super().__init__()
        self.table_name = 'albums'
        self.fields = AlbumsModelSQL.setup_db()
        albums_tree = {
            "By events": {},
            "By filming date": {},
            "By import date": {}
        }
        albums_tree['By events'] = AlbumsModelSQL.select_albums_2dict()
        albums_tree['By filming date'] = AlbumsModelSQL.select_dates('created_at')
        albums_tree['By import date'] = AlbumsModelSQL.select_dates('imported_at')
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
        alb_id = insert_query.lastInsertId()
        parent = self.item(0, 0)
        parent.appendRow([QStandardItem(name), QStandardItem('album id %d' % alb_id)])
        return parent.index()

    def del_album(self, album_id):
        del_query1 = QSqlQuery()
        del_query1.exec(f"DELETE FROM albums_video_files WHERE albums_id={album_id}")
        del_query2 = QSqlQuery()
        del_query2.exec(f"DELETE FROM albums WHERE id={album_id}")
        parent = self.item(0, 0)
        return parent.index()
    



