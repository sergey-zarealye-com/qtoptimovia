from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                               QFormLayout, QLineEdit, QGroupBox, QSizePolicy,
                               QDateEdit)
from PySide6.QtCore import QDate

class ExtSearchUI:

    def setup_ui(self, win: QWidget, col: int) -> None:
        """Set up ui."""
        widget_container = QWidget()
        layout = QVBoxLayout(widget_container)
        if col == 0:
            layout.addWidget(QLabel('<h2>Search form</h2>'))
            form_layout = QFormLayout()
            form_layout.addRow(win.tr("&Description:"), QLineEdit())
            form_layout.addRow(QLabel(win.tr("Filming date")))
            form_layout.addRow(win.tr("&From:"), QDateEdit(QDate.currentDate()))
            form_layout.addRow(win.tr("&To:"), QDateEdit(QDate.currentDate()))
            form_layout.addRow(QLabel(win.tr("Import date")))
            form_layout.addRow(win.tr("&From:"), QDateEdit(QDate.currentDate()))
            form_layout.addRow(win.tr("&To:"), QDateEdit(QDate.currentDate()))
            groupBox = QGroupBox('')
            groupBox.setLayout(form_layout)
            groupBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            layout.addWidget(groupBox)

        elif col == 1:
            layout.addWidget(QLabel('<h2>Scenes</h2>'))
        elif col == 2:
            layout.addWidget(QLabel('<h2>Storyboard</h2>'))

        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(widget_container)