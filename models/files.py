from PyQt5.QtCore import Qt, QDir, QAbstractTableModel
from PyQt5.QtWidgets import QFileSystemModel, QMessageBox
from PyQt5.QtSql import QSqlQuery, QSqlTableModel

import os


class FilesModel(QAbstractTableModel):
    FILE_FILTERS = ['*.mov', '*.avi', '*.mp4']
    FILE_EXTS = ['.mov', '.avi', '.mp4']
    COLUMNS = dict([
        ("description", "Description"),
        ("created_at", "Created at"),
        ("proc_progress", "Processed"),
    ])


    def __init__(self, page:int):
        super().__init__()
        self.page = page
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(QDir.currentPath())
        self.fs_model.setNameFilters(FilesModel.FILE_FILTERS)
        self.fs_model.setNameFilterDisables(False)
        self.table_name = "video_files"
        self.fields = self.setup_db()
        self.selected_dir = None
        self.db_model = QSqlTableModel()
        self.db_model.setTable(self.table_name)
        self.db_model.setEditStrategy(QSqlTableModel.OnFieldChange)

    def data(self, index, role):
        row = index.row()
        col= index.column()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.db_model.data(self.db_model.index(row, col))

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
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                import_name VARCHAR NOT NULL,
                import_dir VARCHAR NOT NULL,
                cache_path VARCHAR,
                archive_path VARCHAR,
                imported_at DATETIME NOT NULL,
                processed_at DATETIME,
                archived_at DATETIME,
                proc_progress FLOAT NOT NULL,
                description TEXT,
                fps FLOAT, 
                created_at DATETIME, 
                duration FLOAT,
                width INTEGER, 
                height INTEGER, 
                audio_depth FLOAT, 
                aac_rate FLOAT, 
                audio_channels INTEGER,
                aspect FLOAT, 
                rot FLOAT, 
                sar FLOAT, 
                dar FLOAT, 
                start FLOAT, 
                bitrate FLOAT
            )
            """
        )
        create_idx_query1 = QSqlQuery()
        create_idx_query1.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{self.table_name}_import_dir ON {self.table_name}(import_dir)
            """
        )
        create_idx_query2 = QSqlQuery()
        create_idx_query2.exec(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{self.table_name}_import_name ON {self.table_name}(import_name)
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
                'description',
                'fps' ,
                'created_at' ,
                'duration' ,
                'width' ,
                'height' ,
                'audio_depth' ,
                'aac_rate' ,
                'audio_channels' ,
                'aspect' ,
                'rot' ,
                'sar' ,
                'dar' ,
                'start' ,
                'bitrate'
                ]

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
        select_query.prepare("SELECT id from video_files where import_dir=? AND import_name=?")
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

    @staticmethod
    def select_nonstarted_imports():
        select_query = QSqlQuery()
        select_query.exec("SELECT id from video_files where processed_at IS NULL AND proc_progress=0.0")
        out = []
        while select_query.next():
            out.append(select_query.value(0))
        return out

    @staticmethod
    def select_file_path(id:int):
        select_query = QSqlQuery()
        select_query.prepare("SELECT import_name, import_dir FROM video_files WHERE id=?")
        select_query.addBindValue(id)
        if not select_query.exec():
            print(select_query.lastError().text())
        if select_query.first():
            return os.path.join(select_query.value(1), select_query.value(0))
        else:
            return None

    @staticmethod
    def update_fields(id:int, data:dict):
        updates = [f"{k}=?" for k in data.keys()]
        if len(updates):
            sql = f"UPDATE video_files SET {', '.join(updates)} WHERE id=?"
            update_query = QSqlQuery()
            update_query.prepare(sql)
            for k in data.keys():
                update_query.addBindValue(data[k])
            update_query.addBindValue(id)
            update_query.exec()
        else:
            raise Exception('Program error: empy list of fields to update')

    @staticmethod
    def select_uniq_years_all(table_name, field):
        select_query = QSqlQuery()
        select_query.exec(f"SELECT STRFTIME('%Y', {field}) FROM {table_name} GROUP BY STRFTIME('%Y', {field})")
        out = []
        while select_query.next():
            out.append(select_query.value(0))
        return out

    @staticmethod
    def select_uniq_months_by_year(table_name, field, year):
        select_query = QSqlQuery()
        select_query.prepare(f"SELECT STRFTIME('%m', {field}) FROM {table_name} WHERE STRFTIME('%Y', {field})=? GROUP BY STRFTIME('%m', {field})")
        select_query.addBindValue(year)
        select_query.exec()
        out = []
        while select_query.next():
            out.append(select_query.value(0))
        return out