from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from src.Model.DynamicData.Interface.GateParameterInterface import GateParameterInterface
from src.Model.DynamicData.Concreate.GateTree import GateTree
from src.Model.DynamicData.Proxy.GateObjectProxy import GateObjectProxy
from sys import stderr

class ControlAPI():

    @staticmethod
    def getGateObject(objectPath: str) -> GateObjectInterface:
        return GateObjectProxy(ControlAPI._getGateObject(objectPath))

    @staticmethod
    def updateGateObjectField(objectPath: str, field: str, value: float | str):
        setattr(ControlAPI._getGateObject(objectPath), field, value)

    @staticmethod
    def updateGateParamValue(objectPath: str, paramLabel: str, fieldIndex: str, value : str):
        gateObject = ControlAPI._getGateObject(objectPath)
        param = gateObject.param[paramLabel]

        if "text" == param.inputType:
            if value in ("", "-"):
                value = 0
            else:
                value = float(value)
        elif "checkbox" == param.inputType:
            value = value == "True"
        elif "dropdown" in param.inputType:
            if value not in param.unitList:
                print(f"\033[33mCannot update valueList attribute of {param} with {value} since it is not a valid value.\033[0m", file=stderr)
                return
        param.updateValue(fieldIndex, value)

    @staticmethod
    def updateGateParamUnitIndex(objectPath: str, paramLabel: str, index: int):
        gateObject = ControlAPI._getGateObject(objectPath)
        param = gateObject.param[paramLabel]
        if param.inputType == "text":
            param.updateUnitIndex(index)
        else:
            print(f"\033[33mCannot update unit index attribute of {param} with {index} since it is does not have units.\033[0m", file=stderr)

    @staticmethod
    def createGateVolumeChild(parentPath: str, childName: str, volumeType: str, repeaterType: str):
        gateTree = GateTree()
        parentObject = ControlAPI._getGateObject(parentPath)
        parentObject.addChild(gateTree.createVolume(childName, volumeType, repeaterType))

    @staticmethod
    def getWorldVolumeNames() -> list[str]:
        gateTree = GateTree()
        objPath = gateTree.yamlData["gate"]["object_path"]["WORLD"]["object_path"]
        gateObject = ControlAPI._getGateObject(objPath)

        names: list[str] = [gateObject.name]
        childrenToSee: list[GateObjectInterface] = list(gateObject.children.values())
        while(len(childrenToSee) > 0):
            child: GateObjectInterface = childrenToSee.pop(0)
            names.append(child.name)
            childrenToSee += list(child.children.values())

        return names

    @staticmethod
    def getProcessNames() -> list[str]:
        gateTree = GateTree()
        objPath = gateTree.yamlData["gate"]["object_path"]["PHYSICS"]["object_path"]
        gateObject = ControlAPI._getGateObject(objPath)

        return [childName for childName in gateObject.children]

    @staticmethod
    def setGateObjectName(objectPath: str, name: str):
        gateObject = ControlAPI._getGateObject(objectPath)
        gateObject.name = name    

    @staticmethod
    def getYamlUnits(unit: str) -> list[str]:
        gateTree = GateTree()
        return gateTree.yamlData["gate"]["units"][unit]

    @staticmethod
    def createDistributionChild(childName: str, distributionType: str):
        gateTree = GateTree()
        distributionsInfo = ControlAPI._getYamlData("gate/object_path/DISTRIBUTIONS")
        parentObject = ControlAPI._getGateObject(distributionsInfo["object_path"])

    @staticmethod
    def createProcess(processName: str):
        gateTree = GateTree()
        physicsInfo = ControlAPI._getYamlData("gate/object_path/PHYSICS")
        processObject = gateTree.createGateObjectEmpty("/".join([physicsInfo["object_path"], processName]))
        gateTree.addParamFromYamlSection(processObject, ControlAPI._getYamlData("gate/parameter/physics/process"))

    @staticmethod
    def _getGateObject(objectPath: str) -> GateObjectInterface:
        gateObject = GateTree()
        
        for pathToken in objectPath.split("/")[1:]:
            gateObject = gateObject[pathToken]
        
        return gateObject

    @staticmethod
    def _getYamlData(yamlPath: str):
        yamlToken = yamlPath.split("/")
        if yamlPath[0] == "/":
            yamlToken = yamlToken[1:]

        gateTree = GateTree()
        yamlData = gateTree.yamlData

        for token in yamlToken:
            yamlData = yamlData[token]

        return yamlData


