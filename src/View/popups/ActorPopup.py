# DistributionPopup.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.Control.ControlAPI import ControlAPI
from src.View.helper.PopupsHelper import PopupsHelper

class ActorPopup(QDialog):
    def __init__(self, parent, on_create=None, on_create_args = []):
        """
        Create the ActorPopup handler.

        Args:
            parent: QWidget parent of the popup
            on_create: function to call when the digitizer is created 
            on_create_args: arguments to call the on_create function
        """
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Create Actor")
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
        name_label = QLabel("Actor Name:")
        name_label.setFont(self.font)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. actorChild")
        self.name_edit.setFont(self.font)
        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)

        # Type (immutable after creation — we’ll store it as a Label param on the child)
        type_label = QLabel("Actor Type:")
        type_label.setFont(self.font)
        self.type_combo = QComboBox()
        self.type_combo.setFont(self.font)
        self.type_combo.addItems(ControlAPI.getActorTypes())
        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)

        # Create
        create_btn = QPushButton("Create")
        create_btn.setFont(self.font)
        create_btn.clicked.connect(self._handle_create)
        layout.addWidget(create_btn)

    def _handle_create(self):
        """Create the actor gate object, call the on_create function and close the popup."""
        actorName = self.name_edit.text().strip() or "actorChild"
        actorName = PopupsHelper.uniqueName(actorName, ControlAPI.getObjectNames("ACTOR"))


        actorType = self.type_combo.currentText()

        if actorName != "":
            ControlAPI.createActor(actorName, actorType)

        if self.on_create:
            self.on_create(*self.on_create_args)
        self.accept()