from PyQt5.QtWidgets import QHeaderView

from models.scenes import SceneModel
from models.sql.montage_headers import MontageHeadersModelSQL
from models.sql.montage_materials import MontageMaterialsModelSQL
from models.sql.scenes import SceneModelSQL
from slots.base import SlotsBase
from workers.ext_searcher import ExtSearcher
from workers.sim_search import SimSearcher


class ExtSearchSlots(SlotsBase):
    def __init__(self, win):
        self.window = win
        self.ui = win.ui.pages[4]
        self.search_results = None
        self.video_file_id_column = 1

    def search_scenes(self):
        self.show_search_results(0, None)
        self.clear_scenes_view()
        self.ui.search_results_model.offset = 0
        prompt = self.ui.description.text()
        prompt = prompt.strip()
        if len(prompt):
            worker = ExtSearcher(prompt=prompt)
            worker.signals.result.connect(self.show_search_results)
            self.window.gpu_threadpool.start(worker)

    def show_search_results(self, page:int, search_results:dict):
        self.search_results = search_results
        if search_results is None:
            found_scene_id_list = []
            distances = []
        else:
            found_scene_id_list = search_results['scene_index_list']
            distances = search_results['distances']
        is_include_horizontal = self.ui.include_horizontal.isChecked()
        is_include_vertical = self.ui.include_vertical.isChecked()
        created_at_from = self.ui.created_at_from.date()
        created_at_to = self.ui.created_at_to.date()
        imported_at_from = self.ui.imported_at_from.date()
        imported_at_to = self.ui.imported_at_to.date()
        self.ui.search_results_model.set_results(found_scene_id_list,
                                                  is_include_horizontal, is_include_vertical,
                                                  created_at_from, created_at_to,
                                                  imported_at_from, imported_at_to)
        self.ui.search_results_view.clearSelection()
        self.clear_scenes_view()
        self.ui.search_results_model.layoutChanged.emit()
        self.ui.pager.setText(str(page + 1))
        self.ui.plot_graph.clear()
        self.ui.plot_graph.plot(range(len(distances)), distances)
        if page == 0:
            self.ui.gofwd_action.setDisabled(False)

    def search_results_back(self):
        page, back_disable, fwd_disable = self.ui.search_results_model.goback()
        self.ui.goback_action.setDisabled(back_disable)
        self.ui.gofwd_action.setDisabled(fwd_disable)
        self.show_search_results(page, self.search_results)

    def search_results_fwd(self):
        page, back_disable, fwd_disable = self.ui.search_results_model.gofwd()
        self.ui.goback_action.setDisabled(back_disable)
        self.ui.gofwd_action.setDisabled(fwd_disable)
        self.show_search_results(page, self.search_results)

    def show_found_scenes(self, signal):
        video_file_id_idx = signal.siblingAtColumn(1)
        video_file_id = signal.model().db_model.data(video_file_id_idx)
        self.update_layout(self.ui.scenes_list_model, set_filter=f"video_file_id='{video_file_id}'")
        self.ui.info_action.setEnabled(True)

    def find_similar_scenes(self, flag):
        print('find_similar_scenes')
        uipage = self.window.ui.col3_stack_widget.currentIndex()
        signal = self.window.ui.pages[uipage].context_index
        scene_id_idx = signal.siblingAtColumn(0)
        scene_id = signal.model().db_model.data(scene_id_idx)
        col = signal.column()
        fv = SceneModelSQL.select_embedding(scene_id)
        worker = SimSearcher(fv=fv)
        worker.signals.result.connect(self.show_sim_search_results)
        self.window.cpu_threadpool.start(worker)

    def show_sim_search_results(self, page:int, search_results:dict):
        self.window.ui.col1_stack_widget.setCurrentIndex(4)
        self.window.ui.col2_stack_widget.setCurrentIndex(4)
        self.window.ui.col3_stack_widget.setCurrentIndex(4)
        self.search_results = search_results
        if search_results is None:
            found_scene_id_list = []
            distances = []
        else:
            found_scene_id_list = search_results['scene_index_list']
            distances = search_results['distances']
        self.ui.search_results_model.offset = 0
        self.ui.search_results_model.set_results(found_scene_id_list)
        self.ui.search_results_view.clearSelection()
        self.clear_scenes_view()
        self.ui.search_results_model.layoutChanged.emit()
        self.ui.pager.setText(str(page + 1))

        self.ui.plot_graph.clear()
        self.ui.plot_graph.plot(range(len(distances)), distances)
        if page == 0:
            self.ui.gofwd_action.setDisabled(False)
            self.ui.goback_action.setDisabled(True)

    def to_montage(self, signal):
        sel_indexes = self.ui.search_results_view.selectionModel().selectedIndexes()
        if len(sel_indexes):
            video_file_id = self.get_video_file_id(sel_indexes[0])
            montage_header_id = MontageHeadersModelSQL.get_current()
            if montage_header_id is not None:
                id = MontageMaterialsModelSQL.add_to_montage(montage_header_id, video_file_id)
                self.ui.to_montage_action.setEnabled(id is None)
