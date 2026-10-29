from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListView, QLabel, QHBoxLayout, QLineEdit,
    QPushButton, QCheckBox, QSizePolicy, QFileDialog, QAbstractItemView, QComboBox
)
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem, QFontMetrics, QRegularExpressionValidator
from PyQt6.QtCore import Qt, QSize, QRegularExpression
from functools import partial

# Use your existing popups
from src.View.popups.PhysicsProcessPopup import PhysicsProcessPopup
from src.View.popups.SourcePopup import SourcePopup
from .header import create_header_section
from src.Model.StaticData.StaticData import SYSTEM_TYPES, SYSTEM_LEVELS_BY_TYPE, SYSTEM_LEVEL_SHAPES
from src.View.parameters.BigPopupCombo import BigPopupCombo
from src.View.parameters.ElidingLabel import ElidingLabel
from src.View.popups.DistributionsPopup import DistributionPopup
from src.View.popups.DigitizerPopup import DigitizerPopup
from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from src.Model.DynamicData.Interface.GateParameterInterface import GateParameterInterface
from src.Control.ControlAPI import ControlAPI

class InspectorSection:
    """
    Encapsulates the Inspector UI and logic. Keeps your look & behavior.
    Public API:
      - widget: container to add in layout
      - listview: QListView (for font update)
      - populate_parameters(item)  # mirrors your old method name/signature
      - resize_parameters(font_size)
    """
    
    def __init__(self, parent):
        """
        Create the inspector section.

        Args:
            parent: widget that holds the inspector section (Main Window)
        """
        self.host = parent
        self.widget = QWidget(parent)
        self.layout = QVBoxLayout(self.widget)

        self._seed_mode_dd = None
        self._seed_manual_edit = None

        self.label = create_header_section(self.widget, "Inspector View")
        self.layout.addWidget(self.label)

        self.listview = QListView()
        self.listview.setSpacing(0)
        self.layout.addWidget(self.listview)

        # Cache of inspector widgets for resize
        # Each entryL {"label": QLabel|None, "inputs": [widgets], "unit": QComboBox|None}
        self.inspector_widgets = []


    # --------------------------
    # Small helpers
    # --------------------------
    
    def _font(self, fs: int, bold: bool = False) -> QFont:
        """
        Get font widget

        Args:
            fs: font size
            bold: enable bold letters
        """
        return QFont("Arial", fs, QFont.Weight.Bold if bold else QFont.Weight.Normal)
    
    def _label_min_px(self, fs: int, ch: int = 32) -> int:
        """
        Get label minimal width in pixel

        Args:
            fs: font size
            ch: number of caracter
        """
        fm = QFontMetrics(self._font(fs))
        return int(ch * fm.horizontalAdvance("M"))
    
    def _std_label_width(self, fs: int) -> int:
        """
        Get standard label width

        Args:
            fs: font size
        """
        return 175 + fs * 6
    
    def _control_height(self, fs: int) -> int:
        """
        A control height based on font, with a floor

        Args:
            fs: font size
        """
        fm = QFontMetrics(self._font(fs))
        return max(24, fm.height() + 4)
    
    def _prepare_combo(self, cb: BigPopupCombo):
        """
        Setup the combo widget

        Args:
            cb: combo widget
        """
        cb.setMaxVisibleItems(20)
        view = QListView(cb)
        view.setUniformItemSizes(True)
        view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        cb.setView(view)
        
    def _combo(self, fs: int, items=None, width: int | None = None) -> BigPopupCombo:
        """
        Create the combo widget.

        Args:
            fs: font size
            items: list of items to put in the dropdown list
            width: custom width of the widget
        """
        dd = BigPopupCombo(popup_rows=14, min_chars=16)
        dd.setFont(self._font(fs))
        self._prepare_combo(dd)
        if items:
            dd.addItems(items)
        if width:
            dd.setFixedWidth(width)
        return dd
    
    def _button(self, text: str, fs: int, width: int | None, click):
        """
        Create the button widget.

        Args:
            text: label to display on the button
            fs: font size
            width: custom width of the widget
        """
        btn = QPushButton(text)
        btn.setFont(self._font(fs))
        if width:
            btn.setFixedWidth(width)
        btn.setStyleSheet("font-size: 18px; font-weight: bold; border: none; background: transparent;" if "➕" in text else "")
        btn.clicked.connect(click)
        return btn
    
    def _row_widget(self) -> tuple[QWidget, QHBoxLayout]:
        """Create a param row."""
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(1, 2, 1, 2)
        h.setSpacing(4)
        h.setAlignment(Qt.AlignmentFlag.AlignLeft)
        return row, h
    
    def _append_widget_row(self, model: QStandardItemModel, widget: QWidget, fs: int, vpad: int = 6, spacer: int = 1):
        """
        Add a param row to a model.

        Args:
            model: model to which the param row will be added
            widget: param row
            fs: font size
            vpad: vertical padding on the row
            spacer: number of empty row to add after
        """
        row_item = QStandardItem()
        model.appendRow(row_item)
        self.listview.setIndexWidget(row_item.index(), widget)
        self._apply_row_height(row_item, widget, fs, vpad=vpad)
        if spacer:
            self._add_spacer(model, spacer)
        
    def apply_font(self, fs: int):
        """
        Apply the font to the section.

        Args:
            fs: font size
        """
        base = self._font(fs)
        self.widget.setFont(base)
        self.listview.setFont(base)
        self.label.setFont(self._font(fs, bold=True))

    
    # -----------------------------
    # Main population
    # -----------------------------
    def populate_parameters(self, item):
        """
        Refresh the parameters in the inspector section with the current selected item from the hierarchy section.

        Args:
            item: selected item from the hierarchy section
        """
        if not item:
            return
        gateObjectPath: str = item.data(0, Qt.ItemDataRole.UserRole)
        gateObject : GateObjectInterface = ControlAPI.getGateObject(gateObjectPath)

        # reset model + cache
        verticalScrollValue = self.listview.verticalScrollBar().value()
        self.inspector_widgets = []
        model: QStandardItemModel = self.listview.model()
        if model:
            model.clear()
        else:
            model = QStandardItemModel()

        self.listview.setModel(model)
        font_size = self.host.font_size_slider.value()

        # header
        self._add_header(model, gateObject)
        

        # special rows
        self._maybe_add_physics_plus(model, gateObject, font_size)
        self._maybe_add_source_plus(model, gateObject, font_size)
        self._maybe_add_distributions_plus(model, gateObject,font_size)
        self._maybe_add_digitizer_plus(model, gateObject,font_size)
        self._maybe_add_rename(model, gateObject, font_size)
        #self._maybe_add_role(model, gateObject, font_size)
        #self._maybe_add_system_root_row(model, gateObject, font_size)
        self._maybe_add_attach_row(model, gateObject, font_size)
        
        if getattr(gateObject, "path", "") == "/gate/source":
            self._maybe_add_source_controls(model, item, gateObject, font_size)

        # parameters
        self._add_parameters_block(model, gateObject, font_size)
        #self._sync_seed_manual_state()

        # final pass for sizing
        self.resize_parameters(font_size)

        # Getting the vertical scroll back
        self.listview.verticalScrollBar().setValue(verticalScrollValue)

        # Update layout
        # model.layoutChanged.emit()
        
    
    
    # -----------------------------
    # Header and section labels
    # -----------------------------
    def _add_header(self, model: QStandardItemModel, gate_object: GateObjectInterface):
        """
        Add header rows to the inspector section.

        Args:
            model: model of the inspector section
            gate_object: gate object with that is selected from the hierarchy section
        """
        model.appendRow(QStandardItem(f"Object: {gate_object.name}"))
        
    def _add_section_label(self, model: QStandardItemModel, title: str, font_size: int):
        """
        Add title label to seperate different section of the param rows.

        Args:
            model: model of the inspector section
            title: title of the section
            font_size: font size
        """
        label_item = QStandardItem()
        label = ElidingLabel(title)
        label.setFont(self._font(font_size, bold=True))
        label.setStyleSheet("color: black; background-color: #e0e0e0; padding: 4px;")
        model.appendRow(label_item)
        self.listview.setIndexWidget(label_item.index(), label)
        self._apply_row_height(label_item, label, font_size, vpad=4)
    

    # -----------------------------
    # Special rows (physics/source/etc.)
    # -----------------------------

    def _maybe_add_physics_plus(self, model: QStandardItemModel, gate_object: GateObjectInterface, font_size: int):
        """
        Add the creation button for the physics folder.

        Args:
            model: model of the inspector section
            gate_object: gate object associated with the current selected item
            font_size: font size
        """
        if gate_object.path != ControlAPI.getObjectPath("PHYSICS"):
            return
        
        btn = self._button("➕", font_size, 40, click=lambda: PhysicsProcessPopup(
            self.host, self.host.populate_hierarchy_tree, [self.host.cManager.node_tree]
            ).exec())
        self._append_widget_row(model, btn, font_size)
        
        
    def _maybe_add_source_plus(self, model: QStandardItemModel, gate_object: GateObjectInterface, font_size: int):
        """
        Add the creation button for the source folder.
        
        Args:
            model: model of the inspector section
            gate_object: gate object associated with the current selected item
            font_size: font size
        """
        if gate_object.path != ControlAPI.getObjectPath("SOURCE"):
            return
        btn = self._button( "Add ➕", font_size, 120, click=lambda: SourcePopup(
            self.host, lambda: self.host.populate_hierarchy_tree(self.host.cManager.node_tree)
            ).exec()
        )
        
        self._append_widget_row(model, btn, font_size)
        
    def _maybe_add_distributions_plus(self, model: QStandardItemModel, gate_object: GateObjectInterface, font_size: int):
        """
        Add the creation button for the distributions folder.
        
        Args:
            model: model of the inspector section
            gate_object: gate object associated with the current selected item
            font_size: font size
        """
        if gate_object.path != ControlAPI.getObjectPath("DISTRIBUTIONS"):
            return
        btn = self._button( "Add ➕", font_size, 120, click=lambda: DistributionPopup(
            self.host, self.host.populate_hierarchy_tree, [self.host.cManager.node_tree]
            ).exec()
        )
        self._append_widget_row(model, btn, font_size)

    def _maybe_add_digitizer_plus(self, model: QStandardItemModel, gate_object: GateObjectInterface, font_size: int):
        """
        Add the creation button for the digitizer folder.
        
        Args:
            model: model of the inspector section
            gate_object: gate object associated with the current selected item
            font_size: font size
        """
        if gate_object.path != ControlAPI.getObjectPath("DIGITIZER"):
            return
        btn = self._button( "Add ➕", font_size, 120, click=lambda: DigitizerPopup(
            self.host, self.host.populate_hierarchy_tree, [self.host.cManager.node_tree]
            ).exec()
        )
        self._append_widget_row(model, btn, font_size)

    def _maybe_add_rename(self, model: QStandardItemModel, gate_object: GateObjectInterface, font_size: int):
        """
        Add the text input to rename the item.
        
        Args:
            model: model of the inspector section
            gate_object: gate object associated with the current selected item
            font_size: font size
        """
        pathToken = gate_object.path.split("/")[1:]
        if len(pathToken) == 1 or (pathToken[0] == "gate" and len(pathToken) == 2):
            return
        widget = self._build_rename_row(gate_object, font_size)
        self._append_widget_row(model, widget, font_size)


    def _maybe_add_role(self, model: QStandardItemModel, gate_object: GateObjectInterface, font_size: int):
        """
        (DEPRECATED) Add the text input to choose the role for selected the item.
        
        Args:
            model: model of the inspector section
            gate_object: gate object associated with the current selected item
            font_size: font size
        """
        if not getattr(gate_object, "parent", None) or gate_object.parent.name != "world":
            return
        widget = self._build_role_row(gate_object, font_size)
        self._append_widget_row(model, widget, font_size)
        

    def _maybe_add_system_root_row(self, model: QStandardItemModel, gate_object: GateObjectInterface, font_size: int):
        """
        (DEPRECATED) Add the text input to enable system root for selected the item.
        
        Args:
            model: model of the inspector section
            gate_object: gate object associated with the current selected item
            font_size: font size
        """
        # Only direct daughters of world can become a "system root"
        if not getattr(gate_object, "parent", None) or gate_object.parent.name != "world":
            return
        row, h = self._row_widget()

        lbl = ElidingLabel("System:")
        lbl.setFont(QFont("Arial", font_size))
        lbl.setMinimumWidth(self._label_min_px(font_size))
        
        cb = QCheckBox("Mark as system root")
        cb.setChecked(bool(getattr(gate_object, "system_type", None)))

        dd = self._combo(font_size)
        dd.addItems(SYSTEM_TYPES)
        #self._prepare_combo(dd)
        if getattr(gate_object, "system_type", None) in SYSTEM_TYPES:
            dd.setCurrentText(gate_object.system_type)

        def set_root_enabled(st):
            if st == Qt.CheckState.Checked.value:
                # ensure model has helpers on object
                if not hasattr(gate_object, "set_system_root"):
                    gate_object.set_system_root = lambda sys_type: setattr(gate_object, "system_type", sys_type)
                gate_object.set_system_root(dd.currentText())
            else:
                gate_object.system_type = None

        cb.stateChanged.connect(set_root_enabled)
        dd.currentTextChanged.connect(lambda v: gate_object.set_system_root(v) if cb.isChecked() else None)

        h.addWidget(lbl)
        h.addWidget(cb)
        h.addWidget(dd)
        self._append_widget_row(model, row, font_size)

    def _maybe_add_attach_row(self, model: QStandardItemModel, gate_object: GateObjectInterface, font_size: int):
        """
        (DEPRECATED) Add the dropdown input row to attach volume for selected the item.
        
        Args:
            model: model of the inspector section
            gate_object: gate object associated with the current selected item
            font_size: font size
        """
        systems = self._all_system_roots()
        if not systems or gate_object.name == "gate" or not self._is_under_world(gate_object):
            return

        row, h = self._row_widget()
    
        lbl = ElidingLabel("Attach to system:");
        lbl.setFont(QFont("Arial", font_size));
        lbl.setMinimumWidth(self._label_min_px(font_size))

        sys_dd = self._combo(font_size, width=220 + font_size * 2)
        sys_dd.addItem(" - ")
        for s in systems:
            sys_dd.addItem(s.system_name if hasattr(s, "system_name") else s.get_name())
        if getattr(gate_object, "system_name", None):
            sys_dd.setCurrentText(gate_object.system_name)

        level_dd = self._combo(font_size)

        def refresh_levels():
            """(DEPRECATED) Refresh the levels of the attached volume."""

            name = sys_dd.currentText()
            if name.strip() in {"-", " - "}:
                level_dd.clear(); return
            sys_obj = next((s for s in systems if (getattr(s, "system_name", s.get_name()) == name)), None)
            level_dd.clear()
            if sys_obj:
                for lvl in SYSTEM_LEVELS_BY_TYPE.get(getattr(sys_obj, "system_type", None), []):
                    level_dd.addItem(lvl)
                if getattr(gate_object, "system_level", None) in [level_dd.itemText(i) for i in range(level_dd.count())]:
                    level_dd.setCurrentText(gate_object.system_level)

        refresh_levels()
        sys_dd.currentTextChanged.connect(lambda _: refresh_levels())

        def apply_attach():
            """(DEPRECATED) Apply the attached volume configuration"""

            name = sys_dd.currentText()
            if name.strip() in {"-", " - "}:
                gate_object.system_name = None; gate_object.system_level = None; return
            level = level_dd.currentText() or None
            if not hasattr(gate_object, "attach_to_system"):
                gate_object.attach_to_system = lambda nm, lv: (setattr(gate_object, "system_name", nm),
                                                            setattr(gate_object, "system_level", lv))
            gate_object.attach_to_system(name, level)
            # optional hint
            sys_type = None
            for s in systems:
                if getattr(s, "system_name", s.get_name()) == name:
                    sys_type = getattr(s, "system_type", None); break
            hint = self._shape_hint_text(gate_object, sys_type, level or "")
            if hint: self.host.write_to_console(f"Note: {hint}")

        sys_dd.currentTextChanged.connect(lambda _: apply_attach())
        level_dd.currentTextChanged.connect(lambda _: apply_attach())

        h.addWidget(lbl); h.addWidget(sys_dd); h.addWidget(level_dd)
        self._append_widget_row(model, row, font_size)
    
    
    # -----------------------------
    # Parameters block
    # -----------------------------    
    def _add_parameters_block(self, model: QStandardItemModel, gateObject: GateObjectInterface, fontSize: int):
        """
        Add the all the parameters in the section for selected the item.
        
        Args:
            model: model of the inspector section
            gateObject: gate object associated with the current selected item
            fontSize: font size
        """
        for param in gateObject.param.values():
            # one param row
            if param.inputType in ("label", "dynamic_label"):
                self._add_section_label(model, param.displayedLabel, fontSize)
            elif param.inputType not in ("macro"):              
                row_widget = self._build_param_row(gateObject.path, param, fontSize)
                self._append_widget_row(model, row_widget, fontSize)

    def _build_param_row(self, objectPath: str, param: GateParameterInterface, fontSize: int) -> QWidget:
        """
        Arrange the label, input et if needed the unit in the section for selected the item.
        
        Args:
            objectPath: path to the object selected in the hierarchy section
            param: gate parameter representing the parameter row
            fontSize: font size
        """
        row, h = self._row_widget()
        
        label = ElidingLabel(param.displayedLabel)
        label.setFont(self._font(fontSize))
        label.setMinimumWidth(self._label_min_px(fontSize))
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        h.addWidget(label)
        
        inputs = []
        for i in range(len(param.valueList)):
            w = self._build_input_widget(objectPath, param, i, fontSize)
            w.setFont(QFont("Arial", fontSize))
            h.addWidget(w, 0)
            inputs.append(w)
        
        unit_dd = None
        if getattr(param, "unitList", None) and param.inputType == "text":
            unit_dd = self._combo(fontSize, items=param.unitList, width=100)
            default_index = param.defaultUnitIndex
            unit_dd.setCurrentIndex(default_index)
            unit_dd.currentIndexChanged.connect(lambda index, p=param: ControlAPI.updateGateParamUnitIndex(objectPath, param.displayedLabel, index))
            h.addWidget(unit_dd)
        
        self.inspector_widgets.append({"label":label, "inputs":inputs, "unit":unit_dd})
        return row

    def _build_input_widget(self, objectPath: str, param: GateParameterInterface, fieldIndex: int, fontSize: int):
        """
        Choose the constructor depending on the parameter's input type.

        Args:
            objectPath: path to the object selected in the hierarchy section
            param: gate parameter representing the parameter row
            fieldIndex: index of the value field (There can be multiple field possible, but generally, there is only one -> fieldIndex = 0)
            fontSize: font size
        """

        buildWidget = {
            "text": self._build_text_widget,
            "dropdown": self._build_dropdown_widget,
            "macro_dropdown": self._build_dropdown_widget,
            "dynamic_dropdown": self._build_dropdown_widget,
            "checkbox": self._build_checkbox_widget,
            "select": self._build_select_widget,
            "object_name_dropdown": self._build_dropdown_widget,
            "children_name_dropdown": self._build_dropdown_widget,
            "attached_volume_dropdown": self._build_dropdown_widget,
            "digitizer_detector_dropdown": self._build_dropdown_widget,
            "dynamic_object_name_dropdown": self._build_dropdown_widget
        }

        return buildWidget[param.inputType](objectPath, param, fieldIndex, fontSize)

    def _build_text_widget(self, objectPath: str, param: GateParameterInterface, fieldIndex: int, fontSize: int):
        """
        Build the text input widget.
        
        Args:
            objectPath: path to the object selected in the hierarchy section
            param: gate parameter representing the parameter row
            fieldIndex: index of the value field (There can be multiple field possible, but generally, there is only one -> fieldIndex = 0)
            fontSize: font size
        """
        w = QLineEdit()
        w.setText(str(param.valueList[fieldIndex]))
        w.setFixedWidth(60 + fontSize)
        regex = QRegularExpression("-?[0-9]+(.[0-9]+)?")
        validator = QRegularExpressionValidator(regex)
        w.setValidator(validator)
        w.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        w._edited = False
        w.textEdited.connect(lambda _: setattr(w, "_edited", True))
        w.editingFinished.connect(lambda: 
                              self.updateParamTextValue(w, objectPath, param.displayedLabel, fieldIndex, w.text()))
        return w

    def _build_dropdown_widget(self, objectPath: str, param: GateParameterInterface, fieldIndex: int, fontSize: int):
        """
        Build the dropdown input widget.
        
        Args:
            objectPath: path to the object selected in the hierarchy section
            param: gate parameter representing the parameter row
            fieldIndex: index of the value field (There can be multiple field possible, but generally, there is only one -> fieldIndex = 0)
            fontSize: font size
        """
        w = self._combo(fontSize, items=param.unitList or [], width=100)
        w.setCurrentIndex(param.unitList.index(param.valueList[fieldIndex]))
        w.currentIndexChanged.connect(lambda index:
                                      self.updateParamValue(objectPath, param.displayedLabel, fieldIndex, param.unitList[index]))
        w.setFixedWidth(120 + fontSize * 2)
        return w

    def _build_checkbox_widget(self, objectPath: str, param: GateParameterInterface, fieldIndex: int, fontSize):
        """
        Build the checkbox input widget.
        
        Args:
            objectPath: path to the object selected in the hierarchy section
            param: gate parameter representing the parameter row
            fieldIndex: index of the value field (There can be multiple field possible, but generally, there is only one -> fieldIndex = 0)
            fontSize: font size
        """
        w = QCheckBox()
        w.setChecked(param.valueList[fieldIndex])
        w.stateChanged.connect(lambda state: 
                               self.updateParamValue(objectPath, param.displayedLabel, fieldIndex, str(state == Qt.CheckState.Checked.value)))
        return w

    def _build_select_widget(self, objectPath: str, param: GateParameterInterface, fieldIndex: int, fontSize):
        """
        Build the select input widget.
        
        Args:
            objectPath: path to the object selected in the hierarchy section
            param: gate parameter representing the parameter row
            fieldIndex: index of the value field (There can be multiple field possible, but generally, there is only one -> fieldIndex = 0)
            fontSize: font size
        """
        selectValue = param.valueList[fieldIndex]
        if (selectValue == None):
            w = self._button("Browse...", fontSize, 200,
                            click=(lambda _, objectPath=objectPath, paramLabel=param.displayedLabel, fieldIndex=fieldIndex: 
                                   self.browse_file_for_param(w, objectPath, paramLabel, fieldIndex)))
        else:
            w = self._button(selectValue, fontSize, 200,
                            click=(lambda _, objectPath=objectPath, paramLabel=param.displayedLabel, fieldIndex=fieldIndex: 
                                   self.browse_file_for_param(w, objectPath, paramLabel, fieldIndex)))
            w.setStyleSheet("text-align: right;")
        
        return w
    
    
    # -----------------------------
    # Utility actions
    # -----------------------------
    def updateView(self, item):
        """
        Refresh view of hierarchy and inspector sections.

        Args:
            item: currently selected item from the hierarchy section
        """
        self.host.populate_hierarchy_tree(self.host.cManager.node_tree)
        self.populate_parameters(item)

    def updateParamValue(self, objectPath: str, paramName: str, fieldIndex: int, value: str):
        """
        Update data model with user selected value.
        
        Args:
            objectPath: path to the object selected in the hierarchy section
            paramName: displayed label of the parameter in which the value is changed
            fieldIndex: index of the value field (There can be multiple field possible, but generally, there is only one -> fieldIndex = 0)
            value: new value
        """
        ControlAPI.updateGateParamValue(objectPath, paramName, fieldIndex, value)
        self.updateView(self.host.hierarchySection._find_tree_child(objectPath))

    
    def updateParamTextValue(self, widget, objectPath: str, paramName: str, fieldIndex: int, value: str):
        """
        Update data model with user selected value.
        
        Args:
            widget: text widget that had its value changed
            objectPath: path to the object selected in the hierarchy section
            paramName: displayed label of the parameter in which the value is changed
            fieldIndex: index of the value field (There can be multiple field possible, but generally, there is only one -> fieldIndex = 0)
            value: new value
        """
        if widget._edited == True:
            widget._edited = False
            ControlAPI.updateGateParamValue(objectPath, paramName, fieldIndex, value)
            self.updateView(self.host.hierarchySection._find_tree_child(objectPath))


    def browse_file_for_param(self, button, objectPath: str, paramName: str, fieldIndex: int):
        """
        Execute a dialog window to select a file.

        Args:
            button: select widget
            objectPath: path to the object selected in the hierarchy section
            paramName: displayed label of the parameter in which the value is changed
            fieldIndex: index of the value field (There can be multiple field possible, but generally, there is only one -> fieldIndex = 0)
            
        """
        dlg = QFileDialog()
        dlg.setWindowTitle("Select a File")
        dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
        if dlg.exec():
            selected_file = dlg.selectedFiles()[0]
            ControlAPI.updateGateParamValue(objectPath, paramName, fieldIndex, selected_file)
            button.setText(selected_file)
            button.setStyleSheet("text-align: right;")
            self.host.write_to_console(f"Selected file for {paramName}: {selected_file}")
            self.host.populate_hierarchy_tree(self.host.cManager.node_tree)
            self.populate_parameters(self.host.hierarchySection._find_tree_child(objectPath))
    
    
    # -----------------------------
    # Rename / Role rows
    # -----------------------------
    def _build_rename_row(self, gate_object: GateObjectInterface, font_size):
        """
        Build the rename row in the inspector section

        Args:
            gate_object: gate object associated with the item currently selected in the hierarchy section
            font_size: font size
        """
        row, h = self._row_widget()

        lbl = ElidingLabel("Object Name:")
        lbl.setFont(self._font(font_size))
        lbl.setMinimumWidth(self._label_min_px(font_size))
        lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        name_input = QLineEdit()
        name_input.setFont(self._font(font_size))
        name_input.setText(gate_object.name)
        name_input.setFixedHeight(int(font_size * 1.8) - 4)
        name_input.setFixedWidth(170 + (font_size * 2))
        name_input.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        apply_btn = QPushButton("Apply")
        apply_btn.setFont(self._font(font_size))
        apply_btn.setFixedHeight(int(font_size * 1.8) - 4)
        apply_btn.setFixedWidth(70 + font_size)
        apply_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        apply_btn.clicked.connect(lambda: self.rename_gate_object(gate_object, name_input.text()))

        h.addWidget(lbl)
        h.addWidget(name_input)
        h.addWidget(apply_btn)
        h.addStretch(1)
        return row
    
    def _build_role_row(self, gate_object: GateObjectInterface, font_size):
        """
        (DEPRECATED) Build the role attribution row in the inspector section
        
        Args:
            gate_object: gate object associated with the item currently selected in the hierarchy section
            font_size: font size
        """
        row, h = self._row_widget()

        lbl = ElidingLabel("Object Role: ")
        lbl.setFont(self._font(font_size))
        lbl.setMinimumWidth(self._label_min_px(font_size))
        lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        dd = self._combo(font_size, width=170 + font_size * 2)
        siblings = gate_object.parent.children if gate_object.parent else []
        existing_roles = [obj.role for obj in siblings if obj != gate_object]

        dd.addItem(" - ")
        if "Scanner" not in existing_roles:
            dd.addItem("Scanner")
        if "Phantom" not in existing_roles:
            dd.addItem("Phantom")

        dd.setCurrentText(gate_object.name or " - ")
        dd.currentTextChanged.connect(lambda v: setattr(gate_object, "role", v if v != " - " else None))

        h.addWidget(lbl); h.addWidget(dd)
        return row
    
    
    def rename_gate_object(self, gate_object: GateObjectInterface, new_name):
        """
        Rename gate object and verify that is it a unique name
        
        Args:
            gate_object: gate object associated with the item currently selected in the hierarchy section
            font_size: font size
        """
        existing_names = set()
        root = self.host.hierarchySection.tree.invisibleRootItem()
        for i in range(root.childCount()):
            existing_names.add(root.child(i).text(0))

        unique_name = new_name
        if new_name in existing_names and gate_object.name != new_name:
            i = 1
            while f"{new_name}{i}" in existing_names:
                i += 1
            unique_name = f"{new_name}{i}"

        ControlAPI.setGateObjectName(gate_object.path, new_name)
        selected_item = self.host.hierarchySection.tree.currentItem()
        if selected_item:
            selected_item.setText(0, unique_name)
        self.host.write_to_console(f"Renamed object to: {unique_name}")
    
    # -----------------------------
    # Source helpers
    # -----------------------------
    def _maybe_add_source_controls(self, model, item, src_obj: GateObjectInterface, font_size):   
        """
        (DEPRECATED) Add the source controls in the current item selected

        Args:
            model: model of the inspector section
            item: current selected item
            src_obj: gate object associated with the current selected item
            font_size: font size
        """ 
        row, h = self._row_widget()

        lbl = ElidingLabel("Attach to volume:")
        lbl.setFont(self._font(font_size))
        lbl.setMinimumWidth(self._label_min_px(font_size))

        dd = self._combo(font_size, width=240 + font_size * 2)
        dd.addItem(" - ")
        for name in ControlAPI.getObjectNames(ControlAPI.getObjectPath("WORLD")):
            dd.addItem(name)

        attach_param = next((p for p in src_obj.param.values() if p.path.endswith("/attachTo")), None)
        current_attach = (attach_param.default_value_list[0] if (attach_param and attach_param.default_value_list) else "")
        if current_attach and dd.findText(current_attach) != -1:
            dd.setCurrentText(current_attach)

        def on_attach_changed(txt):
            if attach_param:
                attach_param.default_value_list = ["" if txt.strip() in ("", "-", " - ") else txt]

        dd.currentTextChanged.connect(on_attach_changed)

        # Delete button for this source
        del_btn = QPushButton("Delete Source")
        del_btn.setFont(self._font(font_size))
        del_btn.setFixedWidth(160)
        del_btn.clicked.connect(lambda: self._delete_source(item, src_obj))

        h.addWidget(lbl)
        h.addWidget(dd)
        h.addWidget(del_btn)
        self._append_widget_row(model, row, font_size)
    
    
    def _delete_source(self, item, src_obj: GateObjectInterface):
        """
        (DEPRECATED) Delete the source selected
        
        Args:
            model: model of the inspector section
            item: current selected item
            src_obj: gate object associated with the current selected item
        """ 
        # Remove from GateObject parent
        parent_obj: GateObjectInterface = getattr(src_obj, "parent", None)
        if parent_obj and hasattr(parent_obj, "daughters"):
            try:
                parent_obj.children.remove(src_obj)
            except ValueError:
                pass

        # REmove from the QTreeWidget
        tree = self.host.hierarchySection.tree
        # 'item' here is the QTreeWidgetItem passed from populate_parameters; if not, find it:
        qt_item = item if hasattr(item, "data") else tree.currentItem()
        if qt_item and qt_item.parent():
            parent_qt = qt_item.parent()
            parent_qt.removeChild(qt_item)
        elif qt_item:
            # top-level under /source
            idx = tree.indexOfTopLevelItem(qt_item)
            if idx >= 0:
                tree.takeTopLevelItem(idx)

        # Clear inspector
        self.listview.setModel(QStandardItemModel())

        # Console note
        self.host.write_to_console(f"Deleted source '{src_obj.name}'.")
    
    # -----------------------------
    # Misc utilities
    # -----------------------------
    def _add_spacer(self, model, height=1):
        """
        Add an empty row to the model

        Args:
            model: model of the inspector section
            height: height padding
        """
        s = QStandardItem(); 
        s.setSizeHint(QSize(10, height)); 
        s.setEditable(False)
        s.setEnabled(False)
        model.appendRow(s)
        
    def _all_system_roots(self):
        """(DEPRECATED) return all the systems roots of the project"""
        # Scan the current tree for objects with system_type set
        systems = []
        tree = self.host.hierarchySection.tree
        root = tree.invisibleRootItem()
        def walk(item):
            objPath: str = item.data(0, Qt.ItemDataRole.UserRole)
            obj = ControlAPI.getGateObject(objPath)
            if obj and getattr(obj, "system_type", None):
                systems.append(obj)
            for i in range(item.childCount()):
                walk(item.child(i))
        for i in range(root.childCount()):
            walk(root.child(i))
        return systems 
        
    def _shape_hint_text(self, gate_object: GateObjectInterface, system_type, level):
        """
        (DEPRECATED) Get the shape of the volume

        Args:
            gate_object: gate object associated with the current selected item
            system_type: type of system (See Gate documentation to see a list of system type)
            level: depth of the level of the system
        """
        from Classes.StaticData import SYSTEM_LEVEL_SHAPES
        required = SYSTEM_LEVEL_SHAPES.get(system_type, {}).get(level, "any")
        if required == "any":
            return None
        
        if "cylinder" in gate_object.path:
            shape = "cylinder"
        elif "wedge" in gate_object.path:
            shape = "wedge"
        else:
            shape = "box"
        if shape != required:
            return f"Recommended shape for {system_type}:{level} is '{required}', current looks like '{shape}'."
        return None
    
    def _is_under_world(self, obj: GateObjectInterface) -> bool:
        """
        (DEPRECATED) Is true if the gate object is under the world object.
        
        Args:
            obj: gate object associated with the current selected item
        """
        p = getattr(obj, "parent", None)
        while p:
            if p.name == "world":
                return True
            p = getattr(p, "parent", None)
        return False
    
    
    def _sync_seed_manual_state(self):
        """(DEPRECATED) Update the seed parameter."""
        if not self._seed_manual_edit:
            return
        mode = (self._seed_mode_dd.currentText() if self._seed_mode_dd else "").strip().lower()
        is_manual = (mode == "manual")
        self._seed_manual_edit.setEnabled(is_manual)
        if is_manual:
            self._seed_manual_edit.setStyleSheet("")
            self._seed_manual_edit.setToolTip("Enter a seed (0 … 900000000)")
        else:
            self._seed_manual_edit.setStyleSheet("QLineEdit { color: palette(mid); }")
            self._seed_manual_edit.setToolTip("Switch Seed mode to 'manual' to edit")
            
    
    def _apply_row_height(self, std_item, row_widget, fs: int, vpad: int = 6):
        """
        Make the row and all its children tall enough so nothing clips.
        
        Args:
            std_item: current item selected
            row_widget: row widget
            fs: font size
            vpad: vertical padding
        """
        h = self._control_height(fs)

        # controls
        for w in row_widget.findChildren(QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly):
            if isinstance(w, QAbstractItemView):
                continue
            if hasattr(w, "setFixedHeight"):
                w.setFixedHeight(h)
                
        # row item height (this is what prevents clipping)
        std_item.setSizeHint(QSize(1, h + vpad))  # width is ignored by QListView
    
    
    # -----------------------------
    # Resizing (public API)
    # -----------------------------
    def resize_parameters(self, font_size: int):
        """
        Resize parameters of the inspector section

        Args:
            font_size: font size
        """
        if not self.inspector_widgets:
            return
        
        def _text_width(fs: int) -> int: return 120 + (fs * 2)
        def _dd_width(fs: int)   -> int: return 220 + (fs * 2)

        for entry in self.inspector_widgets:
            # ---- normalize entry  ----
            if isinstance(entry, dict):
                label   = entry.get("label")
                inputs  = entry.get("inputs") or []
                unit_dd = entry.get("unit")
            else:
                label   = entry[0] if len(entry) > 0 else None
                second  = entry[1] if len(entry) > 1 else None
                unit_dd = entry[2] if len(entry) > 2 else None
                if isinstance(second, (list, tuple)):
                    inputs = list(second)
                elif second is None:
                    inputs = []
                else:
                    inputs = [second]

            # ---- label sizing ----
            if isinstance(label, QLabel):
                label.setFont(QFont(label.font().family(), font_size))
                if hasattr(self, "_label_min_px"):
                    label.setMinimumWidth(self._label_min_px(font_size))

            # ---- input widgets ----
            for w in inputs:
                if not w:
                    continue
                w.setFont(QFont(w.font().family(), font_size))

                # consistent widths per type
                if isinstance(w, QLineEdit):
                    w.setFixedWidth(_text_width(font_size))
                    w.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                elif isinstance(w, (QComboBox, BigPopupCombo)):
                    w.setFixedWidth(_dd_width(font_size))
                elif isinstance(w, QCheckBox):
                    w.setStyleSheet("")
                elif isinstance(w, QPushButton):
                    w.setFixedWidth(_dd_width(font_size))

            # ---- unit dropdown  ----
            if isinstance(unit_dd, BigPopupCombo):
                unit_dd.setFont(QFont("Arial", font_size))
                unit_dd.setFixedWidth(90 + (font_size // 2))
                self._prepare_combo(unit_dd)

        # ---- row heights ----
        row_h = self._control_height(font_size)
        for entry in self.inspector_widgets:
            # apply height to all widgets
            if isinstance(entry, dict):
                widgets = [entry.get("label")] + (entry.get("inputs") or []) + [entry.get("unit")]
            else:
                second = entry[1] if len(entry) > 1 else None
                if isinstance(second, (list, tuple)):
                    widgets = [entry[0]] + list(second) + ([entry[2]] if len(entry) > 2 else [])
                else:
                    widgets = [entry[0], second, entry[2] if len(entry) > 2 else None]

            for w in widgets:
                if w and hasattr(w, "setFixedHeight"):
                    w.setFixedHeight(row_h)

        # normalize QListView row heights to fix the clipping
        model = self.listview.model()
        if model:
            vpad = 4
            for r in range(model.rowCount()):
                it = model.item(r)
                if it is not None:
                    sh = it.sizeHint()
                    it.setSizeHint(QSize(sh.width(), row_h + vpad))
    
