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


class ExtSearcher(QRunnable):
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
        super(ExtSearcher, self).__init__()

        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.prompt = kwargs['prompt']

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)

    @pyqtSlot()
    def run(self):
        scene_index_list = []
        try:
            emb = self.text_embed(self.prompt)
            scene_index_list = self.get_knn(emb)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
            self.signals.result.emit(1, scene_index_list)
        else:
            self.signals.result.emit(0, scene_index_list)

    def text_embed(self, prompt):
        text = clip.tokenize([prompt]).to(self.device)
        with torch.no_grad():
            text_features = self.clip_model.encode_text(text)
            norm = torch.linalg.vector_norm(text_features)
            text_features /= norm
        return text_features.squeeze(0).detach().cpu().numpy()

    def get_knn(self, vector, k=10):
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
        print(distances)
        return ids
