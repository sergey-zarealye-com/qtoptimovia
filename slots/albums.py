import os

from slots.base import SlotsBase


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
        date = self.ui.tree_model.itemFromIndex(rr).text()
        date = date.split()
        if len(date) == 3:
            field = date[0]
            year = int(date[1])
            month = int(date[2])
            self.update_layout(self.ui.files_list_model, set_filter=f"strftime('%Y', {field})='{year}' AND strftime('%m', {field})='{month:02d}'")
            self.ui.files_list_view.clearSelection()
            self.clear_scenes_view()