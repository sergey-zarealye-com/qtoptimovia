from PyQt5.QtWidgets import QMessageBox

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

    def clear_montage_headers(self):
        dlg = QMessageBox(self.window)
        dlg.setWindowTitle("Please confirm")
        dlg.setText(f"You are about to erase the list of videos selected for montage.\nAre you sure?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()

        if button == QMessageBox.Yes:
            MontageHeadersModelSQL.erase()
            MontageMaterialsModelSQL.erase()
            self.ui.montage_materials_model.set_results()
            self.ui.selected_video_files_list.clear()


    def remove_footage(self):
        videos = MontageHeadersModelSQL.get_videos()
        video_files_id = [videos[i.row()]['video_file_id'] for i in self.ui.selected_video_files_list.selectedIndexes()]
        MontageHeadersModelSQL.remove_by(video_files_id=video_files_id)
        self.load_video_files_list()
        self.populate_footage()


