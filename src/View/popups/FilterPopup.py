# DistributionPopup.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.Control.ControlAPI import ControlAPI
from src.View.helper.PopupsHelper import PopupsHelper

class FilterPopup(QDialog):
    def __init__(self, parent, actorName, on_create=None, on_create_args = []):
        """
        Create the FilterPopup handler.

        Args:
            parent: QWidget parent of the popup
            on_create: function to call when the digitizer is created 
            on_create_args: arguments to call the on_create function
        """
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Create Filter")
        self.setMinimumSize(360, 180)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.actorName = actorName
        self.on_create = on_create
        self.on_create_args = on_create_args

        font_size = getattr(parent, "font_size_slider", None)
        self.font = QFont("Arial", font_size.value() if font_size else 12)

        self._build_ui()

    def _build_ui(self):
        """Build the User Interface for the popup."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Name
        name_label = QLabel("Filter Name:")
        name_label.setFont(self.font)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. filterChild")
        self.name_edit.setFont(self.font)
        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)

        # Type (immutable after creation — we’ll store it as a Label param on the child)
        type_label = QLabel("Filter Type:")
        type_label.setFont(self.font)
        self.type_combo = QComboBox()
        self.type_combo.setFont(self.font)
        self.type_combo.addItems(ControlAPI.getFilterTypes())
        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)

        # Create
        create_btn = QPushButton("Create")
        create_btn.setFont(self.font)
        create_btn.clicked.connect(self._handle_create)
        layout.addWidget(create_btn)

    def _handle_create(self):
        """Create the filter gate object, call the on_create function and close the popup."""
        filterName = self.name_edit.text().strip() or "filterChild"
        filterName = PopupsHelper.uniqueName(filterName, ControlAPI.getObjectNames("/".join([ControlAPI.getObjectPath("ACTOR"), self.actorName])))


        filterType = self.type_combo.currentText()

        if filterName != "":
            ControlAPI.createFilter(self.actorName, filterName, filterType)

        if self.on_create:
            self.on_create(*self.on_create_args)
        self.accept()