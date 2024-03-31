import os
import datetime as dt
import subprocess as sp
import json
import time
import traceback, sys

from PyQt5.QtCore import *
from models.files import FilesModel


class VideoImportWorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        float indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int, float)
    metadata_result = pyqtSignal(int, object)

class VideoImportWorker(QRunnable):
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
        super(VideoImportWorker, self).__init__()

        self.args = args
        self.kwargs = kwargs
        self.signals = VideoImportWorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress
        self.kwargs['metadata_callback'] = self.signals.metadata_result

        self.db = kwargs['db']
        self.id = kwargs['id']

    @pyqtSlot()
    def run(self):
        try:
            metadata = self.parse_metadata(*self.args, **self.kwargs)
            self.kwargs['metadata_callback'].emit(self.id, metadata)
            self.kwargs['progress_callback'].emit(self.id, 10.0)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            pass #self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

    def parse_metadata(self, *args, **kwargs):
        fname = FilesModel.select_file_path(self.id, self.db)
        if fname == None:
            raise Exception(f"Record not found in video_files id {self.id}")
        else:
            aspect = 1.0
            bitrate = 0.0
            """
            Ищет в выходных данных ffprobe такие строки и парсит из них мета-данные фильма:        
            Stream #0:0: Video: mpeg4 (Advanced Simple Profile) (XVID / 0x44495658), yuv420p, 720x400 [SAR 1:1 DAR 9:5], 1976 kb/s, 25 fps, 25 tbr, 25 tbn, 25 tb
            Stream #0:0: Video: rawvideo (UYVY / 0x59565955), uyvy422, 720x576, 172800 kb/s, 25 fps, 25 tbr, 25 tbn, 25 tbc
            Stream #0:0(und): Video: h264 (High) (avc1 / 0x31637661), yuv420p, 1280x676 [SAR 1:1 DAR 320:169], 1959 kb/s, 25 fps, 25 tbr, 25 tbn, 50 tbc (default)
            """
            FFPROBE = "ffmpeg/bin/ffprobe -v quiet -print_format json -show_format -show_streams"
            if not os.path.isfile(fname):
                raise Exception('File not found: ' + fname)
            else:
                command = FFPROBE.split() + [fname]
                pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE,
                                cwd=os.path.dirname(os.path.realpath(__file__)))
                pipe.stdout.readline()
                infos = pipe.stdout.read().decode("utf-8")
                parsed = json.loads("{" + infos)
                creation_time = None
                aac_rate = 0
                audio_depth = 0
                audio_channels = 0
                if not (u'streams' in parsed):
                    raise Exception("File seems not to contain any video.")
                else:
                    for stream in parsed[u'streams']:
                        if stream[u'codec_type'] == 'audio':
                            aac_rate = stream[u'bit_rate']
                            audio_channels = stream[u'channels']
                        if stream[u'codec_type'] == 'video':
                            rot = 0
                            if u'tags' in stream:
                                if u'rotate' in stream[u'tags']:
                                    rot = int(stream[u'tags'][u'rotate'])
                                if u'creation_time' in stream[u'tags']:
                                    creation_time = stream[u'tags'][u'creation_time']
                                    # try:
                                    #     creation_time = dt.datetime.strptime(_creation_time, "%Y-%m-%dT%H:%M:%S.%fZ")
                                    # except:
                                    #     try:
                                    #         creation_time = dt.datetime.strptime(_creation_time, "%Y-%m-%d %H:%M:%S")
                                    #     except:
                                    #         try:
                                    #             creation_time = dt.datetime.strptime(_creation_time, "%Y-%m-%dT%H:%M:%SZ")
                                    #         except:
                                    #             pass
                                    # #TODO в системе время должно быть в 24-ч формате!!!!!!!!!
                            if rot == 0:
                                w = int(stream[u'width'])
                                h = int(stream[u'height'])
                            elif rot == 180 or rot == -180:
                                w = int(stream[u'width'])
                                h = int(stream[u'height'])
                            elif rot == 90 or rot == -90:
                                h = int(stream[u'width'])
                                w = int(stream[u'height'])
                            elif rot == 270 or rot == -270:
                                h = int(stream[u'width'])
                                w = int(stream[u'height'])
                            else:
                                raise Exception('Unknown rotation angle')
                            if u'bit_rate' in stream:
                                bitrate = int(stream[u'bit_rate']) / 1000
                            else:
                                bitrate = int(parsed[u'format'][u'bit_rate']) / 1000
                            fps_n, fps_d = stream[u'r_frame_rate'].split('/')
                            fps = float(fps_n) / float(fps_d)
                            if u'sample_aspect_ratio' in stream:
                                sar = tuple([int(o) for o in stream[u'sample_aspect_ratio'].split(':')])
                                if sar[0] == 0 or sar[1] == 0:
                                    sar = (1, 1)
                            else:
                                sar = (1, 1)
                            if u'display_aspect_ratio' in stream:
                                dar = tuple([int(o) for o in stream[u'display_aspect_ratio'].split(':')])
                            else:
                                dar = (1, 1)
                            start = float(stream[u'start_time'])
                            duration = float(stream[u'duration'])

                aspect = float(sar[0]) / float(sar[1])
                data = dict(fps=fps, creation_time=creation_time, duration=duration,
                            width=w, height=h, audio_depth=audio_depth, aac_rate=aac_rate, audio_channels=audio_channels,
                            aspect=aspect, rot=rot, sar=sar, dar=dar, start=start, bitrate=bitrate)
                return data