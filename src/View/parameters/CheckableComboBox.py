from PyQt6.QtWidgets import QWidget, QComboBox, QListView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

class CheckableComboBox(QComboBox):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.setModel(QStandardItemModel(self))
        self.model().dataChanged.connect(self.updateText)

    def addItems(self, itemsList, checkedItemsList):
        for itemName in itemsList:
            item = QStandardItem()
            item.setText(itemName)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
            if itemName in checkedItemsList:
                item.setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
            else:
                item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
            self.model().appendRow(item)

        self.updateText()

    def updateText(self):
        # Collect text of all checked items
        selected_items = [
            self.model().item(i).text() 
            for i in range(self.model().rowCount()) 
            if self.model().item(i).checkState() == Qt.CheckState.Checked
        ]
        if len(selected_items) == 0:
            self.lineEdit().setText("Choose")
        elif len(selected_items) == 1:
            self.lineEdit().setText(selected_items[0])
        else:
            self.lineEdit().setText(selected_items[0] + ", ...")

