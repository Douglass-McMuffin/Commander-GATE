from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.Model.StaticData.StaticData import SOURCE_TYPES
from src.Control.ControlAPI import ControlAPI
from src.View.helper.PopupsHelper import PopupsHelper

class SourcePopup(QDialog):
    def __init__(self, parent, on_create=None, on_create_args = []):
        """
        Create the DigitizerPopup handler.
        
        keyword arguments:
        parent -- QWidget parent of the popup
        on_create -- function to call when the digitizer is created 
        on_create_args -- arguments to call the on_create function
        """
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Add Source")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.onCreate = on_create
        self.onCreateArgs = on_create_args
        self.fs = parent.font_size_slider.value() if hasattr(parent, "font_size_slider") else 14
        
        self._build_ui()

    def _build_ui(self):
        """Build the User Interface for the popup."""
        lay = QVBoxLayout(self)
        name_lbl = QLabel("Source name:"); name_lbl.setFont(QFont("Arial", self.fs))
        self.name_in = QLineEdit(); self.name_in.setFont(QFont("Arial", self.fs))
        type_lbl = QLabel("Source type:"); type_lbl.setFont(QFont("Arial", self.fs))
        self.type_dd = QComboBox(); self.type_dd.addItems(SOURCE_TYPES); self.type_dd.setFont(QFont("Arial", self.fs))
        btn = QPushButton("Create"); btn.setFont(QFont("Arial", self.fs)); btn.clicked.connect(self._handle_create)

        for w in (name_lbl, self.name_in, type_lbl, self.type_dd, btn):
            lay.addWidget(w)

    def _handle_create(self):
        """Create the digitizer gate object, call the on_create function and close the popup."""
        sourceName = self.name_in.text().strip() or "sourceChild"
        sourceName = PopupsHelper.uniqueName(sourceName, ControlAPI.getObjectNames("SOURCE"))
        sourceType = self.type_dd.currentText()

        ControlAPI.createSource(sourceName, sourceType)

        if self.onCreate:
            self.onCreate(*self.onCreateArgs)
        self.accept()