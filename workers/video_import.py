import os
import datetime as dt
import subprocess as sp
import json
import sys
import traceback, sys

import cv2
from PyQt5.QtCore import *
from PyQt5.QtSql import QSqlDatabase

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

        self.id = kwargs['id']
        self.fname = self.kwargs['video_file_path']
        self.duration = 0.

        BUFFSIZE = 10
        STEP_MSEC = 320
        MAXTIME = 60000
        STEP_FRAMES = 8
        MAXFRAME = 1000
        self.BUFFSIZE = BUFFSIZE
        self.STEP_MSEC = STEP_MSEC
        self.MAXTIME = MAXTIME
        self.STEP_FRAMES = STEP_FRAMES
        self.MAXFRAME = MAXFRAME

    @pyqtSlot()
    def run(self):
        try:
            self.metadata = self.parse_metadata(*self.args, **self.kwargs)
            self.kwargs['metadata_callback'].emit(self.id, self.metadata)
            self.kwargs['progress_callback'].emit(self.id, 10.0)
            scenes = self.split_by_scenes(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            pass #self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

    def split_by_scenes(self, *args, **kwargs):
        for pos_list, buff in self.frame_iterator():
            pos_sec = pos_list[-1]['pos_sec']
            progress = pos_sec / self.duration * 90
            self.kwargs['progress_callback'].emit(self.id, progress)

    def parse_metadata(self, *args, **kwargs):
            bitrate = 0.0
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
            creation_time = None
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
                    rot = 0
                    if u'tags' in stream:
                        if u'rotate' in stream[u'tags']:
                            rot = int(stream[u'tags'][u'rotate'])
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

            # ==============================================================================
            #     Итератор по фильму позволяет получать кадры, упакованные в мини-батчи.
            #     Входные данные:
            #     -    fname - путь к файлу видео.
            #     -    scene_cuts (опционально) - список границ сцен в миллисекундах.
            #           Если он задан, мини-батчи формируются с учетом этого,
            #           т.е. в мини-батч попадают только кадры из одной сцены,
            #           не более CUT_MAX_FRAMES.
            #     -    CUT_MAX_FRAMES не должен быть больше 10 (ограничение реализации
            #           GoogLeNet) игнорируется если scene_cuts не задан!
            #     -    STEP_MSEC - интервал выбороки кадров из фильма в миллисекундах
            #     -    MAXTIME - предел длительности фильма в миллисекундах;
            #           0 - нет предела (весь фильм)
            #     -    BUFFSIZE - максимальный размер минибатча
            # ==============================================================================

    def frame_iterator(self, scene_cuts=None, CUT_MAX_FRAMES=10, is_ravnomerno=False):
        buff_cnt = 0
        buff = []
        pos_list = []
        cap = cv2.VideoCapture(self.fname)
        current_cut = 0
        if is_ravnomerno:
            sample_step = scene_cuts[0] / (CUT_MAX_FRAMES + 1)
        else:
            sample_step = self.STEP_MSEC
        if cap.isOpened():
            frame_msec = 0.
            try:
                while True:
                    ret = cap.grab()
                    if ret > 0:
                        msec = cap.get(cv2.CAP_PROP_POS_MSEC)
                        pos_frames = cap.get(cv2.CAP_PROP_POS_FRAMES)
                        pos_avi_ratio = cap.get(cv2.CAP_PROP_POS_AVI_RATIO)
                        if self.MAXTIME > 0 and msec > self.MAXTIME:
                            print("MAXTIME reached", msec)
                            break
                        if msec - frame_msec >= sample_step:  # self.STEP_MSEC:
                            if scene_cuts is None:
                                ret, bgr_frame = cap.retrieve()
                                frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
                                frame_msec = msec
                                buff_cnt += 1
                                buff.append(frame)
                                pos_list.append({'pos_sec': msec / 1000.,
                                                 'pos_frames': pos_frames})
                                if buff_cnt >= self.BUFFSIZE:
                                    yield pos_list, buff
                                    buff_cnt = 0
                                    buff = []
                                    pos_list = []
                            elif not is_ravnomerno:
                                if buff_cnt < CUT_MAX_FRAMES and (
                                        current_cut >= len(scene_cuts) or
                                        msec < scene_cuts[current_cut]):
                                    ret, bgr_frame = cap.retrieve()
                                    frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
                                    frame_msec = msec
                                    buff_cnt += 1
                                    buff.append(frame)
                                    pos_list.append({'pos_sec': msec / 1000.,
                                                     'pos_frames': pos_frames,
                                                     'pos_avi_ratio': pos_avi_ratio})

                                if current_cut < len(scene_cuts) and msec >= scene_cuts[current_cut]:
                                    current_cut += 1
                                    if len(pos_list):
                                        yield pos_list, buff
                                        buff_cnt = 0
                                        buff = []
                                        pos_list = []
                            else:
                                if 0 < current_cut < len(scene_cuts):
                                    sample_step = (scene_cuts[current_cut] - scene_cuts[current_cut - 1]) / (
                                            CUT_MAX_FRAMES + 0)
                                if buff_cnt < CUT_MAX_FRAMES and (
                                        current_cut >= len(scene_cuts) or
                                        msec < scene_cuts[current_cut]):
                                    ret, bgr_frame = cap.retrieve()
                                    frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
                                    frame_msec = msec
                                    buff_cnt += 1
                                    buff.append(frame)
                                    pos_list.append({'pos_sec': msec / 1000.,
                                                     'pos_frames': pos_frames,
                                                     'pos_avi_ratio': pos_avi_ratio})

                                if current_cut < len(scene_cuts) and msec >= scene_cuts[current_cut]:
                                    current_cut += 1
                                    if len(pos_list):
                                        yield pos_list, buff
                                        buff_cnt = 0
                                        buff = []
                                        pos_list = []
                    else:
                        break
            except GeneratorExit:
                print(traceback.format_exc())
                pass
            except Exception:
                print(traceback.format_exc())
            cap.release()
            if len(pos_list) and (scene_cuts is None):
                yield pos_list, buff
            elif len(pos_list) and (scene_cuts != None):
                yield pos_list, buff