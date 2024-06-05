import os

from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from models.sql.files import FilesModelSQL


class ColoredQFileSystemModel(QFileSystemModel):
    STATUS_MISSING = 1
    STATUS_IMPORTED = 2
    STATUS_CAN_BE_IMPORTED = 3

    def __init__(self):
        super().__init__()

    def data(self, index, role):
        if role == Qt.BackgroundColorRole:
            path = self.filePath(index)
            file_status = self.get_file_status(path)
            if file_status == ColoredQFileSystemModel.STATUS_MISSING:
                return QColor('#ff8a80')
            elif file_status == ColoredQFileSystemModel.STATUS_IMPORTED:
                return QColor('#b9f6ca')
            elif file_status == ColoredQFileSystemModel.STATUS_CAN_BE_IMPORTED:
                return QColor('#ffff8d')

        return super(ColoredQFileSystemModel, self).data(index, role)

    @staticmethod
    def get_file_status(path):
        is_imported = FilesModelSQL.is_file_imported(path)
        is_file_exists = os.path.isfile(path)
        if is_imported and is_file_exists:
            return ColoredQFileSystemModel.STATUS_IMPORTED
        elif not is_imported and is_file_exists:
            return ColoredQFileSystemModel.STATUS_CAN_BE_IMPORTED
        elif is_imported and not is_file_exists:
            return ColoredQFileSystemModel.STATUS_MISSING
