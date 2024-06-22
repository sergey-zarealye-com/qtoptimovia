from matplotlib import pyplot as plt

x1, x2, resps, thr = [],[],[],[]
sub_starts, sub_ends = [], []
scene_starts, scene_ends = [], []
with open('data/log.txt') as log:
    for row in log:
        data = row.split("\t")
        if data[0] == 'plot':
            current_pos, scene_end, resp, thresh = data[1:]
            x1.append(float(current_pos))
            x2.append(float(scene_end))
            resps.append(float(resp))
            thr.append(float(thresh))
        elif data[0] == 'sub':
            sub_scene_start, current_pos = data[1:]
            sub_starts.append(float(sub_scene_start))
            sub_ends.append(float(current_pos))
        elif data[0] == 'scene':
            scene_start, scene_end = data[1:]
            scene_starts.append(float(scene_start))
            scene_ends.append(float(scene_end))

plt.figure()
plt.plot(x1, resps)
plt.plot(x1, thr)
for i in range(len(sub_starts)):
    plt.plot([sub_starts[i], sub_ends[i]], [-0.5, -0.8])
for i in range(len(scene_starts)):
    plt.plot([scene_starts[i], scene_ends[i]], [-1.5, -1.8])

# plt.scatter(sub_ends, [.1]*len(sub_ends), label='sub_end')
# plt.scatter(scene_ends, [.2]*len(scene_ends), label='scene_end')
plt.legend()
plt.show()







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