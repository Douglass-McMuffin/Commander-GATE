from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QListWidget, QListWidgetItem, QWidget, QSizePolicy, QScrollArea, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.View.StyleSheets import WORLD_OBJECT_WINDOW_STYLESHEET
from src.Control.ControlAPI import ControlAPI
from src.View.helper.PopupsHelper import PopupsHelper

class WorldObjectPopup(QDialog):
    def __init__(self, parent, parentObjectPath, on_create=None, on_create_args = []):
        """
        Create the DigitizerPopup handler.

        Args:
            parent: QWidget parent of the popup
            parentObjectPath: path of the gate object that is the parent of the new volume
            on_create: function to call when the digitizer is created 
            on_create_args: arguments to call the on_create function
        """
        super().__init__(parent)
        
        self.setModal(True)
        self.setWindowTitle("Create World Object")
        self.setMinimumSize(400, 200)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.volumeType = ControlAPI.getYamlUnits("VOLUME_TYPES")
        self.repeaterType = ControlAPI.getYamlUnits("REPEATER_TYPES")

        self.font_size = parent.font_size_slider.value()
        self.parentObjectPath = parentObjectPath
        self.onCreate = on_create
        self.onCreateArgs = on_create_args

        self._build_ui()
        self.create_button.clicked.connect(self._handle_create)

    def _build_ui(self):
        """Build the User Interface for the popup."""
        self.setStyleSheet(WORLD_OBJECT_WINDOW_STYLESHEET)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        label_font = QFont("Arial", self.font_size)

        # Section: Name
        name_label = QLabel("Object Name:")
        name_label.setFont(label_font)
        self.name_input = QLineEdit()
        self.name_input.setFont(label_font)
        self.name_input.setPlaceholderText("Enter object name")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        # Section: Shape
        shape_label = QLabel("Shape:")
        shape_label.setFont(label_font)
        self.shape_dropdown = QComboBox()
        self.shape_dropdown.setFont(label_font)
        self.shape_dropdown.addItems(self.volumeType)
        layout.addWidget(shape_label)
        layout.addWidget(self.shape_dropdown)

        # Section: Repeater
        repeater_label = QLabel("Repeater:")
        repeater_label.setFont(label_font)
        self.repeater_dropdown = QComboBox()
        self.repeater_dropdown.setFont(label_font)
        self.repeater_dropdown.addItems(self.repeaterType)
        layout.addWidget(repeater_label)
        layout.addWidget(self.repeater_dropdown)

        # Button
        self.create_button = QPushButton("Create")
        self.create_button.setFont(label_font)
        layout.addWidget(self.create_button)

    def _handle_create(self):
        """Create the digitizer gate object, call the on_create function and close the popup."""
        name = self.name_input.text().strip() or "volumeChild"
        name = PopupsHelper.uniqueName(name, ControlAPI.getObjectNames("WORLD"))
        volumeType = self.shape_dropdown.currentText()
        repeaterType = self.repeater_dropdown.currentText()

        ControlAPI.createGateVolumeChild(self.parentObjectPath, name, volumeType, repeaterType)

        if self.onCreate:
            self.onCreate(*self.onCreateArgs)
        self.accept()