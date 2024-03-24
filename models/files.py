from PyQt5.QtCore import Qt, QDir, QAbstractListModel
from PyQt5.QtWidgets import QFileSystemModel, QMessageBox
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

import os

class FilesModel(QAbstractListModel):
    FILE_FILTERS = ['*.mov', '*.avi', '*.mp4']
    FILE_EXTS = ['.mov', '.avi', '.mp4']

    def __init__(self):
        super().__init__()
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(QDir.currentPath())
        self.fs_model.setNameFilters(FilesModel.FILE_FILTERS)
        self.fs_model.setNameFilterDisables(False)
        self.setup_db()
        self.selected_dir = None
        self.db_model = QSqlTableModel()
        self.db_model.setTable("video_files")

    def data(self, i, role):
        if role == Qt.DisplayRole:
            import_name = self.db_model.data(self.db_model.index(i.row(), self.db_model.fieldIndex("import_name")))
            proc_progress = self.db_model.data(self.db_model.index(i.row(), self.db_model.fieldIndex("proc_progress")))
            return import_name

    def rowCount(self, index):
        if index.isValid():
            0
        else:
            return self.db_model.rowCount()

    def setup_db(self):
        create_table_query = QSqlQuery()
        create_table_query.exec(
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
        create_idx_query1 = QSqlQuery()
        create_idx_query1.exec(
            """
            CREATE INDEX IF NOT EXISTS idx_video_files_import_dir ON video_files(import_dir)
            """
        )
        create_idx_query2 = QSqlQuery()
        create_idx_query2.exec(
            """
            CREATE INDEX IF NOT EXISTS idx_video_files_import_name ON video_files(import_name)
            """
        )

    def get_file_path(self, idx):
        self.selected_dir = self.fs_model.filePath(idx)
        return self.selected_dir

    def get_video_files(self, dir_path):
        # self.db_model.setFilter(f"import_dir='{dir_path}'")
        # self.db_model.select()
        # print('get_video_files', self.db_model.rowCount())
        files = os.listdir(dir_path)
        return [os.path.join(dir_path, fn) for fn in files
                if os.path.splitext(os.path.join(dir_path, fn))[1].lower() in FilesModel.FILE_EXTS
        ]

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