"""
This file's main purpose is to help the initialisation process of the GateTree object such as the parameter of some simulation's properties.
"""
from src.Model.DynamicData.GateParameter import GateParameter
from src.Model.DynamicData.GateObject import GateObject
import yaml

class SingletonMeta(type):
    _instances = {}
    _lock = None  # Initialize in __new__ or use a lock for thread safety

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class GateTreeHelper(metaclass=SingletonMeta):

    def __init__(self):
        with open("src/Model/StaticData/GATE10Configuration.yaml", "r") as file:
            self.yamlData = yaml.safe_load(file)

    ### Volume factory

    # tiny joiners
    @staticmethod
    def _noPathFormater(name: str = None, sub: str = None) -> str: return ""

    @staticmethod
    def _noNamePathFormater(name: str = None, sub: str = "") -> str: return f"/{sub}"

    @staticmethod
    def _normalPathFormater(name: str, sub: str = "") -> str: return f"/{name}/{sub}"

    @staticmethod
    def _geometryPathFormater(name: str, sub: str) -> str: return f"/{name}/geometry/{sub}"

    @staticmethod
    def _visPathFormater(name: str, sub: str) -> str:  return f"/{name}/vis/{sub}"

    def createVolume(self, name: str, type:str, materialDB:list[str], repeaterType: str) -> GateObject:
        volumeParamList: list[dict] = self.yamlData["gate"]["parameter"]["volume"][type]
        gateParameterList: list[GateParameter] = []

        
        gateParameterList += self.createParamSection(name, volumeParamList, self._geometryPathFormater)

        gateParameterList.append(GateParameter(self._normalPathFormater(name) + "setMaterial", "Material", "dropdown", [None], materialDB))

        ### General parameter for a volume
        # placement parameters
        paramSection: list[dict] = self.yamlData["gate"]["parameter"]["volume"]["volume_general"]["placement_parameters"]
        gateParameterList += self.createParamSection(name, paramSection, self._normalPathFormater)

        # moving parameters
        paramSection = self.yamlData["gate"]["parameter"]["volume"]["volume_general"]["moving_parameters"]
        gateParameterList += self.createParamSection(name, paramSection, self._normalPathFormater)

        # visualization parameters
        paramSection = self.yamlData["gate"]["parameter"]["volume"]["volume_general"]["visualization_parameters"]
        gateParameterList += self.createParamSection(name, paramSection, self._visPathFormater)

        # repeater parameters
        paramSection = self.yamlData["gate"]["parameter"]["volume"]["volume_repeater"][repeaterType]
        gateParameterList += self.createParamSection(name, paramSection, self._normalPathFormater)
        
        return GateObject("", name, param=gateParameterList)

    def createParamSection(self, name:str, paramSection: list[dict], pathFormater: function) -> list[GateParameter]:
        gateParameterList: list[GateParameter] = []

        paramRowBuilder = {
            "text": self.createParamTextRow,
            "dropdown": self.createParamDropdownRow,
            "checkbox": self.createParamCheckboxRow,
            "select": self.createParamSelectRow,
            "label": self.createParamLabelRow
        }
        
        for param in paramSection:
            type_input: str = param["property"]["type"]
            gateParameterList += paramRowBuilder[type_input](name, param, pathFormater)

        return gateParameterList

    def createParamTextRow(self, name: str, param: dict, pathFormater: function) -> list[GateParameter]:
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[any] = param["property"]["default_value"]
        unit_type: str = param["property"]["units"]
        unit_list: list[str] = self.yamlData["gate"]["units"][unit_type]
        default_unit_index: int = param["property"]["default_unit_index"]

        return [
            GateParameter(pathFormater(name, label_path_dict["path"]), label_path_dict["label"], type_input, default_value, unit_list, default_unit_index) 
            for label_path_dict in param["label_list"]]

    def createParamDropdownRow(self, name: str, param: dict, pathFormater: function) -> list:
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[any] = param["property"]["default_value"]
        default_unit_index: int = 0
        value_list: list[str] = self.yamlData["gate"]["units"][param["property"]["value_list"]]

        for value in default_value:
            if type(value) == str:
                default_unit_index = value_list.index(value)
            elif type(value) == int:
                default_unit_index = value
                default_value = [value_list[value]]

        return [GateParameter(pathFormater(name, label_path_dict["path"]), label_path_dict["label"], type_input, default_value, value_list, default_unit_index) for label_path_dict in param["label_list"]]

    def createParamCheckboxRow(self, name: str, param: dict, pathFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[bool] = param["property"]["default_value"]

        return [GateParameter(pathFormater(name, label_path_dict["path"]), label_path_dict["label"], type_input, default_value, None, None) for label_path_dict in param["label_list"]]

    def createParamSelectRow(self, name: str, param: dict, pathFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[any] = param["property"]["default_value"]

        return [GateParameter(pathFormater(name, label_path_dict["path"]), label_path_dict["label"], type_input, default_value, None, None) for label_path_dict in param["label_list"]]

    def createParamLabelRow(self, name: str, param: dict, pathFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]

        return [GateParameter("", label_path_dict["label"], type_input, None, None, None) for label_path_dict in param["label_list"]]

    def createParamDynamicDropdown(self, name: str, param: dict, pathFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[any] = param["property"]["default_value"]
        value_list_tag: str = param["property"]["value_list_tag"]

        value_list: list[str] = self.getValueListFromValueListTag(value_list_tag)


    def getValueListFromValueListTag(self, valueListTag: str):
        pass


    ### gate children factories
    
    def createPhysics(self) -> GateObject:
        physicsYamlData = self.yamlData["gate"]["parameter"]["physics"]

        parameterList : list[GateParameter] = self.createParamSection("", physicsYamlData, self._noNamePathFormater)

        return GateObject("/physics", "physics", param=parameterList)

    def createSource(self) -> GateObject:
        return GateObject("/source", "source", [])

    def createSubSource(self, name: str, sourceType: str) -> GateObject:
        parameterList: list[GateParameter] = self.createParamSection(name, self.yamlData["gate"]["parameter"]["source"]["source_general"], self._normalPathFormater)
        parameterList += self.createParamSection(name, self.yamlData["gate"]["parameter"]["source"][sourceType], self._normalPathFormater)
        return GateObject("/source", "source", param=parameterList)

    def createOutput(self) -> GateObject:
        parameterList: list[GateParameter] = self.createParamSection("", self.yamlData["gate"]["parameter"]["output"], self._noNamePathFormater)

        return GateObject("/output", "output", param=parameterList)

    def createAcquisition(self) -> GateObject:
        parameterList: list[GateParameter] = self.createParamSection("", self.yamlData["gate"]["parameter"]["acquisition"], self._noNamePathFormater)

        return GateObject("", "acquisition", param=parameterList)

    def createVis(self) -> GateObject:
            parameterList: list[GateParameter] = self.createParamSection("", self.yamlData["gate"]["parameter"]["vis"], self._noNamePathFormater)
    
            return GateObject("../vis", "vis", param=parameterList)