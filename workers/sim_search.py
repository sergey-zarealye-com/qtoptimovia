import os
import sys
import traceback

import clip
import numpy as np
import nmslib
import torch
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMessageBox

from workers.worker_signals import WorkerSignals


class SimSearcher(QRunnable):
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
        super(SimSearcher, self).__init__()

        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.fv = kwargs['fv']

    @pyqtSlot()
    def run(self):
        scene_index_list, distances = [], []
        try:
            scene_index_list, distances = self.get_knn(self.fv)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
            self.signals.result.emit(0, None)
        else:
            self.signals.result.emit(0, dict(scene_index_list=scene_index_list,
                                             distances=distances))

    def get_knn(self, vector, k=500):
        fname = os.path.join('data', 'scenes.idx')
        index = nmslib.init(method='hnsw', space='l2')
        try:
            index.loadIndex(fname)
        except:
            QMessageBox.critical(
                None,
                "Optimovia - Error!",
                traceback.format_exc(),
            )
        ids, distances = index.knnQuery(vector, k=k)
        return ids, distances
