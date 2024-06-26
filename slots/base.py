from PyQt5.QtWidgets import QHeaderView

from models.scenes import SceneModel
from models.sql.albums import AlbumsModelSQL
from models.sql.files import FilesModelSQL
from models.sql.montage_headers import MontageHeadersModelSQL
from models.sql.montage_materials import MontageMaterialsModelSQL
from models.sql.scenes import SceneModelSQL
from ui.windows.choose_album import ChooseAlbumDialog


class SlotsBase():

    def clear_scenes_view(self):
        self.update_scenes(self.ui.scenes_list_model, -1)
        self.ui.info_action.setDisabled(True)  # Info tool button
        if hasattr(self.ui, 'to_album_action'):
            self.ui.to_album_action.setDisabled(True)
        if hasattr(self.ui, 'to_montage_action'):
            self.ui.to_montage_action.setDisabled(True)

    def show_scenes(self, signal):
        video_file_id = self.get_video_file_id(signal)
        thumb_height = FilesModelSQL.get_thumb_height(video_file_id, SceneModel.THUMB_WIDTH, SceneModel.THUMB_HEIGHT)
        vheader = self.ui.scenes_list_view.verticalHeader()
        vheader.setDefaultSectionSize(thumb_height)
        vheader.sectionResizeMode(QHeaderView.Fixed)
        self.update_scenes(self.ui.scenes_list_model, video_file_id)
        self.ui.info_action.setEnabled(True)
        if hasattr(self.ui, 'to_album_action'):
            self.ui.to_album_action.setEnabled(True)
        if hasattr(self.ui, 'to_montage_action'):
            # self.ui.to_montage_action.setDisabled(MontageMaterialsModelSQL.is_video_in_montage(video_file_id))
            self.ui.to_montage_action.setEnabled(True)

    def update_scenes(self, model, video_file_id):
        model.db_model.setQuery(SceneModelSQL.scene_view_query(video_file_id))
        model.layoutChanged.emit()

    def update_layout(self, model, set_filter=None):
        if set_filter != None:
            model.db_model.setFilter(set_filter)
        model.db_model.select()
        model.layoutChanged.emit()

    def get_video_file_id(self, signal):
        video_file_id_idx = signal.siblingAtColumn(self.video_file_id_column)
        return signal.model().db_model.data(video_file_id_idx)

    def to_album(self, signal):
        sel_indexes = self.ui.files_list_view.selectionModel().selectedIndexes()
        if len(sel_indexes):
            video_file_id = self.get_video_file_id(sel_indexes[0])
            self.window.to_album_dialog = ChooseAlbumDialog(self.window)
            if self.window.to_album_dialog.exec():
                selection = self.window.to_album_dialog.album_selector.currentIndex()
                album_id = self.window.to_album_dialog.albums[selection][0]
                AlbumsModelSQL.add_file_to_album(album_id, video_file_id)

    def to_montage(self, signal):
        sel_indexes = self.ui.files_list_view.selectionModel().selectedIndexes()
        if len(sel_indexes):
            video_file_id = self.get_video_file_id(sel_indexes[0])
            ret = MontageHeadersModelSQL.insert(video_file_id)
            self.ui.to_montage_action.setEnabled(ret is None)

    def slider_moved(self, smth):
        self.ui.scenes_list_model.slider_moved = True

    def slider_released(self):
        self.ui.scenes_list_model.slider_moved = False
        self.ui.scenes_list_model.layoutChanged.emit()