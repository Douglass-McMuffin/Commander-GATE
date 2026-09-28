import pytest
from src.Model.DynamicData.GateParameter import GateParameter as GPNew
from Classes.GateParameter import GateParameter as GPOld
from src.Model.DynamicData.GateObject import GateObject as GONew
from Classes.GateObject import GateObject as GOOld

from src.Model.HelperFunction.GateTreeInitialisationFunction import GateTreeHelper
from Classes.GObjectCreator import GObjectCreator

from Classes.RepeaterParameterBuilder import RepeaterParameterBuilder


class TestYamlFunction():

    @staticmethod
    def helper_CheckEquivalentGateObject(gateObjectOld : GOOld, gateObjectNew : GONew):
        assert gateObjectOld.name == gateObjectNew.name
        assert gateObjectOld.path == gateObjectNew.path
        
        paramIndexOld = 0
        paramIndexNew = 0
        while paramIndexNew < len(gateObjectNew.param):
            pOld : GPOld = gateObjectOld.parameters[paramIndexOld]
            pNew : GPNew = gateObjectNew.param[paramIndexNew]
        
            # In the older architecture, the label are not initialised in the static data.
            if pNew.input_type_list == "label" or pOld.input_type_list == ["Label"]:
                if pNew.input_type_list == "label":
                    paramIndexNew += 1
                if pOld.input_type_list in (["Label"], []):
                    paramIndexOld += 1
                continue
        
            # We don't evaluate the Material param since it is different
            if pNew.displayed_label == "Material":
                paramIndexNew += 1
                paramIndexOld += 1
                continue
        
            assert pOld.path == pNew.path
            assert pOld.displayed_name == pNew.displayed_label
        
            # There are some changes between the old and new format
            match pNew.input_type_list:
                case "text":
                    # First, I removed the type list to just a single type to ease the process.
                    assert pOld.input_type_list[0] == "TextArea"
                    assert pOld.default_value_list == pNew.default_value_list
                    if pNew.unit_list == []:
                        assert pOld.unit_list in (None, ["exclude", "include"])
                        assert pOld.default_unit in (None, "exclude")
                        assert pNew.default_unit_index == None
                    else:
                        assert pOld.unit_list == pNew.unit_list
                        assert pOld.default_unit == pNew.unit_list[pNew.default_unit_index]
        
                case "dropdown":
                    assert pOld.value_list[0] == pNew.unit_list
                    if type(pOld.default_value_list[0]) == int:
                        pOld.value_list[0][pOld.default_value_list[0]] == pNew.default_value_list
                    else:
                        pOld.default_value_list == pNew.default_value_list
        
                case "checkbox":
                    assert bool(pOld.default_value_list[0]) == bool(pNew.default_value_list[0])
        
                case "select":
                    assert pOld.default_value_list == pNew.default_value_list
        
        
            paramIndexOld += 1
            paramIndexNew += 1

    @pytest.mark.parametrize("type_input", [
        ("box"),
        ("sphere"),
        ("cylinder"),
        ("cone"),
        ("ellipsoid"),
        ("elliptical tube"),
        ("hexagon"),
        ("wedge"),
        ("tet-mesh-box")
    ])
    @pytest.mark.parametrize("repeater_type", [
        (" - "),
        ("linear"),
        ("ring"),
        ("cubicArray"),
        ("quadrant"),
        ("sphere"),
        ("genericRepeater")
    ])
    def test_VolumeCreation(self, type_input, repeater_type):
        gateTreeHelper = GateTreeHelper()
        gObjectCreator = GObjectCreator()

        name = "objectTest"
        material = ["material"]

        gOld = gObjectCreator.create_world_daughter(name, type_input, material)
        gOld.parameters += gObjectCreator.build_repeater(name, repeater_type)
        gNew = gateTreeHelper.createVolume(name, type_input, material, repeater_type)

        self.helper_CheckEquivalentGateObject(gOld, gNew)
        
    def test_PhysicsCreate(self):
        material_db = []
        
        gObjectCreator = GObjectCreator()
        gTreeHelper = GateTreeHelper()
        gate_root = gObjectCreator.create_gate_root()
        gate_root = gObjectCreator.create_static_objects(gate_root, material_db)
        for child in gate_root.get_daughters():
            if child.name == "physics":
                gOld = child
                break
        gNew = gTreeHelper.createPhysics()

        self.helper_CheckEquivalentGateObject(gOld, gNew)

    def test_SourceCreate(self):
        material_db = []
        
        gObjectCreator = GObjectCreator()
        gTreeHelper = GateTreeHelper()
        gate_root = gObjectCreator.create_gate_root()
        gate_root = gObjectCreator.create_static_objects(gate_root, material_db)
        for child in gate_root.get_daughters():
            if child.name == "source":
                gOld = child
                break
        gNew = gTreeHelper.createSource()
        
        self.helper_CheckEquivalentGateObject(gOld, gNew)

    def test_OutputCreate(self):
        material_db = []
    
        gObjectCreator = GObjectCreator()
        gTreeHelper = GateTreeHelper()
        gate_root = gObjectCreator.create_gate_root()
        gate_root = gObjectCreator.create_static_objects(gate_root, material_db)
        for child in gate_root.get_daughters():
            if child.name == "output":
                gOld = child
                break
        gNew = gTreeHelper.createOutput()
    
        self.helper_CheckEquivalentGateObject(gOld, gNew)
    
    def test_AcquisitionCreate(self):
        material_db = []

        gObjectCreator = GObjectCreator()
        gTreeHelper = GateTreeHelper()
        gate_root = gObjectCreator.create_gate_root()
        gate_root = gObjectCreator.create_static_objects(gate_root, material_db)
        for child in gate_root.get_daughters():
            if child.name == "acquisition":
                gOld = child
                break
        gNew = gTreeHelper.createAcquisition()

        self.helper_CheckEquivalentGateObject(gOld, gNew)

    def test_VisCreate(self):
        material_db = []
        
        gObjectCreator = GObjectCreator()
        gTreeHelper = GateTreeHelper()
        gate_root = gObjectCreator.create_gate_root()
        gate_root = gObjectCreator.create_static_objects(gate_root, material_db)
        for child in gate_root.get_daughters():
            if child.name == "vis":
                gOld = child
                break
        gNew = gTreeHelper.createVis()
        
        self.helper_CheckEquivalentGateObject(gOld, gNew)

        
    





