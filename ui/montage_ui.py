from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea

from models.montage_headers import MontageHeadersModel
from models.montage_materials import MontageMaterialsModel


class MontageUI:

    def __init__(self):
        self.montage_headers = MontageHeadersModel()
        self.montage_materials = MontageMaterialsModel()

    def setup_ui(self, win: QWidget, col: int) -> None:
        """Set up ui."""
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            layout.addWidget(QLabel('<h3>Montage projects</h3>'))
        elif col == 1:
            layout.addWidget(QLabel('<h3>Source videos</h3>'))
        elif col == 2:
            layout.addWidget(QLabel('<h3>Storyboard</h3>'))

        scroll_area = QScrollArea()
        scroll_area.setWidget(widget_container)

        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(scroll_area)