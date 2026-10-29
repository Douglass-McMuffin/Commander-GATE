# DistributionPopup.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.Control.ControlAPI import ControlAPI
from src.View.helper.PopupsHelper import PopupsHelper

class DigitizerPopup(QDialog):
    def __init__(self, parent, on_create=None, on_create_args = []):
        """
        Create the DigitizerPopup handler.

        Args:
            parent: QWidget parent of the popup
            on_create: function to call when the digitizer is created 
            on_create_args: arguments to call the on_create function
        """
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Create Distribution")
        self.setMinimumSize(360, 180)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

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
        name_label = QLabel("Digitizer Name:")
        name_label.setFont(self.font)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. Singles")
        self.name_edit.setFont(self.font)
        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)

        # Type (immutable after creation — we’ll store it as a Label param on the child)
        type_label = QLabel("Digitizer Type:")
        type_label.setFont(self.font)
        self.type_combo = QComboBox()
        self.type_combo.setFont(self.font)
        self.type_combo.addItems(ControlAPI.getDigitizerTypes())
        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)

        # Type (immutable after creation — we’ll store it as a Label param on the child)
        detector_label = QLabel(":")
        detector_label.setFont(self.font)
        self.detector_combo = QComboBox()
        self.detector_combo.setFont(self.font)
        self.detector_combo.addItems(ControlAPI.getAttachedVolumes())
        layout.addWidget(detector_label)
        layout.addWidget(self.detector_combo)

        # Create
        create_btn = QPushButton("Create")
        create_btn.setFont(self.font)
        create_btn.clicked.connect(self._handle_create)
        layout.addWidget(create_btn)

    def _handle_create(self):
        """Create the digitizer gate object, call the on_create function and close the popup."""
        digitizerName = self.name_edit.text().strip() or "Singles"
        digitizerName = PopupsHelper.uniqueName(digitizerName, ControlAPI.getObjectNames("DIGITIZER"))


        digitizerType = self.type_combo.currentText()
        detectorName = self.detector_combo.currentText()

        if detectorName != "":
            ControlAPI.createDigitizer(detectorName, digitizerType, digitizerName)

        if self.on_create:
            self.on_create(*self.on_create_args)
        self.accept()