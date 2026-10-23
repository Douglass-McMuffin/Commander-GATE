"""
The GateTree represent the tree structure of the GATE simulation.
The main purpose of this class is to provide a convenient way to access the GATE simulation data and to perform various operations on it.
"""
from src.Model.DynamicData.Concreate.GateObject import GateObject
from src.Model.DynamicData.Concreate.GateParameter import GateParameter
from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface
from abc import ABCMeta
import yaml



class SingletonMeta(ABCMeta):
    _instances = {}
    _lock = None  # Initialize in __new__ or use a lock for thread safety

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class GateTree(GateObjectInterface, metaclass=SingletonMeta):

    def setup(self, materialDBPath: str):
        self.yamlData: dict
        self._children: dict[str, GateObject] = {} 
        self.material: list[str]
        self.gateTreeSubscriber: list[GateParameter] = []


        with open("src/Model/StaticData/GATE10Configuration.yaml", "r") as file:
            self.yamlData = yaml.safe_load(file)

           
        self.material = self.readMaterialDB(materialDBPath) # Initialise at the first creation, but not necessary after

        objectPathDict: dict = self.yamlData["gate"]["object_path"]
        for pathDict in objectPathDict.values():
            self.createGateObjectEmpty(pathDict["object_path"])

        for pathDict in objectPathDict.values():
            gateObject = self.getObjectFromGateObjectPath(self, pathDict["object_path"])
            yamlPath = pathDict["yaml_path"]
            yamlPathToken = yamlPath.split("/")
            if gateObject.path.startswith("/gate/world"):
                self.addVolumeParam(gateObject, yamlPathToken[-2], yamlPathToken[-1])
            else:
                self.addParamFromYamlSection(gateObject, self._getYamlData(yamlPath))
            self.initObjectParam(gateObject)

    def __repr__(self):
        return f"material: {self.material}, children: {list(self.children.values())}\n"

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

    def getObjectFromGateObjectPath(self, gateObjectOrigin: GateObjectInterface, gateObjectPath: str) -> GateObject:
        pathToken : list[str] = gateObjectPath.split("/")
        if pathToken[0] in (".", ".."):
            gateObject = gateObjectOrigin
        else:
            gateObject = self
        pathToken = pathToken[1:]
        
        for token in pathToken:
            if token == "..":
                if gateObject.name == "root":
                    return None
                gateObject = gateObject.parent
            elif token != ".":
                gateObject = gateObject[token]

        return gateObject

    def _getYamlData(self, yamlPath: str):
        yamlToken = yamlPath.split("/")
        if yamlPath[0] == "/":
            yamlToken = yamlToken[1:]

        yamlData = self.yamlData

        for token in yamlToken:
            yamlData = yamlData[token]

        return yamlData

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
                    materialList.append(currentMaterialLines[0].split(":")[0])
                    currentMaterialLines.clear()

                currentMaterialLines.append(line)      

        return materialList

    ### param row factories

    def createStaticParam(self, gateObject: GateObject, paramSection: list[dict], macroFormater: function):
        paramRowBuilder = {
            "text":     self.createParamTextRow,
            "dropdown": self.createParamDropdownRow,
            "checkbox": self.createParamCheckboxRow,
            "select":   self.createParamSelectRow,
            "label":    self.createParamLabelRow,
            "macro_dropdown": self.createParamDropdownRow,
            "material_dropdown": self.createParamMaterialDropdown,
            "macro": self.createParamMacro
        }
        
        paramIndex = len(gateObject.paramList)
        for param in paramSection:
            type_input: str = param["property"]["type"]
            if type_input in paramRowBuilder:
                paramRowBuilder[type_input](gateObject, param, paramIndex, macroFormater)
            else:
                paramIndex -= len(param["label_list"])
            paramIndex += len(param["label_list"])

    def createDynamicParam(self, gateObject: GateObject, paramSection: list[dict], macroFormater: function):
       
        paramRowBuilder = {
            "dynamic_dropdown": self.createParamDynamicDropdown,
            "object_name_dropdown": self.createParamObjectNameDropdownRow,
            "children_name_dropdown": self.createParamChildrenNameDropdownRow,
            "attached_volume_dropdown": self.createParamAttachedVolumeDropdownRow,
            "digitizer_detector_dropdown": self.createParamDigitizerDetectorDropdownRow,
            "dynamic_label": self.createParamDynamicLabel,
            "dynamic_object_name_dropdown": self.createParamDynamicObjectNameDropdownRow
        }

        sectionSizeWithoutDynamicParam = 0
        for param in paramSection:
            if param["property"]["type"] not in paramRowBuilder:
                sectionSizeWithoutDynamicParam += len(param["label_list"])
        
        paramIndex = len(gateObject.paramList) - sectionSizeWithoutDynamicParam
        for param in paramSection:
            type_input: str = param["property"]["type"]
            if type_input in paramRowBuilder:
                paramRowBuilder[type_input](gateObject, param, paramIndex, macroFormater)

            paramIndex += len(param["label_list"])
            
        
    def createParamTextRow(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[any] = param["property"]["default_value"]
        unit_type: str = param["property"]["units"]
        unit_list: list[str] = self.yamlData["gate"]["units"][unit_type]
        default_unit_index: int = param["property"]["default_unit_index"]

        for label_macro_dict in param["label_list"]:
            gateObject.paramList.insert(paramIndex, GateParameter(macroFormater(gateObject.name, label_macro_dict["macro"]), label_macro_dict["label"], type_input, default_value, label_macro_dict["multiplicity"], unit_list, default_unit_index, param["property"]))

    def createParamDropdownRow(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
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

        for label_macro_dict in param["label_list"]:
            gateObject.paramList.insert(paramIndex, GateParameter(macroFormater(gateObject.name, label_macro_dict["macro"]), label_macro_dict["label"], type_input, default_value, label_macro_dict["multiplicity"], value_list, default_unit_index, param["property"]))

    def createParamObjectNameDropdownRow(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[any] = param["property"]["default_value"]
        default_unit_index: int = 0
        object_path: list[str] = param["property"]["object_path"]

        observedObjectList = [self.getObjectFromGateObjectPath(gateObject, object_path)]
        unit_list = []
        while len(observedObjectList) > 0:
            observedObject = observedObjectList.pop(0)
            unit_list.append(observedObject.name)
            for child in observedObject.children.values():
                observedObjectList.append(child)
        
        for value in default_value:
            if type(value) == str:
                default_unit_index = unit_list.index(value)
            elif type(value) == int:
                default_unit_index = value
                default_value = [unit_list[value]]

        for label_macro_dict in param["label_list"]:
            gateParameter = GateParameter(macroFormater(gateObject.name, label_macro_dict["macro"]), label_macro_dict["label"], type_input, default_value, label_macro_dict["multiplicity"], unit_list, default_unit_index, param["property"])
            gateObject.paramList.insert(paramIndex, gateParameter)
            self.gateTreeSubscriber.append(gateParameter)

    def createParamChildrenNameDropdownRow(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[any] = param["property"]["default_value"]
        default_unit_index: int = 0
        object_path: list[str] = param["property"]["object_path"]

        observedObjectList = [self.getObjectFromGateObjectPath(gateObject, object_path).children.values()]
        unit_list = self._getYamlData("placeholder/empty_units")
        while len(observedObjectList) > 0:
            observedObject = observedObjectList.pop(0)
            unit_list.append(observedObject.name)
            for child in observedObject.children.values():
                observedObjectList.append(child)

        for value in default_value:
            if type(value) == str:
                default_unit_index = unit_list.index(value)
            elif type(value) == int:
                default_unit_index = value
                default_value = [unit_list[value]]

        for label_macro_dict in param["label_list"]:
            gateParameter = GateParameter(macroFormater(gateObject.name, label_macro_dict["macro"]), label_macro_dict["label"], type_input, default_value, label_macro_dict["multiplicity"], unit_list, default_unit_index, param["property"])
            gateObject.paramList.insert(paramIndex, gateParameter)
            self.gateTreeSubscriber.append(gateParameter)

    def createParamDigitizerDetectorDropdownRow(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[any] = param["property"]["default_value"]
        default_unit_index: int = 0

        observedObjectList = list(self.getObjectFromGateObjectPath(gateObject, self._getYamlData("gate/object_path/DIGITIZER/object_path")).children.values())
        unit_list = []
        while len(observedObjectList) > 0:
            observedObject = observedObjectList.pop(0)
            if observedObject.name != gateObject.name:
                detectorObject = self.getObjectFromGateObjectPath(observedObject.param["Detector Volume Path"].valueList[0])
                inputName = f"{observedObject.name}_{detectorObject.name}"
                unit_list.append(inputName)

        for value in default_value:
            if type(value) == str:
                default_unit_index = unit_list.index(value)
            elif type(value) == int:
                default_unit_index = value
                default_value = [unit_list[value]]

        for label_macro_dict in param["label_list"]:
            gateParameter = GateParameter(macroFormater(gateObject.name, label_macro_dict["macro"]), label_macro_dict["label"], type_input, default_value, label_macro_dict["multiplicity"], unit_list, default_unit_index, param["property"])
            gateObject.paramList.insert(paramIndex, gateParameter)
            self.gateTreeSubscriber.append(gateParameter)

    def createParamAttachedVolumeDropdownRow(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[any] = param["property"]["default_value"]
        default_unit_index: int = 0

        observedObjectList = [self.getObjectFromGateObjectPath(gateObject, self._getYamlData("gate/object_path/WORLD/object_path"))]
        unit_list = []
        while len(observedObjectList) > 0:
            observedObject = observedObjectList.pop(0)
            if observedObject.param["Attach Volume to System"].valueList[0]:
                unit_list.append(observedObject.name)
            for child in observedObject.children.values():
                observedObjectList.append(child)

        for value in default_value:
            if type(value) == str:
                default_unit_index = unit_list.index(value)
            elif type(value) == int:
                default_unit_index = value
                default_value = [unit_list[value]]

        for label_macro_dict in param["label_list"]:
            gateParameter = GateParameter(macroFormater(gateObject.name, label_macro_dict["macro"]), label_macro_dict["label"], type_input, default_value, label_macro_dict["multiplicity"], unit_list, default_unit_index, param["property"])
            gateObject.paramList.insert(paramIndex, gateParameter)
            self.gateTreeSubscriber.append(gateParameter)

    def createParamCheckboxRow(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[bool] = param["property"]["default_value"]

        for label_macro_dict in param["label_list"]:
            gateObject.paramList.insert(paramIndex, GateParameter(macroFormater(gateObject.name, label_macro_dict["macro"]), label_macro_dict["label"], type_input, default_value, label_macro_dict["multiplicity"], None, None))

    def createParamSelectRow(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: list[any] = param["property"]["default_value"]

        for label_macro_dict in param["label_list"]:
            gateObject.paramList.insert(paramIndex, GateParameter(macroFormater(gateObject.name, label_macro_dict["macro"]), label_macro_dict["label"], type_input, default_value, label_macro_dict["multiplicity"], None, None, param["property"]))

    def createParamLabelRow(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]

        for label_macro_dict in param["label_list"]:
            gateObject.paramList.insert(paramIndex, GateParameter("", label_macro_dict["label"], type_input, [0], label_macro_dict["multiplicity"], None, None, param["property"]))

    def createParamDynamicDropdown(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        # Get the value out of "property"
        default_value: list[any]    = param["property"]["default_value"]
        
        objectPath: list[str]       = param["property"]["object_path"]
        labelName: list[str]        = param["property"]["object_label"]
        labelIndex: list[int]       = param["property"]["object_label_index"] 
        listPath: str               = param["property"]["list_path"]

        paramToReach: list[GateParameter] = []
        for labelNameIndex, object in enumerate([self.getObjectFromGateObjectPath(gateObject, objectPath[i]) for i in range(len(objectPath))]):
            for parameter in object.paramList:
                if parameter.displayedLabel == labelName[labelNameIndex]:
                    paramToReach.append(parameter)
        
        pathToken: list[str]        = [paramToReach[i].valueList[labelIndex[i]] for i in range(len(paramToReach))]
        
        for i in range(len(objectPath)):
            listPath = listPath.replace(f"&{i}", pathToken[i])

        unit_list: list[str] =  self._getYamlData(listPath)

        if len(unit_list) > 0:
            for value in default_value:
                if type(value) == str:
                    default_unit_index = unit_list.index(value)
                elif type(value) == int:
                    default_unit_index = value
                    default_value = [unit_list[value]]
        else: # If there is nothing in the unit list, put the placeholder for nothing
            unit_list = self._getYamlData("placeholder/empty_units")
            default_unit_index = 0
            default_value = [unit_list[default_unit_index]] * len(default_value)
            


        for label_macro_dict in param["label_list"]:
            gateParameter = GateParameter(macroFormater(gateObject.name, label_macro_dict["macro"]), label_macro_dict["label"], "dynamic_dropdown", default_value, label_macro_dict["multiplicity"], unit_list, default_unit_index, param["property"])
            gateObject.paramList.insert(paramIndex, gateParameter)
            for parameterPublisher in paramToReach:
                parameterPublisher.addSubcriber(gateParameter)

    def createParamDynamicLabel(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        objectPath: list[str]       = param["property"]["object_path"]
        labelName: list[str]        = param["property"]["object_label"]
        labelIndex: list[int]       = param["property"]["object_label_index"] 

        paramToReach: list[GateParameter] = []
        for labelNameIndex, object in enumerate([self.getObjectFromGateObjectPath(gateObject, objectPath[i]) for i in range(len(objectPath))]):
            for parameter in object.paramList:
                if parameter.displayedLabel == labelName[labelNameIndex]:
                    paramToReach.append(parameter)

        valueToken: list[str]        = [paramToReach[i].valueList[labelIndex[i]] for i in range(len(paramToReach))]

        for label_macro_dict in param["label_list"]:
            paramLabel = label_macro_dict["label"]

            for i in range(len(objectPath)):
                paramLabel = paramLabel.replace(f"&{i}", valueToken[i])

            gateParameter = GateParameter("", paramLabel, type_input, [0], label_macro_dict["multiplicity"], None, None, param["property"] | label_macro_dict)
            gateObject.paramList.insert(paramIndex, gateParameter)
            for paramPublisher in paramToReach:
                paramPublisher.addSubcriber(gateParameter)

    def createParamMacro(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        # Get the value out of "property"
        type_input: str = param["property"]["type"]
        default_value: str = param["property"]["default_value"]

        for label_macro_dict in param["label_list"]:
            gateObject.paramList.insert(paramIndex, GateParameter(label_macro_dict["macro"], label_macro_dict["label"], type_input, default_value, label_macro_dict["multiplicity"]))

    def createParamDynamicObjectNameDropdownRow(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        # Get the value out of "property"
        default_value: list[any]    = param["property"]["default_value"]
        
        objectPath: list[str]       = param["property"]["object_path"]
        labelName: list[str]        = param["property"]["object_label"]
        labelIndex: list[int]       = param["property"]["object_label_index"] 
        listPath: str               = param["property"]["list_path"]
        
        paramToReach: list[GateParameter] = []
        for labelNameIndex, object in enumerate([self.getObjectFromGateObjectPath(gateObject, objectPath[i]) for i in range(len(objectPath))]):
            for parameter in object.paramList:
                if parameter.displayedLabel == labelName[labelNameIndex]:
                    paramToReach.append(parameter)
        
        pathToken: list[str]        = [paramToReach[i].valueList[labelIndex[i]] for i in range(len(paramToReach))]
        
        for i in range(len(objectPath)):
            listPath = listPath.replace(f"&{i}", pathToken[i])
        
        observedObjectList = [self.getObjectFromGateObjectPath(gateObject, listPath)]
        unit_list = []
        while len(observedObjectList) > 0:
            observedObject = observedObjectList.pop(0)
            unit_list.append(observedObject.name)
            for child in observedObject.children.values():
                observedObjectList.append(child)
        
        
        if len(unit_list) > 0:
            for value in default_value:
                if type(value) == str:
                    default_unit_index = unit_list.index(value)
                elif type(value) == int:
                    default_unit_index = value
                    default_value = [unit_list[value]]
        else: # If there is nothing in the unit list, put the placeholder for nothing
            unit_list = self._getYamlData("placeholder/empty_units")
            default_unit_index = 0
            default_value = [unit_list[default_unit_index]] * len(default_value)
        
        for label_macro_dict in param["label_list"]:
            gateParameter = GateParameter(macroFormater(gateObject.name, label_macro_dict["macro"]), label_macro_dict["label"], "dynamic_dropdown", default_value, label_macro_dict["multiplicity"], unit_list, default_unit_index, param["property"])
            gateObject.paramList.insert(paramIndex, gateParameter)
            for parameterPublisher in paramToReach:
                parameterPublisher.addSubcriber(gateParameter)
    
    def createParamMaterialDropdown(self, gateObject: GateObject, param: dict, paramIndex: int, macroFormater: function):
        default_value: list[any]    = param["property"]["default_value"]
        value_list: list[str]       = self.material

        for value in default_value:
            if type(value) == str:
                default_unit_index = value_list.index(value)
            elif type(value) == int:
                default_unit_index = value
                default_value = [value_list[value]]

        for label_macro_dict in param["label_list"]:
            gateObject.paramList.insert(paramIndex, GateParameter(macroFormater(gateObject.name, label_macro_dict["macro"]), label_macro_dict["label"], "dropdown", default_value, label_macro_dict["multiplicity"], value_list, default_unit_index, param["property"]))

    ### gate children factories

    def addVolumeParam(self, gateObject: GateObject, type:str, repeaterType: str):
        volumeParamList: list[dict] = self.yamlData["gate"]["parameter"]["volume"][type]

        self.createStaticParam(gateObject, volumeParamList, self._geometryMacroFormater)  

        # material parameters
        paramSection: list[dict] = self.yamlData["gate"]["parameter"]["volume"]["volume_general"]["material"]
        self.createStaticParam(gateObject, paramSection, self._normalMacroFormater)
        
        # placement parameters
        paramSection = self.yamlData["gate"]["parameter"]["volume"]["volume_general"]["placement_parameters"]
        self.createStaticParam(gateObject, paramSection, self._normalMacroFormater)

        # moving parameters
        paramSection = self.yamlData["gate"]["parameter"]["volume"]["volume_general"]["moving_parameters"]
        self.createStaticParam(gateObject, paramSection, self._normalMacroFormater)

        # visualization parameters
        paramSection = self.yamlData["gate"]["parameter"]["volume"]["volume_general"]["visualization_parameters"]
        self.createStaticParam(gateObject, paramSection, self._visMacroFormater)

        # repeater parameters
        paramSection = self.yamlData["gate"]["parameter"]["volume"]["volume_repeater"][repeaterType]
        self.createStaticParam(gateObject, paramSection, self._normalMacroFormater)

        # attach system parameters
        paramSection = self.yamlData["gate"]["parameter"]["volume"]["attach_systems"]
        self.createStaticParam(gateObject, paramSection, self._normalMacroFormater)
        self.createDynamicParam(gateObject, paramSection, self._normalMacroFormater)

    def addParamFromYamlSection(self, gateObject: GateObject, yamlSection: dict):
        self.createStaticParam(gateObject, yamlSection, self._noNameMacroFormater)
        self.createDynamicParam(gateObject, yamlSection, self._noNameMacroFormater)
    
    def createGateObjectEmpty(self, objectPath: str) -> GateObject:
        parentPath, childName = objectPath.rsplit("/", 1)
        parentObject = self.getObjectFromGateObjectPath(self, parentPath)
        childObject = GateObject(childName)
        parentObject.addChild(childObject)

        for paramToNotify in self.gateTreeSubscriber:
            paramToNotify.receiveNotification()

        return childObject

    @staticmethod
    def initObjectParam(gateObject: GateObject):
        for param in gateObject.paramList:
            gateObject._param[param.displayedLabel] = param
            param._gateObjectParent = gateObject

        for param in gateObject.param.values():
            param.notifyAllSubscriber()

    ### GateTree abstract implementation
    
    @property
    def path(self):
        return ""

    @property
    def name(self):
        return "root"
    
    @property
    def parent(self):
        return None

    @property
    def param(self):
        return {}

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, childDict: dict[str, GateObject]):
        self._children = childDict
        

