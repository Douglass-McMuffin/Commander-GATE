from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from src.Model.DynamicData.Proxy.GateParameterProxy import GateParameterProxy
from sys import stderr

class GateObjectProxy(GateObjectInterface):
    """Implementation of the GateObjectInterface that only give read acces to itself."""

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
        paramDict = {}
        for paramKey in self._gateObject.param:
            paramDict[paramKey] = GateParameterProxy(self._gateObject.param[paramKey])
        return paramDict

    @property
    def children(self):
        childrenDict = {}
        for childKey in self._gateObject.children:
            childrenDict[childKey] = GateParameterProxy(self._gateObject.children[childKey])
        return childrenDict

    @path.setter
    def path(self, path: str):
        print(f"\033[33mCannot change <path> attribute of {str(self)} since it is a proxy.\033[0m", file=stderr)

    @name.setter
    def name(self, name: str):
        print(f"\033[33mCannot change <name> attribute of {str(self)} since it is a proxy.\033[0m", file=stderr)

    @parent.setter
    def parent(self, parent: GateObjectProxy):
        print(f"\033[33mCannot change <parent> attribute of {str(self)} since it is a proxy.\033[0m", file=stderr)

    @param.setter
    def param(self, param: list[GateParameterProxy]):
        print(f"\033[33mCannot change <param> attribute of {str(self)} since it is a proxy.\033[0m", file=stderr)

    @children.setter
    def children(self, children: list[GateObjectProxy]):
        print(f"\033[33mCannot change <children> attribute of {str(self)} since it is a proxy.\033[0m", file=stderr)

    def getObjectFromGateObjectPath(self, gateObjectPath: str) -> GateObjectInterface:
        pathToken : list[str] = gateObjectPath.split("/")[1:]
        if pathToken[0] not in (".", ".."):
            gateObject = GateObjectProxy(GateTree())
        else:
            gateObject = self

        for token in pathToken:
            if token == "..":
                if gateObject.name == "root":
                    print(f"\033[33mCannot get the root node parent since it is the root.\033[0m", file=stderr)
                    return None
                gateObject = gateObject.parent
            elif token != ".":
                gateObject = gateObject[token]

        return gateObject

from src.Model.DynamicData.Concreate.GateTree import GateTree