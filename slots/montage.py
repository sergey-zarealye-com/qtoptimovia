from models.sql.montage_headers import MontageHeadersModelSQL
from models.sql.montage_materials import MontageMaterialsModelSQL
from models.sql.scenes import SceneModelSQL
from slots.base import SlotsBase
from workers.ext_searcher import ExtSearcher
from workers.sim_search import SimSearcher


class MontageSlots(SlotsBase):
    def __init__(self, win):
        self.window = win
        self.ui = win.ui.pages[3]
        self.video_file_id_column = 1

    def load_video_files_list(self):
        videos = MontageHeadersModelSQL.get_videos()
        self.ui.selected_video_files_list.clear()
        self.ui.selected_video_files_list.addItems([v['description'] for v in videos])

    def populate_footage(self):
        MontageMaterialsModelSQL.insert_from_montage_headers()
        self.ui.montage_materials_model.set_results()

