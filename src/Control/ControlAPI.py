from src.Model.DynamicData.Concreate.GateTree import GateTree
from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from src.Model.DynamicData.Interface.GateParameterInterface import GateParameterInterface
from src.Model.DynamicData.Proxy.GateObjectProxy import GateObjectProxy
from src.Model.DynamicData.Concreate.GateObject import GateObject
from src.Model.DynamicData.Concreate.GateParameter import GateParameter
from copy import deepcopy

import json
from sys import stderr

class ControlAPI():

    ### GateObject Methods ###
    @staticmethod
    def getGateObject(objectPath: str) -> GateObjectInterface:
        """
        Get the gate object from the gate tree.

        Args:
            objectPath: path to the object from the root of the gate tree
        """
        return GateObjectProxy(ControlAPI._getGateObject(objectPath))

    @staticmethod
    def updateGateObjectField(objectPath: str, field: str, value: float | str):
        """
        Update the attribute of a gate object.

        Args:
            objectPath: path to the object from the root of the gate tree
            field: name of the attribute
            value: value to insert in the attribute
        """
        setattr(ControlAPI._getGateObject(objectPath), field, value)

    @staticmethod
    def updateGateParamValue(objectPath: str, paramLabel: str, fieldIndex: str, value : str):
        """
        Update selected value of a selected gate parameter.

        Args:
            objectPath: path to the object from the root of the gate tree
            paramLabel: displayed label of the parameter
            fieldIndex: index of the value to change in the value list of the gate parameter
            value: value to insert in the attribute
        """
        gateObject = ControlAPI._getGateObject(objectPath)
        param = gateObject.param[paramLabel]

        if "text" in param.inputType:
            if value in ("", "-"):
                value = 0
            else:
                value = float(value)
        elif "checkbox" in param.inputType:
            value = value == "True"
        elif "dropdown" in param.inputType:
            if value not in param.unitList:
                print(f"\033[33mCannot update valueList attribute of {param} with {value} since it is not a valid value.\033[0m", file=stderr)
                return
        param.updateValue(fieldIndex, value)

    @staticmethod
    def updateGateParamUnitIndex(objectPath: str, paramLabel: str, index: int):
        """
        Update the selected gate parameter prefered unit for a text parameter.

        Args:
            objectPath: path to the object from the root of the gate tree
            paramLabel: displayed label of the parameter
            index: index of the prefered unit in its unit list
        """
        gateObject = ControlAPI._getGateObject(objectPath)
        param = gateObject.param[paramLabel]
        if param.inputType == "text":
            param.updateUnitIndex(index)
        else:
            print(f"\033[33mCannot update unit index attribute of {param} with {index} since it is does not have units.\033[0m", file=stderr)

    @staticmethod
    def createGateVolumeChild(parentPath: str, childName: str, volumeType: str, repeaterType: str):
        """
        Create volume under the selected gate object.
        
        Args:
            parentPath: path to the parent object from the root of the gate tree
            childName: name of the new volume
            volumeType: type of volume to create ("box", "cylinder", ...)
            repeaterType: type of repeater to apply (" - " = None, "linear", "ring", ...)
        """
        gateTree = GateTree()
        childObject = gateTree.createGateObjectEmpty("/".join([parentPath, childName]))
        gateTree.addVolumeParam(childObject, volumeType, repeaterType)
        gateTree.initObjectParam(childObject)

    @staticmethod
    def getObjectNames(objectPath: str) -> list[str]:
        """
        Get the names of the selected object and its children.

        Args:
            objectPath: path to the object from the root of the gate tree
        """
        gateObject = ControlAPI._getGateObject(objectPath)

        names: list[str] = [gateObject.name]
        childrenToSee: list[GateObjectInterface] = list(gateObject.children.values())
        while(len(childrenToSee) > 0):
            child: GateObjectInterface = childrenToSee.pop(0)
            names.append(child.name)
            childrenToSee += list(child.children.values())

        return names

    @staticmethod
    def setGateObjectName(objectPath: str, name: str):
        """
        Update the selected gate object's name

        Args:
            objectPath: path to the object from the root of the gate tree
            name: new name for the selected gate object
        """
        gateObject = ControlAPI._getGateObject(objectPath)
        parentObject = gateObject.parent
        oldName = gateObject.name
        gateObject.name = name    
        parentObject.children.pop(oldName)
        parentObject.children[name] = gateObject


    @staticmethod
    def getYamlUnits(unit: str) -> list[str]:
        """
        Get the selected units.

        Args:
            unit: yaml static keyword for the selected unit
        """
        gateTree = GateTree()
        return gateTree.yamlData["gate"]["units"][unit]

    @staticmethod
    def getProcessTypes() -> list[str]:
        """
        Get every distribution type available.
        """
        return list(ControlAPI._getYamlData("gate/process_components").keys())

    @staticmethod
    def getDistributionTypes() -> list[str]:
        """
        Get every distribution type available.
        """
        return list(ControlAPI._getYamlData("gate/parameter/distributions/distributions_type").keys())

    @staticmethod
    def getDigitizerTypes() -> list[str]:
        """
        Get every digitizer type available.
        """
        return list(ControlAPI._getYamlData("gate/parameter/digitizer/digitizer_type").keys())

    @staticmethod
    def getSourceTypes() -> list[str]:
        """Get every source types available."""
        return list(ControlAPI._getYamlData("gate/parameter/source/source_type").keys())

    @staticmethod
    def getAttachedVolumes() -> list[str]:
        """
        Get the names of every attached volumes.
        """
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
        """
        Get the path of a gate object predetermined folder

        Args:
            objectKey: yaml static keyword for the selected predetermined gate object
        """
        gateTree = GateTree()
        return gateTree.yamlData["gate"]["object_path"][objectKey]["object_path"]

    @staticmethod
    def createDistributionChild(distributionName: str, distributionType: str):
        """
        Create a new distribution.

        Args:
            distributionName: name of the new distribution
            distributionType: type of the new distribution
        """
        gateTree = GateTree()
        distributionsInfo = ControlAPI._getYamlData("gate/object_path/DISTRIBUTIONS")
        distributionObject = gateTree.createGateObjectEmpty("/".join([distributionsInfo["object_path"], distributionName]))
        gateTree.addParamFromYamlSection(distributionObject, ControlAPI._getYamlData("gate/parameter/distributions/distributions_general"))
        gateTree.addParamFromYamlSection(distributionObject, ControlAPI._getYamlData(f"gate/parameter/distributions/distributions_type/{distributionType}"))
        gateTree.initObjectParam(distributionObject)
        distributionObject.param["Distribution type"].updateValue(0, distributionType)


    @staticmethod
    def createProcess(processName: str):
        """
        Create a process to alter the chosen physisc

        Args:
            processName: name of the new process
        """
        gateTree = GateTree()
        physicsInfo = ControlAPI._getYamlData("gate/object_path/PHYSICS")
        processObject = gateTree.createGateObjectEmpty("/".join([physicsInfo["object_path"], processName]))
        gateTree.addParamFromYamlSection(processObject, ControlAPI._getYamlData("gate/parameter/physics/process"))
        gateTree.initObjectParam(processObject)

    @staticmethod
    def createSource(sourceName: str, sourceType: str):
        """
        Create a new source.

        Args:
            sourceName: name of the new source
            sourceType: type of the new source
        """
        gateTree = GateTree()
        sourceInfo = ControlAPI._getYamlData("gate/object_path/SOURCE")
        sourceObject = gateTree.createGateObjectEmpty("/".join([sourceInfo["object_path"], sourceName]))
        gateTree.addParamFromYamlSection(sourceObject, ControlAPI._getYamlData("gate/parameter/source/source_general"))
        gateTree.addParamFromYamlSection(sourceObject, ControlAPI._getYamlData(f"gate/parameter/source/source_type/{sourceType}"))
        gateTree.initObjectParam(sourceObject)

    @staticmethod
    def createDigitizer(sensitiveDetectorName: str, digitizerType: str, singlesDigitizerName: str):
        """
        Create a new digitizer link to a selected sensitive detector

        Args:
            sensitiveDetectorName: name of the sensitive detector
            digitizerType: type of the new digitizer
            singlesDigitizerName: name of the new digitizer
        """
        gateTree = GateTree()
        digitizerInfo = ControlAPI._getYamlData("gate/object_path/DIGITIZER")
        digitizerObject = gateTree.createGateObjectEmpty("/".join([digitizerInfo["object_path"], singlesDigitizerName]))
        gateTree.addParamFromYamlSection(digitizerObject, ControlAPI._getYamlData("gate/parameter/digitizer/digitizer_general"))
        gateTree.initObjectParam(digitizerObject)
        digitizerObject.param["Digitizer Type"].updateValue(0, digitizerType)

        detectorVolumePath = ControlAPI._getDetectorVolume(sensitiveDetectorName).path
        digitizerObject.param["Detector Volume Path"].updateValue(0, detectorVolumePath)

        for moduleType in ControlAPI._getYamlData(f"gate/parameter/digitizer/digitizer_type/{digitizerType}").keys():
            digitizerModuleObject = gateTree.createGateObjectEmpty("/".join([digitizerObject.path, moduleType]))
            gateTree.addParamFromYamlSection(digitizerModuleObject, ControlAPI._getYamlData(f"gate/parameter/digitizer/{digitizerType}_general"))
            gateTree.addParamFromYamlSection(digitizerModuleObject, ControlAPI._getYamlData(f"gate/parameter/digitizer/digitizer_type/{digitizerType}/{moduleType}"))
            gateTree.initObjectParam(digitizerModuleObject)

    @staticmethod
    def getMaterials() -> list[str]:
        """Get the material list used by the project"""
        gateTree = GateTree()
        return gateTree.material

    @staticmethod
    def exportProject(filePath: str):
        """
        Export the model into a json file.

        Args:
            filePath: where to save the project json file
        """
        gateTree = GateTree()
        modelData = gateTree.toDict()
        file = open(filePath, "w")
        json.dump(modelData, file, indent=4)
        file.close()

    @staticmethod
    def importProject(filePath: str):
        """
        Import the model stored in the json file.

        Args:
            filePath: where the project json file is saved
        """
        gateTree = GateTree()
        file = open(filePath, "r")
        jsonContent = json.load(file)
        file.close()

        gateTree.children.clear()
        gateTree.material.clear()
        gateTree.gateTreeSubscriber.clear()

        # Create every gate object empty
        gateObjectDictToView = deepcopy(jsonContent["children"])
        while len(gateObjectDictToView) > 0:
            gateObjectDict = gateObjectDictToView.pop(0)
            gateObjectDictToView += gateObjectDict["children"]

            # Find the parent
            parentObject = gateTree.getObjectFromGateObjectPath(gateTree, gateObjectDict["parent"])
            
            gateObject = GateObject(gateObjectDict["name"])
            gateObject.path = gateObjectDict["path"]
            gateObject.parent = parentObject
            parentObject.children[gateObject.name] = gateObject

        

        # Add every gate parameter without subscriber (they are maybe not initialized yet)
        gateObjectDictToView = deepcopy(jsonContent["children"])
        while len(gateObjectDictToView) > 0:
            gateObjectDict = gateObjectDictToView.pop(0)
            gateObjectDictToView += gateObjectDict["children"]
            gateObject = gateTree.getObjectFromGateObjectPath(gateTree, gateObjectDict["path"])

            for paramDict in gateObjectDict["param"]:
                gateParameter = GateParameter(
                    paramDict["path"],
                    paramDict["displayedLabel"],
                    paramDict["inputType"],
                    paramDict["defaultValueList"],
                    paramDict["multiplicity"],
                    paramDict["unitList"],
                    paramDict["defaultUnitIndex"],
                ) 
                gateParameter.valueList = paramDict["valueList"]
                gateParameter._yamlRawProperty = paramDict["yamlRawProperty"]
                gateParameter._gateObjectParent = gateObject

                gateObject.param[gateParameter.displayedLabel] = gateParameter

        for treeSubscriberPath in deepcopy(jsonContent["gateTreeSubscriber"]):
            objectPath, displayedLabel = treeSubscriberPath.rsplit("/", maxsplit=1)
            treeSubscriber = gateTree.getObjectFromGateObjectPath(gateTree, objectPath)
            gateTree.gateTreeSubscriber.append(treeSubscriber.param[displayedLabel])

        # Add the subscriberValueChanged to the params
        gateObjectDictToView = deepcopy(jsonContent["children"])
        while len(gateObjectDictToView) > 0:
            gateObjectDict = gateObjectDictToView.pop(0)
            gateObjectDictToView += gateObjectDict["children"]
            gateObject = gateTree.getObjectFromGateObjectPath(gateTree, gateObjectDict["path"])

            for paramDict in gateObjectDict["param"]:
                gateParameter = gateObject.param[paramDict["displayedLabel"]]

                for paramSubscriberPath in paramDict["subscriberValueChanged"]:
                    objectPath, displayedLabel = paramSubscriberPath.rsplit("/", maxsplit=1)
                    gateObjectSubscriber = gateTree.getObjectFromGateObjectPath(gateTree, objectPath)
                    gateParameterSubscriber = gateObjectSubscriber.param[displayedLabel]
                    gateParameter._subscriberValueChanged.append(gateParameterSubscriber)
            


    ### Private methods (helpers) ###
    @staticmethod
    def _getGateObject(objectPath: str) -> GateObjectInterface:
        """
        Get the gate object from the gate tree.
        
        Args:
            objectPath: path to the object from the root of the gate tree
        """
        gateTree = GateTree()
        return gateTree.getObjectFromGateObjectPath(gateTree, objectPath)

    @staticmethod
    def _getYamlData(yamlPath: str):
        """
        Get a selected part of the static yaml data.

        Args:
            yamlPath: path from the root of the yaml tree to the selected part
        """
        gateTree = GateTree()
        return gateTree._getYamlData(yamlPath)

    @staticmethod
    def _getDetectorVolume(detectorName: str) -> GateObjectInterface:
        """
        Get the volume associated with a detector.

        Args:
            detectorName: name of the detector associated with the volume
        """
        observedVolume = ControlAPI._getGateObject(ControlAPI.getObjectPath("WORLD"))

        volumeToSee = list(observedVolume.children.values())
        while observedVolume.name != detectorName:
            observedVolume = volumeToSee.pop(0)
            volumeToSee += list(observedVolume.children.values())

        return observedVolume



