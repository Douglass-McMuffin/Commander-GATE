from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import src.View.StyleSheets as Style
from src.Control.ControlAPI import ControlAPI
from src.View.helper.PopupsHelper import PopupsHelper

class PhysicsProcessPopup(QDialog):
    def __init__(self, parent, on_create=None, on_create_args = []):
        """
        Create the DigitizerPopup handler.
        
        Args:
            parent: QWidget parent of the popup
            on_create: function to call when the digitizer is created 
            on_create_args: arguments to call the on_create function
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Physics Processes")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMinimumSize(600, 400)
        self.onCreateCallback = on_create
        self.onCreateCallbackArgs = on_create_args
        self.font_size = parent.font().pointSize()
        self.default_font = QFont("Arial", self.font_size)
        self.setStyleSheet(Style.LIGHT_MODE_STYLESHEET)
        self._build_ui()
    
    def _build_ui(self):
        """Build the User Interface for the popup."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel("Add a physics process:")
        label.setFont(self.default_font)
        layout.addWidget(label)

        label_font = QFont("Arial", self.font_size)
        # Section: Name
        name_label = QLabel("Object Name:")
        name_label.setFont(label_font)
        self.name_input = QLineEdit()
        self.name_input.setFont(label_font)
        self.name_input.setPlaceholderText("Enter object name")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        add_button = QPushButton("Add Process")
        add_button.setFont(self.default_font)
        add_button.setFixedHeight(self.font_size * 2)
        add_button.clicked.connect(self._handle_create)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def _handle_create(self):
        """Create the digitizer gate object, call the on_create function and close the popup."""
        physicsName = self.name_input.text().strip() or "process"
        physicsName = PopupsHelper.uniqueName(physicsName, ControlAPI.getObjectNames("PHYSICS"))
        
        ControlAPI.createProcess(physicsName)

        if self.onCreateCallback:
            self.onCreateCallback(*self.onCreateCallbackArgs)
        self.close()