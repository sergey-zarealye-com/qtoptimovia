from PySide6.QtCore import QDir
from PySide6.QtWidgets import QFileSystemModel
import os

class FilesModel():
    FILE_FILTERS = ['*.mov', '*.avi', '*.mp4']
    FILE_EXTS = ['.mov', '.avi', '.mp4']

    def __init__(self):
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        self.model.setNameFilters(FilesModel.FILE_FILTERS)
        self.model.setNameFilterDisables(False)

    def get_model(self):
        return self.model

    def get_file_path(self, idx):
        return self.model.filePath(idx)

    def get_video_files(self, dir_path):
        files = os.listdir(dir_path)
        return [os.path.join(dir_path, fn) for fn in files
                if os.path.splitext(os.path.join(dir_path, fn))[1].lower() in FilesModel.FILE_EXTS
        ]