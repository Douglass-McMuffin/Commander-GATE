from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics
from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from src.Control.ModelIteratorInterface import ModelIteratorInterface
from src.Control.ModelIterator import ModelIterator
from .header import create_header_section
from sys import stderr
from functools import partial

class HierarchySection:
    
    """
    Encapsulates the hierarchy widget area.
    Exposes:
      - widget: QWidget container
      - tree: QTreeWidget
    """
    
    def __init__(self, parent):
        self.widget = QWidget(parent)
        self.layout = QVBoxLayout(self.widget)

        self.label = create_header_section(self.widget, "Hierarchy View")
        self.layout.addWidget(self.label)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(["Hierarchy"])
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.tree.setIndentation(16)
        self.layout.addWidget(self.tree)
        

    def apply_font(self, fs: int):
        """
        Apply a consistent font to the Hierarchy section and adjust row height.
        Call this from MainWindow.update_font_size(size).
        """
        base = QFont("Arial", fs)
        self.widget.setFont(base)
        self.tree.setFont(base)
        self.label.setFont(QFont("Arial", fs, QFont.Weight.Bold))
        self._update_row_height(fs)

    def _update_row_height(self, fs: int):
        """
        Keep rows comfortably tall but compact.
        """
        fm = QFontMetrics(QFont("Arial", fs))
        row_h = max(22, fm.height() + 6)
        self.tree.setStyleSheet(
            f"""
            QTreeWidget::item {{ height: {row_h}px; padding: 1px 4px; }}
            """
        )
        
        
    # def populate(self, node: GateObjectInterface, write_to_console):
    #     self.tree.clear()
        
    #     def find_existing_item(name):
    #         found = self.tree.findItems(name, Qt.MatchFlag.MatchExactly, 0)
    #         return found[0] if found else None
        
    #     def add_objects_to_tree(parent_item, gate_obj: GateObjectInterface):
    #         existing_node = find_existing_item(gate_obj.name)
            
    #         if not existing_node:
    #             item = QTreeWidgetItem([gate_obj.name])
    #             item.setData(0, Qt.ItemDataRole.UserRole, gate_obj)
                
    #             if gate_obj.name == "world":
    #                 item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
    #                 item.setCheckState(0, Qt.CheckState.Checked)
                    
    #             if parent_item is None:
    #                 self.tree.addTopLevelItem(item)
    #             else:
    #                 parent_item.addChild(item)
                    
    #             write_to_console(f"Adding {gate_obj.name} to tree.")
    #         else:
    #             write_to_console(f"Skipping duplicate: {gate_obj.name}")
    #             item = existing_node
                
    #         for child in gate_obj.children.values():
    #             add_objects_to_tree(item, child)

    #     add_objects_to_tree(None, node)

    def populate(self, write_to_console):
        """Populate the gate object tree in the hierarchy section"""
        # get the node iterator
        modelIterator: ModelIteratorInterface = ModelIterator()
        self.tree.clear()
        while(modelIterator.hasMore()):
            node: GateObjectInterface = modelIterator.getNext()
            parentPath, name = node.path.rsplit("/", 1)
            parentItem = self._find_tree_child(parentPath)
            childItem = QTreeWidgetItem([name])
            childItem.setData(0, Qt.ItemDataRole.UserRole, node.path)

            if node.path == "/gate/world":
                childItem.setFlags(childItem.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                childItem.setCheckState(0, Qt.CheckState.Checked)
            
            if parentItem is self.tree.invisibleRootItem():
                self.tree.addTopLevelItem(childItem)
            else:
                parentItem.addChild(childItem)
            
            write_to_console(f"Adding {name} to tree.")


    
    def _find_tree_child(self, itemPath: str) -> QTreeWidgetItem:
        oldParent = self.tree.invisibleRootItem()
        newParent = self.tree.invisibleRootItem()
        if itemPath == "":
            return oldParent
        
        for barIndex in range(2, itemPath.count("/") + 2):
            observedPath = "/".join(itemPath.split("/")[:barIndex])
            for childIndex in range(oldParent.childCount()):
                child = oldParent.child(childIndex)
                if observedPath == child.data(0, Qt.ItemDataRole.UserRole):
                    newParent = child
                    break
            if oldParent == newParent:
                print(f"Unable to find <{itemPath}> child", file=stderr)
                return None
            oldParent = newParent
            
        return oldParent


            
    # def set_item_enabled_recursively(self, item: QTreeWidgetItem, enabled: bool):
    #     color = Qt.GlobalColor.black if enabled else Qt.GlobalColor.gray
    #     item.setForeground(0, color)
        
    #     gateObjPath: str = item.data(0, Qt.ItemDataRole.UserRole)
    #     if gateObjPath:
    #         gateObjPath.enabled = enabled
            
    #     item.setBackground(0, Qt.GlobalColor.white if enabled else Qt.GlobalColor.lightGray)
    #     for i in range(item.childCount()):
    #         child = item.child(i)
    #         child.setCheckState(0, Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)
    #         self.set_item_enabled_recursively(child, enabled)
            
    @staticmethod
    def _iterate(item, func):
        itemToSee: list[QTreeWidgetItem] = [item]
        while len(itemToSee) > 0:
            itemObserved: QTreeWidgetItem = itemToSee.pop(0)
            func(itemObserved) 
            for i in range(itemObserved.childCount()):
                itemToSee.append(itemObserved.child(i))

    @staticmethod
    def _iterateReturnFirstNotNone(item, func):
        itemToSee: list[QTreeWidgetItem] = [item]
        while len(itemToSee) > 0:
            itemObserved: QTreeWidgetItem = itemToSee.pop(0)
            result = func(itemObserved) 
            if result != None:
                return result
            for i in range(item.childCount()):
                itemToSee.append(item.child(i))
        
            
    def snapshot_state(self):
        """Return (expanded_ids, selected_id, scroll_value)."""
        expandedPaths = set()
        selectedPath = None

        self._iterate(self.tree.invisibleRootItem(), lambda it: (
            expandedPaths.add(it.data(0, Qt.ItemDataRole.UserRole)) if it.isExpanded() else None
        ))

        current = self.tree.currentItem()
        if current:
            selectedPath: str = current.data(0, Qt.ItemDataRole.UserRole)

        vscroll = self.tree.verticalScrollBar().value()
        return expandedPaths, selectedPath, vscroll
    
    
    def restore_state(self, expandedPaths: list[str], selectedPath: str, vscroll):      
        for expandedItemPath in expandedPaths:
            expandedItem = self._find_tree_child(expandedItemPath)
            expandedItem.setExpanded(True)

        if selectedPath is not None:
            selectedItem = self._find_tree_child(selectedPath)
            self.tree.setCurrentItem(selectedItem)
            self.tree.scrollToItem(selectedItem)         

        self.tree.verticalScrollBar().setValue(vscroll)
    
    def add_child_item(self, parent_obj: GateObjectInterface, child_obj: GateObjectInterface):
        """Insert a single child into the existing tree without rebuilding."""
        from PyQt6.QtWidgets import QTreeWidgetItem

        # Find parent item
        target = None
        root = self.tree.invisibleRootItem()

        def finder(it):
            nonlocal target
            obj: GateObjectInterface = it.data(0, Qt.ItemDataRole.UserRole)
            if obj is parent_obj:
                target = it

        for i in range(root.childCount()):
            self._iterate(root.child(i), finder)

        if target is None:
            return None  # parent not found; fall back to full repopulate

        # Create and attach
        item = QTreeWidgetItem([child_obj.name])
        item.setData(0, Qt.ItemDataRole.UserRole, child_obj)
        if getattr(child_obj, "name", lambda: None)() == "world":
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Checked)

        target.addChild(item)
        target.setExpanded(True)
        self.tree.setCurrentItem(item)
        return item