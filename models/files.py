from PyQt5.QtCore import Qt, QDir, QAbstractTableModel
from PyQt5.QtWidgets import QFileSystemModel, QMessageBox
from PyQt5.QtSql import QSqlQuery, QSqlTableModel

import os


class FilesModel(QAbstractTableModel):
    FILE_FILTERS = ['*.mov', '*.avi', '*.mp4']
    FILE_EXTS = ['.mov', '.avi', '.mp4']
    COLUMNS = dict([("description", "Description"),
               ("proc_progress", "Processed"),
    ])


    def __init__(self):
        super().__init__()
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(QDir.currentPath())
        self.fs_model.setNameFilters(FilesModel.FILE_FILTERS)
        self.fs_model.setNameFilterDisables(False)
        self.fields = self.setup_db()
        self.selected_dir = None
        self.db_model = QSqlTableModel()
        self.db_model.setTable("video_files")
        self.db_model.setEditStrategy(QSqlTableModel.OnFieldChange)

    def data(self, index, role):
        row = index.row()
        col= index.column()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.db_model.data(self.db_model.index(row, col))

    # def get_id(self, index):
    #     row = index.row()
    #     return self.db_model.data(self.db_model.index(row, self.db_model.fieldIndex('id')))

    def rowCount(self, index):
        if index.isValid():
            0
        else:
            return self.db_model.rowCount()

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            col = index.column()
            if col in self.get_editable_columns():
                ok = self.db_model.setData(index, value, role)
                return ok
            else:
                return False
        return True

    def flags(self, index):
        col = index.column()
        if col in self.get_editable_columns():
            return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if self.fields[section] in FilesModel.COLUMNS:
                return FilesModel.COLUMNS[self.fields[section]]
        return super().headerData(section, orientation, role)

    def get_progress_section(self):
        return self.fields.index('proc_progress')
    #
    def get_editable_columns(self):
        return [self.fields.index('description')]

    def columnCount(self, index):
        if index.isValid():
            0
        else:
            return self.db_model.columnCount()

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
        return ['id' ,
                'import_name' ,
                'import_dir' ,
                'cache_path' ,
                'archive_path' ,
                'imported_at' ,
                'processed_at' ,
                'archived_at' ,
                'proc_progress' ,
                'description']

    def get_file_path(self, idx):
        self.selected_dir = self.fs_model.filePath(idx)
        return self.selected_dir

    def get_video_files(self, dir_path):
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
            VALUES (?, ?, NULL, NULL, DATETIME('now', 'localtime'), NULL, NULL, 0, ?)
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
                insert_query.addBindValue(fname)
                insert_query.exec()
                fcount += 1
        QMessageBox.information(
            None,
            "Video files import finished",
            f"{fcount} files were scheduled for processing"
        )

    def update_field(self, id, field, value):
        query = QSqlQuery()
        query.exec("UPDATE video_files SET description = 'eee' WHERE id = 13")
        # query.prepare("UPDATE video_files SET ? = ? WHERE id = ?")
        # query.addBindValue(field)
        # query.addBindValue(value)
        # query.addBindValue(id)
        # ok = query.exec()
        # print(ok)
        print(query.last())
        print(query.lastError().driverText())
        print(query.lastError().databaseText())
        return True