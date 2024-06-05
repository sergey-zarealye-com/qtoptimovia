import os

from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from models.sql.files import FilesModelSQL


class ColoredQFileSystemModel(QFileSystemModel):
    def __init__(self):
        super().__init__()
        self.STATUS_MISSING = 1
        self.STATUS_IMPORTED = 2
        self.STATUS_CAN_BE_IMPORTED = 3

    def data(self, index, role):

        if role == Qt.BackgroundColorRole:
            path = self.filePath(index)
            file_status = self.get_file_status(path)
            if file_status == self.STATUS_MISSING:
                return QColor('#ff8a80')
            elif file_status == self.STATUS_IMPORTED:
                return QColor('#b9f6ca')
            elif file_status == self.STATUS_CAN_BE_IMPORTED:
                return QColor('#ffff8d')

        return super(ColoredQFileSystemModel, self).data(index, role)

    def get_file_status(self, path):
        is_imported = FilesModelSQL.is_file_imported(path)
        is_file_exists = os.path.isfile(path)
        if is_imported and is_file_exists:
            return self.STATUS_IMPORTED
        elif not is_imported and is_file_exists:
            return self.STATUS_CAN_BE_IMPORTED