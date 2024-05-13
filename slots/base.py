class SlotsBase():

    def clear_scenes_view(self):
        self.update_layout(self.ui.scenes_list_model, set_filter="0")
        self.ui.info_action.setDisabled(True)  # Info tool button

    def show_scenes(self, signal):
        video_file_id = self.get_video_file_id(signal)
        self.update_layout(self.ui.scenes_list_model, set_filter=f"video_file_id='{video_file_id}'")
        self.ui.info_action.setEnabled(True)

    def update_layout(self, model, set_filter=None):
        if set_filter != None:
            model.db_model.setFilter(set_filter)
        model.db_model.select()
        model.layoutChanged.emit()

    def get_video_file_id(self, signal):
        video_file_id_idx = signal.siblingAtColumn(self.video_file_id_column)
        return signal.model().db_model.data(video_file_id_idx)