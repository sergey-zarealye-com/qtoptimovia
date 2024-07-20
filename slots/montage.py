from PyQt5.QtWidgets import QMessageBox

from models.sql.montage_headers import MontageHeadersModelSQL
from models.sql.montage_materials import MontageMaterialsModelSQL
from slots.base import SlotsBase


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

    def do_cut(self):
        self.ui.storyboard_model.data_model = MontageMaterialsModelSQL.as_list()
        self.ui.storyboard_model.set_results()

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

    def toggle_sub_scene(self, index):
        scene_id = index.model().db_model.data(index.siblingAtColumn(0))
        if index.model().expanded_scene_id is None:
            index.model().expanded_scene_id = scene_id
        else:
            index.model().expanded_scene_id = None
            index.model().expanded_scene_num, index.model().expanded_scene_file_id, \
            index.model().expanded_scene_first_position, \
            index.model().expanded_scene_last_position = None, None, None, None
        index.model().set_results()

