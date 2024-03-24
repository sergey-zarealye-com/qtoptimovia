from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea


class MontageUI:

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