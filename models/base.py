from PyQt5.QtCore import QAbstractTableModel, QByteArray
from PyQt5.QtGui import QPixmap, QImage, QPixmapCache
from PyQt5.QtWidgets import QMessageBox


class PixBaseModel(QAbstractTableModel):

    def __init__(self):
        super().__init__()
        self.slider_moved = False

    def frame_extracted(self, id, obj):
        frm = obj['frame']
        if frm is not None:
            h, w = frm.shape[:2]
            im = QImage(QByteArray(frm.tobytes()), w, h, QImage.Format_RGB888)
            if h > w:
                im = im.scaledToHeight(self.THUMB_HEIGHT)
            else:
                im = im.scaledToWidth(self.THUMB_WIDTH)
            pix = QPixmap.fromImage(im)
            QPixmapCache.insert(obj['cache_key'], pix)
            self.layoutChanged.emit()

    def rowCount(self, index):
        if index.isValid():
            0
        else:
            return self.db_model.rowCount()

    def columnCount(self, index):
        if index.isValid():
            0
        else:
            return self.db_model.columnCount()

    def print_error(self, e):
        exctype, value, traceback_ = e
        QMessageBox.critical(
            None,
            "Optimovia - Error!",
            "Database Error: %s\n%s" % (value, traceback_),
        )