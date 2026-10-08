from src.Model.DynamicData.GateParameter import GateParameter
from src.Model.DynamicData.GateObjectInterface import GateObjectInterface
from src.Model.DynamicData.GateParameter import GateParameter

class GateObject(GateObjectInterface):
    def __init__(self, path: str, name: str, parent: GateObject = None, param: list[GateParameter] = []):
        self._path: str = path
        self._name: str = name
        self._parent: GateObject = parent
        self._param: list[GateParameter] = param
        self._children: dict[str, GateObject] = {} 
        

        # The following caracteristic are going to be a GateParameter :
        # material, translation, rotation, color, style
        # TODO check the CSG Volumes to implement the parameters correctyly

    def __repr__(self):
        return f"name: {self.name}, parameter: {self.param}, children: {list(self.children.values())}"

    def __getitem__(self, key: str):
        return self.children[key]

        
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
            if parameter.displayed_label == parameterToGet:
                return parameter
    
        
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

    @parent.setter
    def parent(self, parent: GateObjectInterface):
        self._parent = parent

    @param.setter
    def param(self, param: list[GateParameter]):
        self._param = param

    @children.setter
    def children(self, childDict: dict[str, GateObject]):
        self._children = childDict