import pytest
from src.Model.DynamicData.Concreate.GateParameter import GateParameter as GPNew
from Classes.GateParameter import GateParameter as GPOld
from src.Model.DynamicData.Concreate.GateObject import GateObject as GONew
from Classes.GateObject import GateObject as GOOld

from src.Model.DynamicData.Concreate.GateTree import GateTree
from Classes.GObjectCreator import GObjectCreator

class TestCompareOldAndNewArchitecture():

    @staticmethod
    def helper_CheckEquivalentGateObject(gateObjectOld : GOOld, gateObjectNew : GONew):
        assert gateObjectOld.name == gateObjectNew.name
        #assert gateObjectOld.path == gateObjectNew.path
        
        paramIndexOld = 0
        paramIndexNew = 0
        while paramIndexOld < len(gateObjectOld.parameters):
            pOld : GPOld = gateObjectOld.parameters[paramIndexOld]
            pNew : GPNew = gateObjectNew.param[paramIndexNew]
        
            # In the older architecture, the label are not initialised in the static data.
            if pNew.inputTypeList == "label" or pOld.input_type_list == ["Label"]:
                if pNew.inputTypeList == "label":
                    paramIndexNew += 1
                if pOld.input_type_list in (["Label"], []):
                    paramIndexOld += 1
                continue
        
            # We don't evaluate the Material param since it is different
            if pNew.displayedLabel == "Set Material":
                paramIndexNew += 1
                paramIndexOld += 1
                continue
        
            assert pOld.path == pNew.path
            assert pOld.displayed_name == pNew.displayedLabel
        
            # There are some changes between the old and new format
            match pNew.inputTypeList:
                case "text":
                    # First, I removed the type list to just a single type to ease the process.
                    assert pOld.input_type_list[0] == "TextArea"
                    assert pOld.default_value_list == pNew.defaultValueList
                    if pNew.unitList == []:
                        assert pOld.unit_list in (None, ["exclude", "include"])
                        assert pOld.default_unit in (None, "exclude")
                        assert pNew.defaultUnitIndex == None
                    else:
                        assert pOld.unit_list == pNew.unitList
                        assert pOld.default_unit == pNew.unitList[pNew.defaultUnitIndex]
        
                case "dropdown":
                    assert pOld.value_list[0] == pNew.unitList
                    if type(pOld.default_value_list[0]) == int:
                        pOld.value_list[0][pOld.default_value_list[0]] == pNew.defaultValueList
                    else:
                        pOld.default_value_list == pNew.defaultValueList
        
                case "checkbox":
                    assert bool(pOld.default_value_list[0]) == bool(pNew.defaultValueList[0])
        
                case "select":
                    assert pOld.default_value_list == pNew.defaultValueList
        
        
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
        gateTree = GateTree()
        gateTree.setup("MaterialDB/AF_GateMaterials.db")
        gObjectCreator = GObjectCreator()

        name = "objectTest"
        material = ["material"]

        gOld = gObjectCreator.create_world_daughter(name, type_input, material)
        gOld.parameters += gObjectCreator.build_repeater(name, repeater_type)
        gNew = gateTree.createVolume(name, type_input, material, repeater_type)

        self.helper_CheckEquivalentGateObject(gOld, gNew)
        
    def test_PhysicsCreate(self):
        material_db = []
        
        gObjectCreator = GObjectCreator()
        gateTree = GateTree()
        gateTree.setup("MaterialDB/AF_GateMaterials.db")
        gate_root = gObjectCreator.create_gate_root()
        gate_root = gObjectCreator.create_static_objects(gate_root, material_db)
        for child in gate_root.get_daughters():
            if child.name == "physics":
                gOld = child
                break
        gNew = gateTree["gate"]["physics"]

        self.helper_CheckEquivalentGateObject(gOld, gNew)

    def test_SourceCreate(self):
        material_db = []
        
        gObjectCreator = GObjectCreator()
        gateTree = GateTree()
        gateTree.setup("MaterialDB/AF_GateMaterials.db")
        gate_root = gObjectCreator.create_gate_root()
        gate_root = gObjectCreator.create_static_objects(gate_root, material_db)
        for child in gate_root.get_daughters():
            if child.name == "source":
                gOld = child
                break
        gNew = gateTree["gate"]["source"]
        
        self.helper_CheckEquivalentGateObject(gOld, gNew)

    def test_OutputCreate(self):
        material_db = []
    
        gObjectCreator = GObjectCreator()
        gateTree = GateTree()
        gateTree.setup("MaterialDB/AF_GateMaterials.db")
        gate_root = gObjectCreator.create_gate_root()
        gate_root = gObjectCreator.create_static_objects(gate_root, material_db)
        for child in gate_root.get_daughters():
            if child.name == "output":
                gOld = child
                break
        gNew = gateTree["gate"]["output"]
    
        self.helper_CheckEquivalentGateObject(gOld, gNew)
    
    def test_AcquisitionCreate(self):
        material_db = []

        gObjectCreator = GObjectCreator()
        gateTree = GateTree()
        gateTree.setup("MaterialDB/AF_GateMaterials.db")
        gate_root = gObjectCreator.create_gate_root()
        gate_root = gObjectCreator.create_static_objects(gate_root, material_db)
        for child in gate_root.get_daughters():
            if child.name == "acquisition":
                gOld = child
                break
        gNew = gateTree["gate"]["acquisition"]

        self.helper_CheckEquivalentGateObject(gOld, gNew)

    def test_VisCreate(self):
        material_db = []
        
        gObjectCreator = GObjectCreator()
        gateTree = GateTree()
        gateTree.setup("MaterialDB/AF_GateMaterials.db")
        gate_root = gObjectCreator.create_gate_root()
        gate_root = gObjectCreator.create_static_objects(gate_root, material_db)
        for child in gate_root.get_daughters():
            if child.name == "vis":
                gOld = child
                break
        gNew = gateTree["vis"]
        
        self.helper_CheckEquivalentGateObject(gOld, gNew)

        
    





