from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt, QVariant

from models.sql.albums import AlbumsModelSQL


class MontageAlbumsListModel(QAbstractTableModel):
    COLUMNS = dict([
        ("name", "Album"),
        ("is_visible", "Use for style template"),
    ])

    def __init__(self):
        super().__init__()
        self.db_model = QSqlTableModel()
        self.db_model.setTable('albums')
        self.fields = AlbumsModelSQL.setup_db()
        self.db_model.setEditStrategy(QSqlTableModel.OnFieldChange)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if self.fields[section] in MontageAlbumsListModel.COLUMNS:
                return MontageAlbumsListModel.COLUMNS[self.fields[section]]
        return super().headerData(section, orientation, role)

    def flags(self, index):
        col = index.column()
        if col == self.get_editable_column():
            return Qt.ItemIsSelectable|Qt.ItemIsEnabled|Qt.ItemIsUserCheckable
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def get_editable_column(self):
        return self.fields.index('is_visible')

    def setData(self, index, value, role):
        if role == Qt.CheckStateRole:
            col = index.column()
            if col == self.get_editable_column():
                checked = value == Qt.Checked
                ok = self.db_model.setData(index, int(not checked))
                return ok
        # return True

    def data(self, index, role):
        row = index.row()
        col = index.column()
        data = self.db_model.data(self.db_model.index(row, col))
        if role == Qt.CheckStateRole and col == self.get_editable_column():
            if data == 0:
                return Qt.Checked
            else:
                return Qt.Unchecked
        if role == Qt.DisplayRole and col != self.get_editable_column():
            return data

    def rowCount(self, index):
        if index.isValid():
            0
        else:
            return self.db_model.rowCount()

    def columnCount(self, index):
        if index.isValid():
            0
        else:
            return self.db_model.columnCount()

    def update_layout(self):
        self.db_model.select()
        self.layoutChanged.emit()