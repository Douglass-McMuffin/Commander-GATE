from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.Model.StaticData.StaticData import PHYSICS_PROCESSES
from src.Model.DynamicData.Concreate.GateParameter import GateParameter
import src.View.StyleSheets as Style
from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from src.Control.ControlAPI import ControlAPI

class PhysicsProcessPopup(QDialog):
    def __init__(self, parent, existingNames: list[str], onChangeCallback):
        super().__init__(parent)
        self.setWindowTitle("Edit Physics Processes")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMinimumSize(600, 400)
        self.existingNames = existingNames
        self.onChangeCallback = onChangeCallback
        self.font_size = parent.font().pointSize()
        self.default_font = QFont("Arial", self.font_size)
        self.setStyleSheet(Style.LIGHT_MODE_STYLESHEET)
        self.init_ui()
    
    def init_ui(self):
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
        add_button.clicked.connect(self.add_process)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def _styled_label(self, text):
        label = QLabel(text)
        label.setFont(self.default_font)
        return label

    def _already_added(self, process_name):
        return any(param.path.endswith(process_name)
                   for param in self.physics_obj.param.values() if "Process" in param.displayedLabel)

    def _get_existing_processes(self):
        return [p.displayed_name.split(" ")[0]
                for p in self.physics_obj.param.values() if "Process" in p.displayedLabel]

    def add_process(self):
        name = self.name_input.text()
        if name in self.existingNames:
            i = 1
            newName = f"{name}{i}"
            while newName in self.existingNames:
                i += 1
                newName = f"{name}{i}"
            name = newName
        
        ControlAPI.createProcess(name)
        self.onChangeCallback()
        self.close()