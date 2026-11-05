from src.Model.DynamicData.Concreate.GateTree import GateTree
from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface

import numpy as np
from scipy.spatial.transform import Rotation

class ExportOpenGate10():

    @staticmethod
    def export(filePath: str):
        gateTree = GateTree()

        file = open(filePath, "w")

        # Setup the file
        file.write(
        """import opengate as gate
        import numpy as np
        from scipy.spatial.transform import Rotation
        
        if __name__ == "__main__":
            sim = gate.Simulation()
            """)


    @staticmethod
    def _addVolume(gateObject: GateObjectInterface) -> str:
        result = ""

        match gateObject.param["Shape of the Volume"]:
            case "box":
                result += f"volume = gate.geometry.volumes.BoxVolume(name=\"{gateObject.name}\")\n"
            case "hexagon":
                result += f"volume = gate.geometry.volumes.HexagonVolume(name=\"{gateObject.name}\")\n"
            case "cone":
                result += f"volume = gate.geometry.volumes.ConsVolume(name=\"{gateObject.name}\")\n"
            # TODO : Find what is the closest to a polyhedra
            case "polyhedra":
                pass
            case "sphere":
                result += f"volume = gate.geometry.volumes.SphereVolume(name=\"{gateObject.name}\")\n"
            case "cylinder":
                result += f"volume = gate.geometry.volumes.TubsVolume(name=\"{gateObject.name}\")\n"
            case "tet-mesh-box":
                result += f"volume = gate.geometry.volumes.TesselatedVolume(name=\"{gateObject.name}\")\n"
        result += f"sim.add_volume(volume)\n"
        
        # TODO : Check what happens for the world volume object
        if gateObject.parent.name != "gate":
            result += f"volume.mother = {gateObject.parent.name}\n"

        
        match gateObject.param["Shape of the Volume"]:
            case "box":
                result += ExportOpenGate10._addTextInput("volume.size[0]", gateObject, "X Lenght")
                result += ExportOpenGate10._addTextInput("volume.size[1]", gateObject, "Y Lenght")
                result += ExportOpenGate10._addTextInput("volume.size[2]", gateObject, "Z Lenght")
            case "hexagon":
                result += ExportOpenGate10._addTextInput("volume.heigth", gateObject, "Height")
                result += ExportOpenGate10._addTextInput("volume.radius", gateObject, "Radius")
            case "cone":
                result += ExportOpenGate10._addTextInput("volume.rmax1", gateObject, "Eternal Radius 1")
                result += ExportOpenGate10._addTextInput("volume.rmax2", gateObject, "Eternal Radius 2")
                result += ExportOpenGate10._addTextInput("volume.rmin1", gateObject, "Internal Radius 1")
                result += ExportOpenGate10._addTextInput("volume.rmin2", gateObject, "Internal Radius 2")
                result += ExportOpenGate10._addTextInput("volume.sphi", gateObject, "Start Phi Angle")
                result += ExportOpenGate10._addTextInput("volume.dphi", gateObject, "Phi Angular Span")
                result += f"volume.dz = {gateObject.param["Heigth"].valueList[0] * 2} * gate.g4_units.{gateObject.param["Heigth"].unitList[gateObject.param["Heigth"].defaultUnitIndex]}\n"

            # TODO : Find what is the closest shape to a polyhedra
            case "polyhedra":
                pass
            case "sphere":
                result += ExportOpenGate10._addTextInput("volume.rmin", gateObject, "Internal Radius")
                result += ExportOpenGate10._addTextInput("volume.rmax", gateObject, "External Radius")
                result += ExportOpenGate10._addTextInput("volume.sphi", gateObject, "Start Phi Angle")
                result += ExportOpenGate10._addTextInput("volume.dphi", gateObject, "Phi Angular Span")
                result += ExportOpenGate10._addTextInput("volume.stheta", gateObject, "Start Theta Angle")
                result += ExportOpenGate10._addTextInput("volume.dtheta", gateObject, "Theta Angular Span")

            case "cylinder":
                result += ExportOpenGate10._addTextInput("volume.rmin", gateObject, "Internal Radius")
                result += ExportOpenGate10._addTextInput("volume.rmax", gateObject, "External Radius")
                result += f"volume.dz = {gateObject.param["Heigth"].valueList[0] * 2} * gate.g4_units.{gateObject.param["Heigth"].unitList[gateObject.param["Heigth"].defaultUnitIndex]}\n"
                result += ExportOpenGate10._addTextInput("volume.sphi", gateObject, "Start Phi Angle")
                result += ExportOpenGate10._addTextInput("volume.dphi", gateObject, "Phi Angular Span")

            case "tet-mesh-box":
                result += ExportOpenGate10._addSelectInput("volume.file_name", gateObject, "Path to .ele File")
                result += ExportOpenGate10._addDropdownInput("volume.size_units", gateObject, "Unit of Length")

        ### Add Material
        result += ExportOpenGate10._addDropdownInput("volume.material", gateObject, "Set Material")

        ### Add Placement parameters
        result += ExportOpenGate10._addTextInput("volume.translation[0]", gateObject, "Set Translation")

        match gateObject.param["Rotation Axis"].valueList[0]:
            case "X":
                axis = [1, 0, 0]
                result += f"volume.rotation = [Rotation.from_rotvec({gateObject.param["Rotation Angle"].valueList[0]} * gate.g4_units.{gateObject.param["Rotation Angle"].unitList[gateObject.param["Rotation Angle"].defaultUnitIndex]} * axis).as_matrix()]\n"
            case "Y":
                axis = [0, 1, 0]
                result += f"volume.rotation = [Rotation.from_rotvec({gateObject.param["Rotation Angle"].valueList[0]} * gate.g4_units.{gateObject.param["Rotation Angle"].unitList[gateObject.param["Rotation Angle"].defaultUnitIndex]} * axis).as_matrix()]\n"
            case "Z":
                axis = [0, 0, 1]
                result += f"volume.rotation = [Rotation.from_rotvec({gateObject.param["Rotation Angle"].valueList[0]} * gate.g4_units.{gateObject.param["Rotation Angle"].unitList[gateObject.param["Rotation Angle"].defaultUnitIndex]} * axis).as_matrix()]\n"

        result += ExportOpenGate10._addTextInput("volume.translation[0]", gateObject, "Set Translation")

        ### Add Visual Effects
        result += ExportOpenGate10._addDropdownInput("volume.color", gateObject, "Color")
        if gateObject.param["Line Style"].valueList[0] != "unbroken":
            result += "volume.style = \"wireframe\"\n"


    @staticmethod
    def _addTextInput(variable: str, gateObject: GateObjectInterface, parameterLabel: str):
        return f"{variable} = {gateObject.param[parameterLabel].valueList[0]} * gate.g4_units.{gateObject.param[parameterLabel].unitList[gateObject.param["X Length"].defaultUnitIndex]}\n"

    @staticmethod
    def _addSelectInput(variable: str, gateObject: GateObjectInterface, parameterLabel: str):
        return f"{variable} = {gateObject.param[parameterLabel].valueList[0]}"

    @staticmethod
    def _addDropdownInput(variable: str, gateObject: GateObjectInterface, parameterLabel: str):
        return f"{variable} = {gateObject.param[parameterLabel].valueList[0]}"
