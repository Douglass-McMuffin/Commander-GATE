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
        childObject = gateTree.createGateObjectEmpty("/".join([parentPath, childName]))
        gateTree.addVolumeParam(childObject, volumeType, repeaterType)
        gateTree.initObjectParam(childObject)

    @staticmethod
    def getObjectNames(objectPath: str) -> list[str]:
        gateObject = ControlAPI._getGateObject(objectPath)

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
    def getDistributionTypes() -> list[str]:
        return list(ControlAPI._getYamlData("gate/parameter/distributions/distributions_type").keys())

    @staticmethod
    def getDigitizerTypes() -> list[str]:
        return list(ControlAPI._getYamlData("gate/parameter/digitizer/digitizer_type").keys())

    @staticmethod
    def getAttachedVolumes() -> list[str]:
        gateTree = GateTree()
        observedObjectList = [gateTree.getObjectFromGateObjectPath(gateTree, gateTree._getYamlData("gate/object_path/WORLD/object_path"))]
        unitList = []
        while len(observedObjectList) > 0:
            observedObject = observedObjectList.pop(0)
            if observedObject.param["Attach Volume to System"].valueList[0]:
                unitList.append(observedObject.name)
            for child in observedObject.children.values():
                observedObjectList.append(child)
        return unitList

    @staticmethod
    def getObjectPath(objectKey: str) -> str:
        gateTree = GateTree()
        return gateTree.yamlData["gate"]["object_path"][objectKey]["object_path"]

    @staticmethod
    def createDistributionChild(distributionName: str, distributionType: str):
        gateTree = GateTree()
        distributionsInfo = ControlAPI._getYamlData("gate/object_path/DISTRIBUTIONS")
        distributionObject = gateTree.createGateObjectEmpty("/".join([distributionsInfo["object_path"], distributionName]))
        gateTree.addParamFromYamlSection(distributionObject, ControlAPI._getYamlData("gate/parameter/distributions/distributions_general"))
        gateTree.addParamFromYamlSection(distributionObject, ControlAPI._getYamlData(f"gate/parameter/distributions/distributions_type/{distributionType}"))
        gateTree.initObjectParam(distributionObject)
        distributionObject.param["Distribution type"].updateValue(0, distributionType)


    @staticmethod
    def createProcess(processName: str):
        gateTree = GateTree()
        physicsInfo = ControlAPI._getYamlData("gate/object_path/PHYSICS")
        processObject = gateTree.createGateObjectEmpty("/".join([physicsInfo["object_path"], processName]))
        gateTree.addParamFromYamlSection(processObject, ControlAPI._getYamlData("gate/parameter/physics/process"))
        gateTree.initObjectParam(processObject)

    @staticmethod
    def createSource(sourceName: str, sourceType: str):
        gateTree = GateTree()
        sourceInfo = ControlAPI._getYamlData("gate/object_path/SOURCE")
        sourceObject = gateTree.createGateObjectEmpty("/".join([sourceInfo["object_path"], sourceName]))
        gateTree.addParamFromYamlSection(sourceObject, ControlAPI._getYamlData("gate/parameter/source/source_general"))
        gateTree.addParamFromYamlSection(sourceObject, ControlAPI._getYamlData(f"gate/parameter/source/{sourceType}"))
        gateTree.initObjectParam(sourceObject)

    @staticmethod
    def createDigitizer(sensitiveDetectorName: str, digitizerType: str, singlesDigitizerName: str):
        gateTree = GateTree()
        digitizerInfo = ControlAPI._getYamlData("gate/object_path/DIGITIZER")
        digitizerObject = gateTree.createGateObjectEmpty("/".join([digitizerInfo["object_path"], singlesDigitizerName]))
        gateTree.addParamFromYamlSection(digitizerObject, ControlAPI._getYamlData("gate/parameter/digitizer/digitizer_general"))
        gateTree.initObjectParam(digitizerObject)
        digitizerObject.param["Digitizer Type"].updateValue(0, digitizerType)

        detectorVolumePath = ControlAPI._getDetectorVolume(sensitiveDetectorName).path
        digitizerObject.param["Detector Volume Path"].updateValue(0, detectorVolumePath)

        for moduleType in ControlAPI._getYamlData(f"gate/parameter/digitizer/{digitizerType}").keys():
            digitizerModuleObject = gateTree.createGateObjectEmpty("/".join(digitizerObject.path, moduleType))
            gateTree.addParamFromYamlSection(digitizerModuleObject, ControlAPI._getYamlData(f"gate/parameter/digitizer/{digitizerType}_general"))
            gateTree.addParamFromYamlSection(digitizerModuleObject, ControlAPI._getYamlData(f"gate/parameter/digitizer/digitizer_type/{digitizerType}/{moduleType}"))
            gateTree.initObjectParam(digitizerModuleObject)

    @staticmethod
    def _getGateObject(objectPath: str) -> GateObjectInterface:
        gateObject = GateTree()
        
        for pathToken in objectPath.split("/")[1:]:
            gateObject = gateObject[pathToken]
        
        return gateObject

    @staticmethod
    def _getYamlData(yamlPath: str):
        gateTree = GateTree()
        return gateTree._getYamlData(yamlPath)

    @staticmethod
    def _getDetectorVolume(detectorName: str) -> GateObjectInterface:
        observedVolume = ControlAPI._getGateObject(ControlAPI.getObjectPath("WORLD"))

        volumeToSee = list(observedVolume.children.values())
        while observedVolume.name != detectorName:
            observedVolume = volumeToSee.pop(0)
            volumeToSee += list(observedVolume.children.values())

        return observedVolume



