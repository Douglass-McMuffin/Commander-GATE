from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics
from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from src.Control.ModelIteratorInterface import ModelIteratorInterface
from src.Control.ModelIterator import ModelIterator
from .header import create_header_section
from sys import stderr

class HierarchySection:
    """
    Encapsulates the hierarchy widget area.
    Exposes:
      - widget: QWidget container
      - tree: QTreeWidget
    """
    
    def __init__(self, parent):
        """
        Get the hierarchy section

        keyword arguments:
        parent -- QWidget parent 
        """
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

        keyword arguments:
        fs -- font size
        """
        base = QFont("Arial", fs)
        self.widget.setFont(base)
        self.tree.setFont(base)
        self.label.setFont(QFont("Arial", fs, QFont.Weight.Bold))
        self._update_row_height(fs)

    def _update_row_height(self, fs: int):
        """
        Keep rows comfortably tall but compact.

        keyword arguments:
        fs -- font size
        """
        fm = QFontMetrics(QFont("Arial", fs))
        row_h = max(22, fm.height() + 6)
        self.tree.setStyleSheet(
            f"""
            QTreeWidget::item {{ height: {row_h}px; padding: 1px 4px; }}
            """
        )

    def populate(self, write_to_console):
        """
        Populate the gate object tree in the hierarchy section.
        
        keyword arguments:
        write_to_console -- function that write directly to the console"""
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
        """
        Get the QTreeWidgetItem related to the item path.

        keyword arguments:
        itemPath -- path of the item inside the tree widget
        """
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
            
    @staticmethod
    def _iterate(item, func):
        """
        Iterate through the item and its children recursively and execute a funcion for each.

        keyword arguments:
        item -- item that is iterated through
        func -- funcion applied for each item in the following manner : func(item)
        """
        itemToSee: list[QTreeWidgetItem] = [item]
        while len(itemToSee) > 0:
            itemObserved: QTreeWidgetItem = itemToSee.pop(0)
            func(itemObserved) 
            for i in range(itemObserved.childCount()):
                itemToSee.append(itemObserved.child(i))

    @staticmethod
    def _iterateReturnFirstNotNone(item, func):
        """
        Iterate through the item and its children recursively until the funcion returns.
        
        keyword arguments:
        item -- item that is iterated through
        func -- funcion applied for the item in the following manner : func(item)
        """
        itemToSee: list[QTreeWidgetItem] = [item]
        while len(itemToSee) > 0:
            itemObserved: QTreeWidgetItem = itemToSee.pop(0)
            result = func(itemObserved) 
            if result != None:
                return result
            for i in range(item.childCount()):
                itemToSee.append(item.child(i))
        
            
    def snapshot_state(self):
        """
        Take a snapshot of the tree widget state and return the information concerning the expanded and selected items, but also the vertical scroll.
        Return in this way : (expanded_ids, selected_id, scroll_value).
        """
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
        """
        Restore the tree widget state with expanded and selected items but also vertical scroll.

        keyword arguments:
        expandedPaths -- list of item's path that are expanded
        selectedPath -- item's path that is selected
        vscroll -- vertical scroll
        """   
        for expandedItemPath in expandedPaths:
            expandedItem = self._find_tree_child(expandedItemPath)
            expandedItem.setExpanded(True)

        if selectedPath is not None:
            selectedItem = self._find_tree_child(selectedPath)
            self.tree.setCurrentItem(selectedItem)
            self.tree.scrollToItem(selectedItem)         

        self.tree.verticalScrollBar().setValue(vscroll)
    
    def add_child_item(self, parentPath: str, childObj: GateObjectInterface):
        """
        Insert a single child into the existing tree without rebuilding.
        
        keyword arguments:
        parentPath -- item path of the parent
        childObj -- child gate object"""
        from PyQt6.QtWidgets import QTreeWidgetItem

        # Find parent item
        parentItem = self._find_tree_child(parentPath)

        # Create and attach
        item = QTreeWidgetItem([childObj.name])
        item.setData(0, Qt.ItemDataRole.UserRole, childObj.path)
        if childObj.path.startswith("/gate/world"):
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Checked)

        parentItem.addChild(item)
        parentItem.setExpanded(True)
        self.tree.setCurrentItem(item)
        return item