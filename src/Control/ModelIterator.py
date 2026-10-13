from src.Control.ModelIteratorInterface import ModelIteratorInterface
from src.Model.DynamicData.Proxy.GateObjectProxy import GateObjectProxy
from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from src.Model.DynamicData.Concreate.GateTree import GateTree

class ModelIterator(ModelIteratorInterface):

    def __init__(self):
        self._gateTree: GateTree = GateTree()
        self._currentGateObject: GateObjectInterface = self._gateTree

    def getNext(self) -> GateObjectInterface:
        """Depth First Search"""

        gObj = self._currentGateObject
        #If the current gate object has children, check the children
        if len(gObj.children) >= 1:
            self._currentGateObject = list(self._currentGateObject.children.values())[0]
            return GateObjectProxy(self._currentGateObject)
        
        while(gObj.parent is not None):
            #If not, check if it has siblings (take a step up to the parent and then check children)
            siblings = gObj.parent.children
            if len(siblings) >= 2:
                nextSiblingIndex = list(siblings.values()).index(gObj) + 1
                # If the gate object is not the last siblings
                if nextSiblingIndex < len(siblings):
                    self._currentGateObject = list(siblings.values())[nextSiblingIndex]
                    return GateObjectProxy(self._currentGateObject)
                else:
                    gObj = gObj.parent
            else:
                gObj = gObj.parent

        return None

    def hasMore(self) -> bool:
        gObj = self._currentGateObject
        #If the current gate object has children, check the children
        if len(gObj.children) >= 1:
            return True
        
        while(gObj.parent is not None):
            #If not, check if it has siblings (take a step up to the parent and then check children)
            siblings = gObj.parent.children
            if len(siblings) >= 2:
                nextSiblingIndex = list(siblings.values()).index(gObj) + 1
                if nextSiblingIndex < len(siblings):
                    return True
                else:
                    gObj = gObj.parent
            else:
                gObj = gObj.parent
        
        return False
                
            