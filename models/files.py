from PySide6.QtCore import QDir
from PySide6.QtWidgets import QFileSystemModel, QMessageBox
from PySide6.QtSql import QSqlDatabase, QSqlQuery
import os

class FilesModel():
    FILE_FILTERS = ['*.mov', '*.avi', '*.mp4']
    FILE_EXTS = ['.mov', '.avi', '.mp4']

    def __init__(self):
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        self.model.setNameFilters(FilesModel.FILE_FILTERS)
        self.model.setNameFilterDisables(False)
        self.setup_db()

    def get_model(self):
        return self.model

    def setup_db(self):
        createTableQuery = QSqlQuery()
        createTableQuery.exec(
            """
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
                description TEXT
            )
            """
        )
        createIdxQuery1 = QSqlQuery()
        createIdxQuery1.exec(
            """
            CREATE INDEX IF NOT EXISTS idx_video_files_import_dir ON video_files(import_dir)
            """
        )
        createIdxQuery2 = QSqlQuery()
        createIdxQuery2.exec(
            """
            CREATE INDEX IF NOT EXISTS idx_video_files_import_name ON video_files(import_name)
            """
        )

    def get_file_path(self, idx):
        return self.model.filePath(idx)

    def get_video_files(self, dir_path):
        files = os.listdir(dir_path)
        return [os.path.join(dir_path, fn) for fn in files
                if os.path.splitext(os.path.join(dir_path, fn))[1].lower() in FilesModel.FILE_EXTS
        ]

    # @staticmethod
    # def get_imported_files

    @staticmethod
    def import_files(flist: list[str]):
        select_query = QSqlQuery()
        select_query.prepare(f"SELECT id from video_files where import_dir=? AND import_name=?")
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
            VALUES (?, ?, NULL, NULL, DATETIME('now', 'localtime'), NULL, NULL, 0, '')
            """
        )
        fcount = 0
        for fn in flist:
            path, fname = os.path.split(fn)
            select_query.addBindValue(path)
            select_query.addBindValue(fname)
            select_query.exec()
            if not select_query.first():
                insert_query.addBindValue(fname)
                insert_query.addBindValue(path)
                insert_query.exec()
                fcount += 1
        QMessageBox.information(
            None,
            "Video files import finished",
            f"{fcount} files were scheduled for processing"
        )