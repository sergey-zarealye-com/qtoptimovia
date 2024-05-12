import os

from models.albums import AlbumsModel
from models.files import FilesModel
from models.scenes import SceneModel
from slots.base import SlotsBase


class FilesImportSlots(SlotsBase):
    def __init__(self, win):
        self.window = win
        self.ui = win.ui.pages[1]
        self.video_file_id_column = 0

    def import_video_files(self, signal):
        FilesModel.import_files(self.window.video_files_in_directory)
        self.update_layout(self.ui.files_list_model)

    def update_metadata(self, id:int, metadata:dict):
        FilesModel.update_fields(id, metadata)
        self.update_layout(self.ui.files_list_model)

    def import_thread_complete(self, id: int):
        print('finished import id:', id)
        self.window.ui.pages[0].tree_model = AlbumsModel()
        self.window.ui.pages[0].tree.setModel(self.window.ui.pages[0].tree_model)

    def insert_scene(self, video_file_id:int, obj:dict):
        scene_start = obj['scene_start']
        scene_end = obj['scene_end']
        scene_embedding = obj['scene_embedding']
        scene_id = SceneModel.insert(video_file_id, scene_start, scene_end, scene_embedding)