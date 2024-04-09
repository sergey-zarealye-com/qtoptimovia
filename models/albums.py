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
        albums_tree = {
            "By events": {},
            "By filming date": {},
            "By import date": {}
        }
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
            month_name = calendar.month_name[int(month)]
            out[year][month_name] = "%s %s %s" %(field, year, int(month))
        return out