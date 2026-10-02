import pytest
from src.Model.DynamicData.GateParameter import GateParameter as GPNew
from Classes.GateParameter import GateParameter as GPOld
from src.Model.DynamicData.GateObject import GateObject as GONew
from Classes.GateObject import GateObject as GOOld

from src.Model.DynamicData.GateTree import GateTree
from Classes.GObjectCreator import GObjectCreator

class TestNewArchitecture():

    def test_GateTreeInit(self):
        gateTree = GateTree()
        gateTree.setup("MaterialDB/AF_GateMaterials.db")
        print(gateTree)        
        print("done")

    def test_dynamicDropdownWithUpdatedField_change(self):
        gateTree = GateTree()
        gateTree.setup("MaterialDB/AF_GateMaterials.db")

        assert gateTree["gate"]["systems"].getParameter("Systems Structure Type").value_list[0] == "scanner"
        assert gateTree["gate"]["world"].getParameter("Level selection").value_list[0] == "level1"

        gateTree["gate"]["systems"].getParameter("Systems Structure Type").updateField(0, "CPET")

        assert gateTree["gate"]["systems"].getParameter("Systems Structure Type").value_list[0] == "CPET"
        assert gateTree["gate"]["world"].getParameter("Level selection").value_list[0] == "sector"

    def test_dynamicDropdownWithUpdatedField_noChange(self):
        gateTree = GateTree()
        gateTree.setup("MaterialDB/AF_GateMaterials.db")

        assert gateTree["gate"]["systems"].getParameter("Systems Structure Type").value_list[0] == "scanner"
        assert gateTree["gate"]["world"].getParameter("Level selection").value_list[0] == "level1"

        gateTree["gate"]["world"].getParameter("Level selection").updateField(0, "level2")
        gateTree["gate"]["systems"].getParameter("Systems Structure Type").updateField(0, "scanner")

        assert gateTree["gate"]["systems"].getParameter("Systems Structure Type").value_list[0] == "scanner"
        assert gateTree["gate"]["world"].getParameter("Level selection").value_list[0] == "level2"
    