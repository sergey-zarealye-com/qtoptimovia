from PyQt5.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QFormLayout, QWidget, QVBoxLayout, QComboBox

from models.albums import AlbumsModel


class ChooseAlbumDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.album_selector = QComboBox()
        self.albums = AlbumsModel.select_albums()
        self.album_selector.addItems([a[1] for a in self.albums])
        QBtn = QDialogButtonBox.Save | QDialogButtonBox.Cancel
        layout = QVBoxLayout()
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.setWindowTitle("Choose an album")
        form_layout = QFormLayout()
        form_layout.addRow('Album name', self.album_selector)
        form = QWidget()
        form.setLayout(form_layout)
        layout.addWidget(form)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
