import os
import datetime as dt
import subprocess as sp
import json
import sys
import traceback

from PyQt5.QtCore import *

from workers.worker_signals import WorkerSignals


class MetadataWorker(QRunnable):
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
        super(MetadataWorker, self).__init__()

        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.id = kwargs['id']
        self.fname = self.kwargs['video_file_path']
        self.duration = 0.


    @pyqtSlot()
    def run(self):
        try:
            self.metadata = self.parse_metadata(*self.args, **self.kwargs)
            self.signals.progress.emit(self.id, 10.0)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.metadata_result.emit(self.id, self.metadata)
            self.signals.finished.emit(self.id, self.metadata)

    def parse_metadata(self, *args, **kwargs):
            bitrate = 0.0
            rot = 0
            """
            Ищет в выходных данных ffprobe такие строки и парсит из них мета-данные фильма:        
            Stream #0:0: Video: mpeg4 (Advanced Simple Profile) (XVID / 0x44495658), yuv420p, 720x400 [SAR 1:1 DAR 9:5], 1976 kb/s, 25 fps, 25 tbr, 25 tbn, 25 tb
            Stream #0:0: Video: rawvideo (UYVY / 0x59565955), uyvy422, 720x576, 172800 kb/s, 25 fps, 25 tbr, 25 tbn, 25 tbc
            Stream #0:0(und): Video: h264 (High) (avc1 / 0x31637661), yuv420p, 1280x676 [SAR 1:1 DAR 320:169], 1959 kb/s, 25 fps, 25 tbr, 25 tbn, 50 tbc (default)
            """
            if sys.platform == 'win32':
                FFPROBE = "ffmpeg/bin/ffprobe -v quiet -print_format json -show_format -show_streams"
            else:
                FFPROBE = "ffprobe -v quiet -print_format json -show_format -show_streams"

            command = FFPROBE.split() + [self.fname]
            pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE,
                            cwd=os.path.dirname(os.path.realpath(__file__)))
            pipe.stdout.readline()
            infos = pipe.stdout.read().decode("utf-8")
            parsed = json.loads("{" + infos)
            creation_time = dt.datetime.now().isoformat()
            aac_rate = 0
            audio_depth = 0
            audio_channels = 0
            if not (u'streams' in parsed):
                raise Exception("File seems not to contain any video.")
            for stream in parsed[u'streams']:
                if stream[u'codec_type'] == 'audio':
                    aac_rate = stream[u'bit_rate']
                    audio_channels = stream[u'channels']
                if stream[u'codec_type'] == 'video':
                    if u'tags' in stream:
                        if u'rotate' in stream[u'tags']:
                            rot = int(stream[u'tags'][u'rotate'])
                        elif u'side_data_list' in stream:
                            for side_data in stream[u'side_data_list']:
                                if u'rotation' in side_data:
                                    rot = int(side_data[u'rotation'])
                                    break
                        if u'creation_time' in stream[u'tags']:
                            creation_time = stream[u'tags'][u'creation_time']
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
                    self.duration = float(stream[u'duration'])

            aspect = float(sar[0]) / float(sar[1])
            data = dict(fps=fps, created_at=creation_time, duration=self.duration,
                        width=w, height=h, audio_depth=audio_depth, aac_rate=aac_rate, audio_channels=audio_channels,
                        aspect=aspect, rot=rot, sar=sar, dar=dar, start=start, bitrate=bitrate)
            return data
