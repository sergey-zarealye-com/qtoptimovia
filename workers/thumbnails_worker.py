from time import time_ns as time
import sys
import traceback

from PyQt5.QtCore import *
import cv2

from workers.worker_signals import WorkerSignals


class ThumbnailsWorker(QRunnable):
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
        super(ThumbnailsWorker, self).__init__()

        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.id = kwargs['id']
        self.fname = self.kwargs['video_file_path']
        self.time_stamp = self.kwargs['ts']
        self.cache_key = self.kwargs['cache_key']
        self.frame = None

    @pyqtSlot()
    def run(self):
        t = 10000.
        t0 = time()
        cap = cv2.VideoCapture(self.fname)
        try:
            cap.set(cv2.CAP_PROP_POS_MSEC, self.time_stamp * 1000)
            ret, bgr_frame = cap.retrieve()
            if bgr_frame is not None:
                self.frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
                h, w = self.frame.shape[:2]
                self.frame = cv2.resize(self.frame, (256, h*256//w), cv2.INTER_NEAREST)
            t = time() - t0
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(self.id, dict(cache_key=self.cache_key,
                                                   frame=self.frame))
        finally:
            cap.release()
            self.signals.finished.emit(self.id, t)
