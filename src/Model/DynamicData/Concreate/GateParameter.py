import src.Model.StaticData.StaticData as StaticData
from src.Model.DynamicData.Interface.GateParameterInterface import GateParameterInterface



class GateParameter(GateParameterInterface):
    def __init__(
            self, 
            path: str,
            displayed_label: str, 
            input_type_list: str, 
            default_value_list: list[str | int | float],
            unit_list: list[str] = [], 
            default_unit_index: int = 0,
            yaml_raw_property: dict[str, str | int | list[str]] = {}
        ):
        self._path = path
        self._displayedLabel = displayed_label
        self._inputTypeList = input_type_list        
        self._defaultValueList = default_value_list
        self._valueList = default_value_list
        self._unitList = unit_list
        self._defaultUnitIndex = default_unit_index
        self._yamlRawProperty = yaml_raw_property

        self._subscriberValueChanged: list[GateParameter] = []

    def __repr__(self):
        return f"Param <\"{self._displayedLabel}\">"
    
    def to_dict(self):
        return {
            "path": self._path,
            "name": self._displayedLabel,
            "input_types": self._inputTypeList,
            "default_values": self._defaultValueList,
            "values": self._valueList,
            "unit_list": self.compare_lists(),
            "chosen_unit": self._unitList
        }
        
    def compare_lists(self):
        """Compares the stored unit_list with unit lists in StaticData and returns the matching list name as a string."""
        if not self._unitList:
            return None  # No unit list to compare
        
        unit_lists = {
            "LENGTH_UNITS": StaticData.LENGTH_UNITS,
            "SURFACE_UNITS": StaticData.SURFACE_UNITS,
            "VOLUME_UNITS": StaticData.VOLUME_UNITS,
            "ANGLE_UNITS": StaticData.ANGLE_UNITS,
            "TIME_UNITS": StaticData.TIME_UNITS,
            "SPEED_UNITS": StaticData.SPEED_UNITS,
            "ANGULAR_SPEED_UNITS": StaticData.ANGULAR_SPEED_UNITS,
            "ENERGY_UNITS": StaticData.ENERGY_UNITS,
            "ACTIVITY_DOSE_UNITS": StaticData.ACTIVITY_DOSE_UNITS,
            "AMOUNT_OF_SUBSTANCE_UNITS": StaticData.AMOUNT_OF_SUBSTANCE_UNITS,
            "MASS_UNITS": StaticData.MASS_UNITS,
            "VOLUMIC_MASS_UNITS": StaticData.VOLUMIC_MASS_UNITS,
            "ELECTRIC_CHARGE_UNITS": StaticData.ELECTRIC_CHARGE_UNITS,
            "ELECTRIC_CURRENT_UNITS": StaticData.ELECTRIC_CURRENT_UNITS,
            "ELECTRIC_POTENTIAL_UNITS": StaticData.ELECTRIC_POTENTIAL_UNITS,
            "MAGNETIC_FLUX_UNITS": StaticData.MAGNETIC_FLUX_UNITS,
            "TEMPERATURE_UNITS": StaticData.TEMPERATURE_UNITS,
            "FORCE_PRESSURE_UNITS": StaticData.FORCE_PRESSURE_UNITS,
            "POWER_UNITS": StaticData.POWER_UNITS,
            "FREQUENCY_UNITS": StaticData.FREQUENCY_UNITS
        }

        for list_name, predefined_list in unit_lists.items():
            if set(self._unitList) == set(predefined_list):  # Compare as sets to avoid order dependency
                return list_name

        return "UNKNOWN"  # If no match is found


    def addSubcriber(self, gateParameter: GateParameter):
        self._subscriberValueChanged.append(gateParameter)

    def notifyAllSubscriber(self):
        for parameter in self._subscriberValueChanged:
            parameter.receiveNotification(self)

    def notifyOneSubscriber(self, gateParameter: GateParameter):
        gateParameter.receiveNotification(self)

    def receiveNotification(self, context: GateParameter):
        if self._inputTypeList == "dynamic_dropdown":
            gateTree = GateTree()

            objectPath: list[str]       = self._yamlRawProperty["object_path"]
            labelName: list[str]        = self._yamlRawProperty["object_label"]
            labelIndex: list[int]       = self._yamlRawProperty["object_label_index"] 
            listPath: str               = self._yamlRawProperty["list_path"]
            
            paramToReach: list[GateParameter] = [gateTree.getParamFromGateObjectPath(objectPath[i], labelName[i]) for i in range(len(objectPath))]
            
            pathToken: list[str]        = [paramToReach[0]._valueList[labelIndex[i]] for i in range(len(paramToReach))]
            
            for index in range(len(objectPath)):
                listPath = listPath.replace(f"&{index}", pathToken[index])
            
            self.unitList: list[str] =  gateTree.getDataFromYamlPath(listPath)

            for index, value in enumerate(self._valueList):
                if value not in self._unitList:
                    self._valueList[index] = self._unitList[0]

    def updateField(self, fieldIndex: int, newData: str | float):
        self._valueList[fieldIndex] = newData
        self.notifyAllSubscriber()

    ### GateParameterInterface Implementation
    @property
    def path(self) -> str:
        return self._path

    @property
    def displayedLabel(self) -> str:
        return self._displayedLabel

    @property
    def inputTypeList(self) -> str:
        return self._inputTypeList

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

    @path.setter
    def path(self, path: str):
        self._path = path

    @displayedLabel.setter
    def displayedLabel(self, displayedLabel: str):
        self._displayedLabel = displayedLabel

    @inputTypeList.setter
    def inputTypeList(self, inputTypeList: str):
        self._inputTypeList = inputTypeList

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


    


from src.Model.DynamicData.Concreate.GateTree import GateTree            