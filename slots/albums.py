import os

from models.albums import AlbumsModel
from models.scenes import SceneModel
from slots.base import SlotsBase
from workers.sim_search import SimSearcher


class AlbumsSlots(SlotsBase):
    def __init__(self, win):
        self.window = win
        self.ui = win.ui.pages[0]
        self.video_file_id_column = 0

    def show_files_for_date(self, signal):
        r = signal.row()
        c = signal.column()
        p = signal.parent()
        rr = self.ui.tree_model.index(r, c+1, p)
        data = self.ui.tree_model.itemFromIndex(rr).text()
        data = data.split()
        if len(data) == 3:
            if data[0] == 'album' and data[1] == 'id':
                album_id = int(data[2])
                video_file_id_list = AlbumsModel.select_files_for_album(album_id)
                self.update_layout(self.ui.files_list_model, 
                                   set_filter=f"id IN ({','.join(video_file_id_list)})")
            else:
                field = data[0]
                year = int(data[1])
                month = int(data[2])
                self.update_layout(self.ui.files_list_model, 
                                   set_filter=f"strftime('%Y', {field})='{year}' AND strftime('%m', {field})='{month:02d}'")
            self.ui.files_list_view.clearSelection()
            self.clear_scenes_view()


