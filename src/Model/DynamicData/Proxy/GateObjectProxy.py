from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from src.Model.DynamicData.Proxy.GateParameterProxy import GateParameterProxy
from sys import stderr

class GateObjectProxy(GateObjectInterface):

    def __init__(self, gateObject: GateObjectInterface):
        self._gateObject = gateObject



    ### GateObjectInterface Methods

    @property
    def path(self):
        return self._gateObject.path

    @property
    def name(self):
        return self._gateObject.name

    @property
    def parent(self):
        return GateObjectProxy(self._gateObject.parent)

    @property
    def param(self):
        return [GateParameterProxy(param) for param in self._gateObject.param]

    @property
    def children(self):
        return [GateObjectProxy(child) for child in self._gateObject.children]

    @path.setter
    def path(self, path: str):
        print(f"Cannot change <path> attribute of {str(self)} since it is a proxy.", file=stderr)

    @name.setter
    def name(self, name: str):
        print(f"Cannot change <name> attribute of {str(self)} since it is a proxy.", file=stderr)

    @parent.setter
    def parent(self, parent: GateObjectProxy):
        print(f"Cannot change <parent> attribute of {str(self)} since it is a proxy.", file=stderr)

    @param.setter
    def param(self, param: list[GateParameterProxy]):
        print(f"Cannot change <param> attribute of {str(self)} since it is a proxy.", file=stderr)

    @children.setter
    def children(self, children: list[GateObjectProxy]):
        print(f"Cannot change <children> attribute of {str(self)} since it is a proxy.", file=stderr)