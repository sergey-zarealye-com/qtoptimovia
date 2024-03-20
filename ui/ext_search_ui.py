from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea


class ExtSearchUI:

    def setup_ui(self, win: QWidget, col: int) -> None:
        """Set up ui."""
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            layout.addWidget(QLabel('<h2>Search form</h2>'))
        elif col == 1:
            layout.addWidget(QLabel('<h2>Scenes</h2>'))
        elif col == 2:
            layout.addWidget(QLabel('<h2>Storyboard</h2>'))

        scroll_area = QScrollArea()
        scroll_area.setWidget(widget_container)

        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(scroll_area)