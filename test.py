
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data, checked):
        super(TableModel, self).__init__()
        self._data = data
        self._checked = checked

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data[index.row()][index.column()]
            return str(value)

        if role == Qt.CheckStateRole:
            checked = self._checked[index.row()][index.column()]
            return Qt.Checked if checked else Qt.Unchecked

    def setData(self, index, value, role):
        if role == Qt.CheckStateRole:
            checked = value == Qt.Checked
            self._checked[index.row()][index.column()] = checked
            return True

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def flags(self, index):
        return Qt.ItemIsSelectable|Qt.ItemIsEnabled|Qt.ItemIsUserCheckable

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()


        self.table = QtWidgets.QTableView()

        data = [
          [1, 9, 2],
          [1, 0, -1],
          [3, 5, 2],
          [3, 3, 2],
          [5, 8, 9],
        ]

        checked = [
          [True, True, True],
          [False, False, False],
          [True, False, False],
          [True, False, True],
          [False, True, True],
        ]

        self.model = TableModel(data, checked)
        self.table.setModel(self.model)

        self.setCentralWidget(self.table)



app=QtWidgets.QApplication(sys.argv)
window=MainWindow()
window.show()
app.exec_()










'''

# https://mountcreo.com/article/pyqtpyside-drag-and-drop-qtableview-reordering-rows/


from PyQt5.QtCore import (Qt)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QProxyStyle, QStyleOption,
                             QTableView, QHeaderView,
                             QItemDelegate,
                             QApplication, QLabel)


class customTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSelectionBehavior(self.SelectRows)  # Select whole rows
        self.setSelectionMode(self.SingleSelection)  # Only select/drag one row each time
        self.setDragDropMode(
            self.InternalMove)  # Objects can only be drag/dropped internally and are moved instead of copied
        self.setDragDropOverwriteMode(False)  # Removes the original item after moving instead of clearing it

        # Set our custom style - this draws the drop indicator across the whole row
        self.setStyle(customStyle())

        model = customModel()
        self.setModel(model)
        self.populate()

    def populate(self):
        set_enabled = True  # We'll change this value to show how to drag rows with disabled elements later
        model = self.model()
        for row in ['a', 'b', 'c', 'd', 'e', 'f', 'g']:
            data = []
            for column in range(5):
                item = QStandardItem(f'{row}-{column}')
                item.setDropEnabled(False)
                if column == 3:
                    item.setEnabled(set_enabled)
                data.append(item)
            model.appendRow(data)
        self.setColumnHidden(2, True)


class customModel(QStandardItemModel):
    def mimeData(self, indices):
        """
        Move all data, including hidden/disabled columns
        """
        index = indices[0]
        new_data = []

        for col in range(self.columnCount()):
            new_data.append(index.sibling(index.row(), col))

        item = self.item(index.row(), 3)
        self.was_enabled = item.isEnabled()
        item.setEnabled(True)  # Hack// Fixes copying instead of moving when item is disabled

        return super().mimeData(new_data)

    def dropMimeData(self, data, action, row, col, parent):
        """
        Always move the entire row, and don't allow column "shifting"
        """
        response = super().dropMimeData(data, Qt.CopyAction, row, 0, parent)
        if row == -1:  # Drop after last row
            row = self.rowCount() - 1
        item = self.item(row, 3)
        item.setEnabled(self.was_enabled)  # Hack// Fixes copying instead of moving when style column is disabled
        return response

class customStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget=None):
        """
        Draw a line across the entire row rather than just the column
        we're hovering over.  This may not always work depending on global
        style - for instance I think it won't work on OSX.
        """
        if element == self.PE_IndicatorItemViewItemDrop and not option.rect.isNull():
            option_new = QStyleOption(option)
            option_new.rect.setLeft(0)
            if widget:
                option_new.rect.setRight(widget.width())
            option = option_new
        super().drawPrimitive(element, option, painter, widget)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    table = customTableView()
    table.resize(600, 300)
    table.show()
    sys.exit(app.exec_())


'''