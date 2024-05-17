import os

from models.albums import AlbumsModel
from models.scenes import SceneModel
from slots.base import SlotsBase
from ui.windows.add_album import AddAlbumDialog
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
        item = self.ui.tree_model.itemFromIndex(rr)
        data = item.text().split()
        self.ui.add_album_action.setEnabled( r==0 and c==0 and p.row()==-1 and p.column()==-1
                                             or
                                             p.row() == 0 and p.column() == 0 and p.parent().row()==-1 and p.parent().column()==-1
                                             )
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

    def add_album(self, signal):
        if self.window.add_album_dialog is None:
            self.window.add_album_dialog = AddAlbumDialog(self.window)
        if self.window.add_album_dialog.exec():
            album_name = self.window.add_album_dialog.name.text()
            idx = self.window.ui.pages[0].tree_model.add_album(album_name)
            self.window.ui.pages[0].tree.setExpanded(idx, True)

    def del_album(self, signal):
        pass