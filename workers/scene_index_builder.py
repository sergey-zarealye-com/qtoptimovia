import os
import sys
import traceback
import numpy as np
import nmslib
from PyQt5.QtCore import *
from PyQt5.QtSql import QSqlQuery, QSqlDatabase
from PyQt5.QtWidgets import QMessageBox

from models.scenes import SceneModel
from workers.worker_signals import WorkerSignals


class SceneIndexBuilder(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, *args, **kwargs):
        super(SceneIndexBuilder, self).__init__()

        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            self.index_rebuild()
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.con.close()

    def index_rebuild(self):
        self.con = QSqlDatabase.addDatabase("QSQLITE", "indexer_db_connection")
        self.con.setDatabaseName("data/optimovia.db")
        self.con.setConnectOptions("QSQLITE_OPEN_READONLY")
        if not self.con.open():
            QMessageBox.critical(
                None,
                "Optimovia - Error!",
                "Database Error: %s" % self.con.lastError().databaseText(),
            )
            sys.exit(1)
        fname = os.path.join('data', 'scenes.idx')
        index = nmslib.init(method='hnsw', space='l2')
        for id_list, data in self.iterate_embeddings_batch():
            index.addDataPointBatch(data, id_list)
        index.createIndex({'post': 2}, print_progress=True)
        index.saveIndex(fname)
        # TODO updated index seems to be reloaded only after app restarting

    def iterate_embeddings_batch(self):
        select_query = QSqlQuery(db=self.con)
        lim = 25
        offset = 0
        while True:
            select_query.exec(f"SELECT id, scene_embedding FROM scenes WHERE 1 LIMIT {lim} OFFSET {offset}")
            id_list, batch = [], []
            while select_query.next():
                id = select_query.value(0)
                buff = select_query.value(1)
                id_list.append(id)
                batch.append(SceneModel.frombuffer(buff))
            if len(id_list):
                yield id_list, np.array(batch)
                offset += lim
            else:
                break