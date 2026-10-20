from src.Model.DynamicData.Concreate.GateParameter import GateParameter
from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from src.Model.DynamicData.Concreate.GateParameter import GateParameter

class GateObject(GateObjectInterface):
    def __init__(self, name: str):
        self._path: str
        self._name: str = name
        self._parent: GateObject
        self._param: dict[str, GateParameter] = {}
        self._children: dict[str, GateObject] = {} 

        # Helper variable to create the gateObject
        self.paramList: list[GateParameter] = []

        # The following caracteristic are going to be a GateParameter :
        # material, translation, rotation, color, style
        # TODO check the CSG Volumes to implement the parameters correctyly

    def __repr__(self):
        return f"name: {self.name}, parameter: {self.param}, children: {list(self.children.values())}"
        
    def to_dict(self):
        return {
        "path": self.path,
        "name": self.name,
        "parent": self.parent,
        "param": self.param,
        "children": self.children        
    }

    def getParameter(self, parameterToGet: str) -> GateParameter:
        for parameter in self.param:
            if parameter.displayedLabel == parameterToGet:
                return parameter

    def updatePathRecursive(self):
        parentPath = self.parent.path
        self.path = "/".join([parentPath, self.name])
        for child in self.children.values():
            child.updatePathRecursive()
    
        
    ### GateObject abstract implementation

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def param(self):
        return self._param

    @property
    def children(self):
        return self._children

    @path.setter
    def path(self, path: str):
        self._path = path

    @name.setter
    def name(self, name: str):
        self._name = name
        self.updatePathRecursive()

    @parent.setter
    def parent(self, parent: GateObjectInterface):
        self._parent = parent
        self.updatePathRecursive()

    @param.setter
    def param(self, param: dict[str, GateParameter]):
        self._param = param

    @children.setter
    def children(self, childDict: dict[str, GateObject]):
        self._children = childDict
