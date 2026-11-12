import src.Model.StaticData.StaticData as StaticData
from src.Model.DynamicData.Interface.GateParameterInterface import GateParameterInterface
from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from copy import deepcopy



class GateParameter(GateParameterInterface):
    def __init__(
            self, 
            path: str,
            displayed_label: str, 
            input_type: str, 
            default_value_list: list[str | int | float],
            multiplicity: bool = False,
            unit_list: list[str] = [], 
            default_unit_index: int = 0,
            yaml_raw_property: dict[str, str | int | list[str]] = {}
        ):
        """
        Initialise the gate parameter.
        
        Args:
            path: macro associated with parameter
            displayed_label: label displayed by the parameter
            input_type: type of the input for the parameter ("text", "dropdown", "checkbox", ...)
            default_value_list: defautl value of the parameter before any user changes
            multiplicity: enables multiple instance of this parameter
            unit_list: list of the units for the "text" input and values to choose from for the "dropdown" input
            default_unit_index: default unit to show for either the "text" input or the value for the "dropdown" input
            yaml_raw_property: yaml section associated with the parameter
        """
        self._path = path
        self._displayedLabel = displayed_label
        self._inputType = input_type
        self._defaultValueList = default_value_list
        self._multiplicity = multiplicity
        self._valueList = deepcopy(default_value_list)
        self._unitList = unit_list
        self._defaultUnitIndex = default_unit_index
        self._yamlRawProperty = yaml_raw_property

        self._subscriberValueChanged: list[GateParameter] = []
        self._gateObjectParent: GateObjectInterface = None

    def __repr__(self):
        return f"Param <\"{self._displayedLabel}\">"
    
    def toDict(self):
        """Store and return the gate paramter data in a dictionnary."""
        return {
            "path": self._path,
            "displayedLabel": self._displayedLabel,
            "inputType": self._inputType,
            "defaultValueList": self._defaultValueList,
            "multiplicity": self._multiplicity,
            "valueList": self._valueList,
            "unitList": self._unitList,
            "defaultUnitIndex": self._defaultUnitIndex,
            "yamlRawProperty": self._yamlRawProperty,
            "subscriberValueChanged": ["/".join((param.gateObjectParent.path, param.displayedLabel)) for param in self._subscriberValueChanged] # This make is able to find the parameter instance.
        }



    def addSubcriber(self, gateParameter: GateParameter):
        """
        Add a subscriber to the subcriber-publisher model.
        
        Args:
            gateParameter: parameter to notify when a change has occured."""
        self._subscriberValueChanged.append(gateParameter)

    def notifyAllSubscriber(self):
        """Notify every subscriber of the change."""
        for parameter in self._subscriberValueChanged:
            parameter.receiveNotification()

    def notifyOneSubscriber(self, gateParameter: GateParameter):
        """Notify a selected subscriber of the change."""
        gateParameter.receiveNotification()

    def receiveNotification(self):
        """Handle the noficiation received from the publishing parameter. Update for the most part dynamic parameter."""

        notificationHandler = {
            "dynamic_dropdown": self._receiveNotificationDynamicDropdown,
            "object_name_dropdown": self._receiveNotificationObjectNameDropdown,
            "checkable_object_name_dropdown": self._receiveNotificationCheckableObjectNameDropdown,
            "children_name_dropdown": self._receiveNotificationChildrenNameDropdown,
            "attached_volume_dropdown": self._receiveNotificationAttachedVolumeDropdown,
            "digitizer_detector_dropdown": self._receiveNotificationDigitizerDetectorDropdown,
            "dynamic_label": self._receiveNotificationDynamicLabel,
            "dynamic_object_name_dropdown": self._receiveNotificationDynamicObjectNameDropdown
        }

        notificationHandler[self.inputType]()

    def _receiveNotificationDynamicDropdown(self):
        from src.Model.DynamicData.Concreate.GateTree import GateTree
        gateTree = GateTree()

        objectPath: list[str]       = self._yamlRawProperty["object_path"]
        labelName: list[str]        = self._yamlRawProperty["object_label"]
        labelIndex: list[int]       = self._yamlRawProperty["object_label_index"] 
        listPath: str               = self._yamlRawProperty["list_path"]

        paramToReach: list[GateParameter] = [gateTree.getObjectFromGateObjectPath(self._gateObjectParent, objectPath[i]).param[labelName[i]] for i in range(len(objectPath))]

        pathToken: list[str]        = [paramToReach[i]._valueList[labelIndex[i]] for i in range(len(paramToReach))]

        for index in range(len(objectPath)):
            listPath = listPath.replace(f"&{index}", pathToken[index])

        self.unitList: list[str] =  gateTree._getYamlData(listPath)
        if len(self.unitList) == 0:
            self.unitList = gateTree._getYamlData("placeholder/empty_units")

        self._updateValueList()

    def _receiveNotificationObjectNameDropdown(self):
        from src.Model.DynamicData.Concreate.GateTree import GateTree
        gateTree = GateTree()
        objectPath: str               = self._yamlRawProperty["object_path"]
        
        observedObjectList = [gateTree.getObjectFromGateObjectPath(self._gateObjectParent, objectPath)]
        self.unitList = []
        while len(observedObjectList) > 0:
            observedObject = observedObjectList.pop(0)
            self.unitList.append(observedObject.name)
            for child in observedObject.children.values():
                observedObjectList.append(child)
        
        if len(self.unitList) == 0:
            self.unitList = gateTree._getYamlData("placeholder/empty_units")
        
        self._updateValueList()

    def _receiveNotificationCheckableObjectNameDropdown(self):
        from src.Model.DynamicData.Concreate.GateTree import GateTree
        gateTree = GateTree()
        objectPath: str               = self._yamlRawProperty["object_path"]

        observedObjectList = [gateTree.getObjectFromGateObjectPath(self._gateObjectParent, objectPath)]
        self.unitList = []
        while len(observedObjectList) > 0:
            observedObject = observedObjectList.pop(0)
            self.unitList.append(observedObject.name)
            for child in observedObject.children.values():
                observedObjectList.append(child)

        if len(self.unitList) == 0:
            self.unitList = gateTree._getYamlData("placeholder/empty_units")

        for fieldIndex, field in enumerate(self.valueList):
            for value in field:
                if value not in self.unitList:
                    self.valueList[fieldIndex].remove(value)
                    self.notifyAllSubscriber()

    def _receiveNotificationChildrenNameDropdown(self):
        from src.Model.DynamicData.Concreate.GateTree import GateTree
        gateTree = GateTree()
        objectPath: str               = self._yamlRawProperty["object_path"]
        
        observedObjectList = list(gateTree.getObjectFromGateObjectPath(self._gateObjectParent, objectPath).children.values())
        self.unitList = []
        while len(observedObjectList) > 0:
            observedObject = observedObjectList.pop(0)
            self.unitList.append(observedObject.name)
            for child in observedObject.children.values():
                observedObjectList.append(child)
        
        if len(self.unitList) == 0:
            self.unitList = gateTree._getYamlData("placeholder/empty_units")
        
        self._updateValueList()

    def _receiveNotificationAttachedVolumeDropdown(self):
        from src.Model.DynamicData.Concreate.GateTree import GateTree
        gateTree = GateTree()
        
        observedObjectList = [gateTree.getObjectFromGateObjectPath(self._gateObjectParent, gateTree.yamlData["gate"]["object_path"]["WORLD"]["object_path"])]
        self.unitList = []
        while len(observedObjectList) > 0:
            observedObject = observedObjectList.pop(0)
            if observedObject.param["Attach Volume to System"].valueList[0]:
                self.unitList.append(observedObject.name)
            for child in observedObject.children.values():
                observedObjectList.append(child)
        
        if len(self.unitList) == 0:
            self.unitList = gateTree._getYamlData("placeholder/empty_units")
        
        self._updateValueList()

    def _receiveNotificationDigitizerDetectorDropdown(self):
        from src.Model.DynamicData.Concreate.GateTree import GateTree
        gateTree = GateTree()

        observedObjectList = list(gateTree.getObjectFromGateObjectPath(self._gateObjectParent, gateTree.yamlData["gate"]["object_path"]["DIGITIZER"]["object_path"]).children.values())
        self.unitList = []
        while len(observedObjectList) > 0:
            observedObject = observedObjectList.pop(0)
            if not observedObject.name == self._gateObjectParent.parent.name:
                detectorObject = gateTree.getObjectFromGateObjectPath(self, observedObject.param["Detector Volume Path"].valueList[0])
                inputName = f"{observedObject.name}_{detectorObject.name}"
                self.unitList.append(inputName)

        if len(self.unitList) == 0:
            self.unitList = gateTree._getYamlData("placeholder/empty_units")

        self._updateValueList()

    def _receiveNotificationDynamicLabel(self):
        from src.Model.DynamicData.Concreate.GateTree import GateTree
        gateTree = GateTree()
        
        objectPath: list[str]       = self._yamlRawProperty["object_path"]
        labelName: list[str]        = self._yamlRawProperty["object_label"]
        labelIndex: list[int]       = self._yamlRawProperty["object_label_index"]
        self.displayedLabel: str    = self._yamlRawProperty["label"]
        
        paramToReach: list[GateParameter] = [gateTree.getObjectFromGateObjectPath(self._gateObjectParent, objectPath[i]).param[labelName[i]] for i in range(len(objectPath))]
        
        pathToken: list[str]        = [paramToReach[i]._valueList[labelIndex[i]] for i in range(len(paramToReach))]
        
        for index in range(len(objectPath)):
            self.displayedLabel = self.displayedLabel.replace(f"&{index}", pathToken[index])

    def _receiveNotificationDynamicObjectNameDropdown(self):
        from src.Model.DynamicData.Concreate.GateTree import GateTree
        gateTree = GateTree()
        objectPath: list[str]       = self._yamlRawProperty["object_path"]
        labelName: list[str]        = self._yamlRawProperty["object_label"]
        labelIndex: list[int]       = self._yamlRawProperty["object_label_index"] 
        listPath: str               = self._yamlRawProperty["list_path"]
        
        paramToReach: list[GateParameter] = [gateTree.getObjectFromGateObjectPath(self._gateObjectParent, objectPath[i]).param[labelName[i]] for i in range(len(objectPath))]
        
        pathToken: list[str]        = [paramToReach[i]._valueList[labelIndex[i]] for i in range(len(paramToReach))]
        
        for index in range(len(objectPath)):
            listPath = listPath.replace(f"&{index}", pathToken[index])
        
        observedObjectList = [gateTree.getObjectFromGateObjectPath(self._gateObjectParent, listPath)]
        self.unitList = []
        while len(observedObjectList) > 0:
            observedObject = observedObjectList.pop(0)
            self.unitList.append(observedObject.name)
            for child in observedObject.children.values():
                observedObjectList.append(child)
        
        if len(self.unitList) == 0:
            self.unitList = gateTree._getYamlData("placeholder/empty_units")
        
        self._updateValueList()      

    def _updateValueList(self):
        for index, value in enumerate(self.valueList):
            if value not in self.unitList:
                self.valueList[index] = self.unitList[0]
                self.notifyAllSubscriber()

    def updateValue(self, fieldIndex: int, newData: str | float | bool):
        """
        Update value of the parameter and notify all subscriber of the update.
        
        Args:
            fieldIndex: index of the value in the value list
            newData: value to update the value list with
        """
        self._valueList[fieldIndex] = newData
        # Notify static subscriber
        self.notifyAllSubscriber()

        # Notify dynamic subscriber
        broker = SignalBroker()
        broker.emitSignalFromPublisher(self)


    def updateUnitIndex(self, newIndex: int):
        """
        Update the units

        Args:
            newIndex: index of the updated unit.
        """
        self._defaultUnitIndex = newIndex

    ### GateParameterInterface Implementation
    @property
    def path(self) -> str:
        return self._path

    @property
    def displayedLabel(self) -> str:
        return self._displayedLabel

    @property
    def inputType(self) -> str:
        return self._inputType

    @property
    def defaultValueList(self) -> list[str] | list[float]:
        return self._defaultValueList

    @property
    def valueList(self) -> list[str] | list[float]:
        return self._valueList

    @property
    def unitList(self) -> list[str]:
        return self._unitList

    @property
    def defaultUnitIndex(self) -> int:
        return self._defaultUnitIndex

    @property
    def gateObjectParent(self) -> GateObjectInterface:
        return self._gateObjectParent

    @path.setter
    def path(self, path: str):
        self._path = path

    @displayedLabel.setter
    def displayedLabel(self, displayedLabel: str):
        self._displayedLabel = displayedLabel

    @inputType.setter
    def inputType(self, inputType: str):
        self._inputType = inputType

    @defaultValueList.setter
    def defaultValueList(self, defaultValueList: list[str] | list[float]):
        self._defaultUnitIndex = defaultValueList

    @valueList.setter
    def valueList(self, valueList: list[str] | list[float]):
        self._valueList = valueList

    @unitList.setter
    def unitList(self, unitList: list[str]):
        self._unitList = unitList

    @defaultUnitIndex.setter
    def defaultUnitIndex(self, defaultUnitIndex: int):
        self._defaultUnitIndex = defaultUnitIndex


from src.Control.SignalBroker import SignalBroker
    


            