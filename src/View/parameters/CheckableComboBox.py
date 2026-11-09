from PyQt6.QtWidgets import QWidget, QComboBox, QListView

class CheckableComboBox(QComboBox):

    def __init__(self, parent: QWidget):
        super.__init__(self, parent)

    