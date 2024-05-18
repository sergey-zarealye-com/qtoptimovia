from models.albums import AlbumsModel
from ui.windows.choose_album import ChooseAlbumDialog


class SlotsBase():

    def clear_scenes_view(self):
        self.update_layout(self.ui.scenes_list_model, set_filter="0")
        self.ui.info_action.setDisabled(True)  # Info tool button
        if hasattr(self.ui, 'to_album_action'):
            self.ui.to_album_action.setDisabled(True)

    def show_scenes(self, signal):
        video_file_id = self.get_video_file_id(signal)
        self.update_layout(self.ui.scenes_list_model, set_filter=f"video_file_id='{video_file_id}'")
        self.ui.info_action.setEnabled(True)
        if hasattr(self.ui, 'to_album_action'):
            self.ui.to_album_action.setEnabled(True)

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
                AlbumsModel.add_file_to_album(album_id, video_file_id)
