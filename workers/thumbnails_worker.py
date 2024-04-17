import os
import datetime as dt
import subprocess as sp
import json
import sys
import traceback

import cv2
from PyQt5.QtCore import *
from moviepy.video.io.VideoFileClip import VideoFileClip

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
        try:
            clip = VideoFileClip(self.fname)
            self.frame = clip.get_frame(self.time_stamp)
            clip.close()
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(self.id, dict(cache_key=self.cache_key, frame=self.frame))
        finally:
            pass

