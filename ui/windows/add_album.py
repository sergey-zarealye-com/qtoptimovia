from PyQt5.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QFormLayout, QWidget, QVBoxLayout


class AddAlbumDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.name = QLineEdit()
        QBtn = QDialogButtonBox.Save | QDialogButtonBox.Cancel
        layout = QVBoxLayout()
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.setWindowTitle("Add album")
        form_layout = QFormLayout()
        form_layout.addRow('Album name', self.name)
        form = QWidget()
        form.setLayout(form_layout)
        layout.addWidget(form)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
