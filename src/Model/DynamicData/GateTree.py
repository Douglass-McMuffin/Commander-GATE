"""
The GateTree represent the tree structure of the GATE simulation.
The main purpose of this class is to provide a convenient way to access the GATE simulation data and to perform various operations on it.
"""
from src.Model.DynamicData.GateObject import GateObject
from src.Model.DynamicData.GateParameter import GateParameter
import yaml


class SingletonMeta(type):
    _instances = {}
    _lock = None  # Initialize in __new__ or use a lock for thread safety

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class GateTree(metaclass=SingletonMeta):

    def setup(self, materialDBPath: str):
        self.yamlData: dict
        self.children: dict[str, GateObject] = {} 
        self.material: list[str]



        with open("src/Model/StaticData/GATE10Configuration.yaml", "r") as file:
            self.yamlData = yaml.safe_load(file)

           
        self.material = self.readMaterialDB(materialDBPath) # Initialise at the first creation, but not necessary after

        objectPathDict: dict = self.yamlData["gate"]["object_path"]
        for pathDict in objectPathDict.values():
            yamlPath = pathDict["yaml_path"]
            yamlPathToken = yamlPath.split("/")
            objectPath = pathDict["object_path"]
            objectPathToken = objectPath.split("/")
            parentObject: GateObject | GateTree = self
            for token in objectPathToken:
                if token == objectPathToken[-1]:
                    # Create the GateObject
                    if parentObject == self:
                        if "volume" in yamlPathToken:
                            self.children[token] = self.createVolume(token, yamlPathToken[-2], self.material, yamlPathToken[-1])
                            
                        else:
                            self.children[token] = self.createGateObjectFromYamlSection(objectPath, token, self.getDataFromYamlPath(yamlPath))
                    else:
                        if "volume" in yamlPathToken:                   
                            parentObject.addChild(self.createVolume(token, yamlPathToken[-2], self.material, yamlPathToken[-1]))  
                        else:
                            parentObject.addChild(self.createGateObjectFromYamlSection(objectPath, token, self.getDataFromYamlPath(yamlPath)))                        

                else:
                    # Continue down the tree
                    parentObject = parentObject.children[token]

    def __repr__(self):
        return f"material: {self.material}, children: {list(self.children.values())}\n"

    def __getitem__(self, key: str):
        return self.children[key]

    ### Volume factory

    # tiny joiners
    @staticmethod
    def _noMacroFormater(name: str = None, sub: str = None) -> str: return ""

    @staticmethod
    def _noNameMacroFormater(name: str = None, sub: str = "") -> str: return f"/{sub}"

    @staticmethod
    def _normalMacroFormater(name: str, sub: str = "") -> str: return f"/{name}/{sub}"

    @staticmethod
    def _geometryMacroFormater(name: str, sub: str) -> str: return f"/{name}/geometry/{sub}"

    @staticmethod
    def _visMacroFormater(name: str, sub: str) -> str:  return f"/{name}/vis/{sub}"

    def getObjectFromGateObjectPath(self, gateObjectPath: str) -> GateObject:
        pathToken : list[str] = self.yamlData["gate"]["object_path"][gateObjectPath]["object_path"].split("/")
        gateObject = self
        
        for token in pathToken:
            gateObject = gateObject[token]

        return gateObject

    @staticmethod
    def getParamFromGateObject(gateObject: GateObject, labelName: str) -> GateParameter:
        for paramObject in gateObject.param:
            if paramObject.displayed_label== labelName:
                return paramObject

    def getParamFromGateObjectPath(self, gateObjectPath: str, labelName: str) -> GateParameter:
        gateObject: GateObject = self.getObjectFromGateObjectPath(gateObjectPath)
        return self.getParamFromGateObject(gateObject, labelName)
    
    def getDataFromYamlPath(self, yamlPath: str):
        pathToken = yamlPath.split("/")
    
        yamlPartialData = self.yamlData
        for token in pathToken:
            yamlPartialData = yamlPartialData[token]
    
        return yamlPartialData

    def readMaterialDB(self, materialDBPath: str) -> list[str]:
        
        with open(materialDBPath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        section = None

        currentMaterialLines = []
        materialList = []

        for line in lines:
            line = line.strip()

            if not line or line.startswith("#"): #Skip empty or comment line
                continue

            if line.startswith("[") and line.endswith("]"): #Section header
                section = line.strip("[]").lower()
                continue

            if section == "materials":
                if not line.startswith("+") and len(currentMaterialLines) > 0:
                    materialList.append(currentMaterialLines[0].split(":"))
                    currentMaterialLines.clear()

                currentMaterialLines.append(line)      

        return materialList

    ### param row factories

    def createParamSection(self, name:str, paramSection: list[dict], macroFormater: function) -> list[GateParameter]:
        gateParameterList: list[GateParameter] = []

        paramRowBuilder = {
            "text":     self.createParamTextRow,
            "dropdown": self.createParamDropdownRow,
            "checkbox": self.createParamCheckboxRow,
            "select":   self.createParamSelectRow,
            "label":    self.createParamLabelRow,
            "dynamic_dropdown": self.createParamDynamicDropdown,
            "macro_dropdown": self.createParamDropdownRow,
            "material_dropdown": self.createParamMaterialDropdown
        }
        
        for param in paramSection:
            type_input: str = param["property"]["type"]
            gateParameterList += paramRowBuilder[type_input](name, param, macroFormater)

        return gateParameterList

    def createParamTextRow(self, name: str, param: dict, macroFormater: function) -> list[GateParameter]:
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[any] = param["property"]["default_value"]
        unit_type: str = param["property"]["units"]
        unit_list: list[str] = self.yamlData["gate"]["units"][unit_type]
        default_unit_index: int = param["property"]["default_unit_index"]

        return [
            GateParameter(macroFormater(name, label_macro_dict["macro"]), label_macro_dict["label"], type_input, default_value, unit_list, default_unit_index, param["property"]) 
            for label_macro_dict in param["label_list"]]

    def createParamDropdownRow(self, name: str, param: dict, macroFormater: function) -> list[GateParameter]:
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

        return [GateParameter(macroFormater(name, label_macro_dict["macro"]), label_macro_dict["label"], type_input, default_value, value_list, default_unit_index, param["property"]) for label_macro_dict in param["label_list"]]

    def createParamCheckboxRow(self, name: str, param: dict, macroFormater: function) -> list[GateParameter]:
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[bool] = param["property"]["default_value"]

        return [GateParameter(macroFormater(name, label_macro_dict["macro"]), label_macro_dict["label"], type_input, default_value, None, None) for label_macro_dict in param["label_list"]]

    def createParamSelectRow(self, name: str, param: dict, macroFormater: function) -> list[GateParameter]:
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[any] = param["property"]["default_value"]

        return [GateParameter(macroFormater(name, label_macro_dict["macro"]), label_macro_dict["label"], type_input, default_value, None, None, param["property"]) for label_macro_dict in param["label_list"]]

    def createParamLabelRow(self, name: str, param: dict, macroFormater: function) -> list[GateParameter]:
        # Get the value out of "property"
        type_input: str = param["property"]["type"]

        return [GateParameter("", label_macro_dict["label"], type_input, None, None, None, param["property"]) for label_macro_dict in param["label_list"]]

    def createParamDynamicDropdown(self, name: str, param: dict, macroFormater: function) -> list[GateParameter]:
        # Get the value out of "property"
        default_value: list[any]    = param["property"]["default_value"]
        
        objectPath: list[str]       = param["property"]["object_path"]
        labelName: list[str]        = param["property"]["object_label"]
        labelIndex: list[int]       = param["property"]["object_label_index"] 
        listPath: str               = param["property"]["list_path"]

        paramToReach: list[GateParameter] = [self.getParamFromGateObjectPath(objectPath[i], labelName[i]) for i in range(len(objectPath))]

        pathToken: list[str]        = [paramToReach[i].value_list[labelIndex[i]] for i in range(len(paramToReach))]
        
        for i in range(len(objectPath)):
            listPath = listPath.replace(f"&{i}", pathToken[i])

        value_list: list[str] =  self.getDataFromYamlPath(listPath)

        for value in default_value:
            if type(value) == str:
                default_unit_index = value_list.index(value)
            elif type(value) == int:
                default_unit_index = value
                default_value = [value_list[value]]

        parameterList = [GateParameter(macroFormater(name, label_macro_dict["macro"]), label_macro_dict["label"], "dynamic_dropdown", default_value, value_list, default_unit_index, param["property"]) for label_macro_dict in param["label_list"]]
        for parameterSubscriber in parameterList:
            for parameterPublisher in paramToReach:
                parameterPublisher.addSubcriber(parameterSubscriber)
                parameterPublisher.notifyOneSubscriber(parameterSubscriber)
                
        return parameterList
    
    def createParamMaterialDropdown(self, name: str, param: dict, macroFormater: function) -> list[GateParameter]:
        default_value: list[any]    = param["property"]["default_value"]
        value_list: list[str]       = self.material

        for value in default_value:
            if type(value) == str:
                default_unit_index = value_list.index(value)
            elif type(value) == int:
                default_unit_index = value
                default_value = [value_list[value]]

        return [GateParameter(macroFormater(name, label_macro_dict["macro"]), label_macro_dict["label"], "dropdown", default_value, value_list, default_unit_index, param["property"]) for label_macro_dict in param["label_list"]]

    ### gate children factories

    def createVolume(self, name: str, type:str, materialDB:list[str], repeaterType: str) -> GateObject:
        volumeParamList: list[dict] = self.yamlData["gate"]["parameter"]["volume"][type]
        gateParameterList: list[GateParameter] = []

        
        gateParameterList += self.createParamSection(name, volumeParamList, self._geometryMacroFormater)

        gateParameterList.append(GateParameter(self._normalMacroFormater(name) + "setMaterial", "Material", "dropdown", [None], materialDB, {}))

        ### General parameter for a volume
        # placement parameters
        paramSection: list[dict] = self.yamlData["gate"]["parameter"]["volume"]["volume_general"]["placement_parameters"]
        gateParameterList += self.createParamSection(name, paramSection, self._normalMacroFormater)

        # moving parameters
        paramSection = self.yamlData["gate"]["parameter"]["volume"]["volume_general"]["moving_parameters"]
        gateParameterList += self.createParamSection(name, paramSection, self._normalMacroFormater)

        # visualization parameters
        paramSection = self.yamlData["gate"]["parameter"]["volume"]["volume_general"]["visualization_parameters"]
        gateParameterList += self.createParamSection(name, paramSection, self._visMacroFormater)

        # repeater parameters
        paramSection = self.yamlData["gate"]["parameter"]["volume"]["volume_repeater"][repeaterType]
        gateParameterList += self.createParamSection(name, paramSection, self._normalMacroFormater)

        # attach system parameters
        paramSection = self.yamlData["gate"]["parameter"]["volume"]["attach_systems"]
        gateParameterList += self.createParamSection(name, paramSection, self._normalMacroFormater)
        
        return GateObject("", name, param=gateParameterList)

    def createGateObjectFromYamlSection(self, path:str, name: str, yamlSection: dict) -> GateObject:
        parameterList : list[GateParameter] = self.createParamSection("", yamlSection, self._noNameMacroFormater)

        return GateObject(path, name, param=parameterList)




