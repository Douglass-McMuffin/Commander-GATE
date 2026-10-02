import src.Model.StaticData.StaticData as StaticData



class GateParameter(object):
    def __init__(
            self, 
            path: str,
            displayed_label: str, 
            input_type_list: str, 
            default_value_list: list[any],
            unit_list: list[str] = None, 
            default_unit_index: int = 0,
            yaml_raw_property: dict[str, any] = {}
        ):
        self.path = path
        self.displayed_label = displayed_label
        self.input_type_list = input_type_list        
        self.default_value_list = default_value_list
        self.value_list = default_value_list
        self.unit_list = unit_list
        self.default_unit_index = default_unit_index
        self.yamlRawProperty = yaml_raw_property

        self.subscriberValueChanged: list[GateParameter] = []

    def __repr__(self):
        return f"Param <\"{self.displayed_label}\">"
    
    def to_dict(self):
        return {
            "path": self.path,
            "name": self.displayed_label,
            "input_types": self.input_type_list,
            "default_values": self.default_value_list,
            "values": self.value_list,
            "unit_list": self.compare_lists(),
            "chosen_unit": self.default_unit
        }
        
    def compare_lists(self):
        """Compares the stored unit_list with unit lists in StaticData and returns the matching list name as a string."""
        if not self.unit_list:
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
            if set(self.unit_list) == set(predefined_list):  # Compare as sets to avoid order dependency
                return list_name

        return "UNKNOWN"  # If no match is found


    def addSubcriber(self, gateParameter: GateParameter):
        self.subscriberValueChanged.append(gateParameter)

    def notifyAllSubscriber(self):
        for parameter in self.subscriberValueChanged:
            parameter.receiveNotification(self)

    def notifyOneSubscriber(self, gateParameter: GateParameter):
        gateParameter.receiveNotification(self)

    def receiveNotification(self, context: GateParameter):
        if self.input_type_list == "dynamic_dropdown":
            gateTree = GateTree()

            objectPath: list[str]       = self.yamlRawProperty["object_path"]
            labelName: list[str]        = self.yamlRawProperty["object_label"]
            labelIndex: list[int]       = self.yamlRawProperty["object_label_index"] 
            listPath: str               = self.yamlRawProperty["list_path"]
            
            paramToReach: list[GateParameter] = [gateTree.getParamFromGateObjectPath(objectPath[i], labelName[i]) for i in range(len(objectPath))]
            
            pathToken: list[str]        = [paramToReach[0].value_list[labelIndex[i]] for i in range(len(paramToReach))]
            
            for index in range(len(objectPath)):
                listPath = listPath.replace(f"&{index}", pathToken[index])
            
            self.unit_list: list[str] =  gateTree.getDataFromYamlPath(listPath)

            for index, value in enumerate(self.value_list):
                if value not in self.unit_list:
                    self.value_list[index] = self.unit_list[0]

    def updateField(self, fieldIndex: int, newData: str | float):
        self.value_list[fieldIndex] = newData
        self.notifyAllSubscriber()



from src.Model.DynamicData.GateTree import GateTree            