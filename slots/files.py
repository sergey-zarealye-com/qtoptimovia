import os

from slots.base import SlotsBase


class FilesSlots(SlotsBase):
    def __init__(self, win):
        self.window = win
        self.ui = win.ui.pages[1]
        self.video_file_id_column = 0

    def show_files_in_dir(self, signal):
        if self.ui.tree.isExpanded(signal):
            dir_path = self.ui.files_list_model.get_file_path(signal)
            self.window.video_files_in_directory = self.ui.files_list_model.get_video_files(dir_path)
            self.update_layout(self.ui.files_list_model, set_filter=f"import_dir='{dir_path}'")
            self.ui.files_list_view.clearSelection()
            self.clear_scenes_view()
            # Import tool button
            self.ui.import_action.setEnabled(len(self.window.video_files_in_directory) > 0)
        else:
            self.collapse_files(signal)
            selected_path = self.ui.files_list_model.fs_model.filePath(signal)
            if os.path.isfile(selected_path):
                dir_path, file_name = os.path.split(selected_path)
                self.window.video_files_in_directory = [selected_path]
                self.update_layout(self.ui.files_list_model, set_filter=f"import_dir='{dir_path}' AND import_name='{file_name}'")
                self.clear_scenes_view()
                self.ui.import_action.setEnabled(True)

    def collapse_files(self, signal):
        # Import tool button
        self.ui.import_action.setEnabled(False)
        self.update_layout(self.ui.files_list_model, set_filter='0')
        self.clear_scenes_view()