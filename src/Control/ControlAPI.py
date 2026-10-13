from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from src.Model.DynamicData.Concreate.GateTree import GateTree
from src.Model.DynamicData.Proxy.GateObjectProxy import GateObjectProxy

class ControlAPI():

    @staticmethod
    def getGateObjectFromObjectPath(objectPath: str) -> GateObjectInterface:
        gateObject = GateTree()

        for pathToken in objectPath.split("/")[1:]:
            gateObject = gateObject[pathToken]

        return GateObjectProxy(gateObject)


