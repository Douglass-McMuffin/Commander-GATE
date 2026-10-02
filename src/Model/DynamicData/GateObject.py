from src.Model.DynamicData.GateParameter import GateParameter

class GateObject(object):
    def __init__(self, path: str, name: str, mother: GateObject = None, param: list[GateParameter] = []):
        self.path: str = path
        self.name: str = name
        self.mother: GateObject = mother
        self.param: list[GateParameter] = param
        self.children: dict[str, GateObject] = {} 
        

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
        "mother": self.mother,
        "param": self.param,
        "children": self.children        
    }

    def addChild(self, child: GateObject):
        child.mother = self
        self.children[child.name] = child

    def getParameter(self, parameterToGet: str) -> GateParameter:
        for parameter in self.param:
            if parameter.displayed_label == parameterToGet:
                return parameter
    
        

    