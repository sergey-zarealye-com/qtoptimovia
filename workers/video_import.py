import datetime as dt
import json
import os
import subprocess as sp
import sys
import traceback
import torch
import clip
from PIL import Image
import numpy as np

import cv2
from PyQt5.QtCore import *
from PyQt5.QtSql import QSqlDatabase

from models.files import FilesModel
from workers.worker_signals import WorkerSignals


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
        self.signals = WorkerSignals()

        self.id = kwargs['id']
        self.fname = kwargs['video_file_path']
        self.metadata = kwargs['metadata']
        self.duration = self.metadata['duration']

        BUFFSIZE = 10
        STEP_MSEC = 320 // 2
        MAXTIME = 60000000
        STEP_FRAMES = 8 // 2
        MAXFRAME = 100000
        self.BUFFSIZE = BUFFSIZE
        self.STEP_MSEC = STEP_MSEC
        self.MAXTIME = MAXTIME
        self.STEP_FRAMES = STEP_FRAMES
        self.MAXFRAME = MAXFRAME

        # https://en.wikipedia.org/wiki/Finite_difference_coefficient
        self.FILTR = np.array([35 / 12, -26 / 3, 19 / 2, -14 / 3, 11 / 12])  # forward
        # self.FILTR = np.array([-11/12, 14/3, -19/2, 26/3, -35/12]) #backward
        # self.FILTR = np.array([-1/12,	4/3,	-5/2,	4/3,	-1/12]) #central
        self.NFILTR = len(self.FILTR)
        self.THRESHOLD = 0.5
        self.STD_WINDOW = 10

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)

    @pyqtSlot()
    def run(self):
        try:
            self.scenes = self.split_by_scenes(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(self.id, self.scenes)
        finally:
            self.signals.finished.emit(self.id, self.scenes)
            self.signals.progress.emit(self.id, 100.)

    def tiling(self):
        w = self.metadata['width']
        h = self.metadata['height']
        if w > h:
            x1 = (w - h) // 2
            x2 = w - h
            return (0, 0, h, h), (x1, 0, x1 + h, h), (x2, 0, x2 + h, h)
        elif h > w:
            y1 = (h - w) // 2
            y2 = h - w
            return (0, 0, w, w), (0, y1, w, y1 + w), (0, y2, w, y2 + w)
        else:
            return (0, 0, w, w)

    def split_by_scenes(self, *args, **kwargs):
        # TODO have minimal scene length, join such a short scenes
        scenes = {}
        prev_image_features = None
        mean_image_features = None
        delta = 0.
        scene_start = 0.
        current_pos = 0.
        scene_frames_count = 0
        resp = 0.
        deltas = []
        responces = []
        now_triggered = False
        with torch.no_grad():
            # with open(os.path.join('data',
            #                        os.path.basename(self.fname) + '.txt'), 'w') as out:
            for pos_list, buff in self.frame_iterator():
                for idx in range(len(buff)):
                    current_pos = pos_list[idx]['pos_sec']
                    image_features = None
                    for t in self.tiling():
                        tile = self.clip_preprocess(Image.fromarray(buff[idx][t[1]:t[3], t[0]:t[2]])) \
                            .unsqueeze(0).to(self.device)
                        tile_features = self.clip_model.encode_image(tile)
                        if image_features is None:
                            image_features = tile_features.detach().clone()
                        else:
                            image_features += tile_features
                    norm = torch.linalg.vector_norm(image_features) * len(self.tiling())
                    image_features /= norm
                    if prev_image_features is None:
                        mean_image_features = image_features.detach().clone()
                        scene_frames_count = 1
                    else:
                        mean_image_features += image_features
                        scene_frames_count += 1
                        delta = torch.linalg.vector_norm(prev_image_features - image_features)
                        deltas.append(delta)
                        if len(deltas) >= self.NFILTR:
                            resp = np.dot(np.array(deltas[-self.NFILTR:]), self.FILTR)
                            responces.append(abs(resp))
                        if len(responces) >= self.STD_WINDOW:
                            self.THRESHOLD = 3 * np.array(responces).std()
                        if abs(resp) >= self.THRESHOLD and not now_triggered:
                            scene_end = current_pos - self.STEP_MSEC * (self.NFILTR // 2) / 1000
                            emb = mean_image_features.cpu().numpy() / scene_frames_count
                            self.signals.partial_result.emit(self.id,
                                                             dict(
                                                                 scene_start=scene_start,
                                                                 scene_end=scene_end,
                                                                 scene_embedding=QByteArray(emb.tobytes())
                                                             )
                                                             )
                            scene_start = scene_end
                            scene_frames_count = 0
                            mean_image_features *= 0
                        now_triggered = abs(resp) >= self.THRESHOLD

                        # out.write("%f %f %f %f %d\n" % (pos_list[idx]['pos_sec'], delta, abs(resp), self.THRESHOLD, int(now_triggered)))

                    prev_image_features = image_features.detach().clone()

                pos_sec = pos_list[-1]['pos_sec']
                progress = min(100., 10 + pos_sec / self.duration * 90)
                self.signals.progress.emit(self.id, progress)
            if scene_frames_count > 0:
                emb = mean_image_features.cpu().numpy() / scene_frames_count
                self.signals.partial_result.emit(self.id,
                                                 dict(
                                                     scene_start=scene_start,
                                                     scene_end=current_pos,
                                                     scene_embedding=QByteArray(emb.tobytes())
                                                 )
                                                 )
        return scenes

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
