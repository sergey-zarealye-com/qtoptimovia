from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import Qt


class UiBase:

    def show_context_menu(self, pos):
        index = self.scenes_list_view.indexAt(pos)
        self.context_index = index
        self.scene_context_menu.popup(self.scenes_list_view.viewport().mapToGlobal(pos))

    def setup_context_menu(self, view):
        view.setContextMenuPolicy(Qt.CustomContextMenu)
        view.customContextMenuRequested.connect(self.show_context_menu)
        self.scene_context_menu = QMenu()
        self.find_similar_action = QAction('Find similar')
        self.scene_context_menu.addAction(self.find_similar_action)