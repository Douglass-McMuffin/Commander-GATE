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
        """\"\"\"This opengate 10 python configuration is generated via the Commander-GATE Interface.\"\"\"
        
        import opengate as gate
        import numpy as np
        from scipy.spatial.transform import Rotation
        
        if __name__ == "__main__":
            sim = gate.Simulation()
        """)
        tabulation = "    "

        ### Generate all the volumes
        volumeToSee = [gateTree.getObjectFromGateObjectPath(gateTree, gateTree._getYamlData("gate/object_path/WORLD/object_path"))]
        
        while len(volumeToSee) > 0:
            volume = volumeToSee.pop(0)
            volumeToSee += list(volume.children.values())

            file.write(f"{tabulation}### GENERATING VOLUME {volume.name} ###\n\n")
            file.write(ExportOpenGate10._addVolume(volume, tabulation))
            file.write(f"\n{tabulation}### FINISHED GENERATING VOLUME {volume.name} ###\n")

        ### Setup the physics
        physicsObject = gateTree.getObjectFromGateObjectPath(gateTree, gateTree._getYamlData("gate/object_path/PHYSICS/object_path"))
        physicsName = physicsObject.param["Physics List"].valueList[0]
        if physicsName == " - ":
            physicsName = "FTFP_BERT"
        file.write(f"{tabulation}### GENERATING PHYSICS CONFIGURATION ###\n\n")
        file.write(f"{tabulation}sim.physics_manager.physics_list_name = \"{physicsName}\"\n")
        file.write(f"\n{tabulation}### FINISHED GENERATING PHYSICS CONFIGURATION ###\n")

        ### Setup the sources
        sourceToSee = list(gateTree.getObjectFromGateObjectPath(gateTree, gateTree._getYamlData("gate/object_path/SOURCE/object_path")).children.values())
        
        while len(sourceToSee) > 0:
            source = sourceToSee.pop(0)
        
            file.write(f"{tabulation}### GENERATING SOURCE {source.name} ###\n\n")
            file.write(ExportOpenGate10._addSource(source, tabulation))
            file.write(f"\n{tabulation}### FINISHED GENERATING SOURCE {source.name} ###\n")

        ### Setup the actors



        

        




    @staticmethod
    def _addVolume(gateObject: GateObjectInterface, tab: str) -> str:
        result = ""
        volumeVariable = f"{tab}volume_{gateObject.name}"

        match gateObject.param["Shape of the Volume"]:
            case "box":
                result += f"{volumeVariable} = gate.geometry.volumes.BoxVolume(name=\"{gateObject.name}\")\n"
            case "hexagon":
                result += f"{volumeVariable} = gate.geometry.volumes.HexagonVolume(name=\"{gateObject.name}\")\n"
            case "cone":
                result += f"{volumeVariable} = gate.geometry.volumes.ConsVolume(name=\"{gateObject.name}\")\n"
            # TODO : Find what is the closest to a polyhedra
            case "polyhedra":
                pass
            case "sphere":
                result += f"{volumeVariable} = gate.geometry.volumes.SphereVolume(name=\"{gateObject.name}\")\n"
            case "cylinder":
                result += f"{volumeVariable} = gate.geometry.volumes.TubsVolume(name=\"{gateObject.name}\")\n"
            case "tet-mesh-box":
                result += f"{volumeVariable} = gate.geometry.volumes.TesselatedVolume(name=\"{gateObject.name}\")\n"
        result += f"sim.add_volume(volume)\n"
        
        # TODO : Check what happens for the world volume object
        if gateObject.parent.name != "gate":
            result += f"{volumeVariable}.mother = {gateObject.parent.name}\n"

        
        match gateObject.param["Shape of the Volume"]:
            case "box":
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.size[0]", gateObject, "X Lenght")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.size[1]", gateObject, "Y Lenght")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.size[2]", gateObject, "Z Lenght")
            case "hexagon":
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.heigth", gateObject, "Height")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.radius", gateObject, "Radius")
            case "cone":
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.rmax1", gateObject, "Eternal Radius 1")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.rmax2", gateObject, "Eternal Radius 2")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.rmin1", gateObject, "Internal Radius 1")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.rmin2", gateObject, "Internal Radius 2")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.sphi", gateObject, "Start Phi Angle")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.dphi", gateObject, "Phi Angular Span")
                result += f"{volumeVariable}.dz = {gateObject.param["Heigth"].valueList[0]} * gate.g4_units.{gateObject.param["Heigth"].unitList[gateObject.param["Heigth"].defaultUnitIndex]} / 2.0\n"

            # TODO : Find what is the closest shape to a polyhedra
            case "polyhedra":
                pass
            case "sphere":
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.rmin", gateObject, "Internal Radius")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.rmax", gateObject, "External Radius")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.sphi", gateObject, "Start Phi Angle")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.dphi", gateObject, "Phi Angular Span")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.stheta", gateObject, "Start Theta Angle")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.dtheta", gateObject, "Theta Angular Span")

            case "cylinder":
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.rmin", gateObject, "Internal Radius")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.rmax", gateObject, "External Radius")
                result += f"{volumeVariable}.dz = {gateObject.param["Heigth"].valueList[0] * 2} * gate.g4_units.{gateObject.param["Heigth"].unitList[gateObject.param["Heigth"].defaultUnitIndex]}\n"
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.sphi", gateObject, "Start Phi Angle")
                result += ExportOpenGate10._addTextInput(f"{volumeVariable}.dphi", gateObject, "Phi Angular Span")

            case "tet-mesh-box":
                result += ExportOpenGate10._addSelectInput(f"{volumeVariable}.file_name", gateObject, "Path to .ele File")
                result += ExportOpenGate10._addDropdownInput(f"{volumeVariable}.size_units", gateObject, "Unit of Length")

        ### Add Material
        result += ExportOpenGate10._addDropdownInput(f"{volumeVariable}.material", gateObject, "Set Material")

        ### Add Placement parameters
        result += ExportOpenGate10._addTextInput(f"{volumeVariable}.translation[0]", gateObject, "Set Translation")

        match gateObject.param["Rotation Axis"].valueList[0]:
            case "X":
                axis = [1, 0, 0]
                result += f"{volumeVariable}.rotation = [Rotation.from_rotvec({gateObject.param["Rotation Angle"].valueList[0]} * gate.g4_units.{gateObject.param["Rotation Angle"].unitList[gateObject.param["Rotation Angle"].defaultUnitIndex]} * axis).as_matrix()]\n"
            case "Y":
                axis = [0, 1, 0]
                result += f"{volumeVariable}.rotation = [Rotation.from_rotvec({gateObject.param["Rotation Angle"].valueList[0]} * gate.g4_units.{gateObject.param["Rotation Angle"].unitList[gateObject.param["Rotation Angle"].defaultUnitIndex]} * axis).as_matrix()]\n"
            case "Z":
                axis = [0, 0, 1]
                result += f"{volumeVariable}.rotation = [Rotation.from_rotvec({gateObject.param["Rotation Angle"].valueList[0]} * gate.g4_units.{gateObject.param["Rotation Angle"].unitList[gateObject.param["Rotation Angle"].defaultUnitIndex]} * axis).as_matrix()]\n"

        result += ExportOpenGate10._addTextInput(f"{volumeVariable}.translation[0]", gateObject, "Set Translation")

        ### Add Visual Effects
        result += ExportOpenGate10._addDropdownInput(f"{volumeVariable}.color", gateObject, "Color")
        if gateObject.param["Line Style"].valueList[0] != "unbroken":
            result += "volume.style = \"wireframe\"\n"


    @staticmethod
    def _addSource(gateObject: GateObjectInterface, tab: str) -> str:
        result = ""
        sourceVariable = f"{tab}source_{gateObject.name}"
        sourceTranslation = {
            "gps": "GenericSource",
            "pencil_beam": "IonPencilBeamSource",
            "tps_pencil_beam": "TreatmentPlanPBSource",
            "fast_i124": "fastI124", # Check if the source is really that
            "fast_y90": "fastY90",
            "extended": "PositroniumSource"
        }
        sourceType = sourceTranslation[gateObject.param["Source Type"].valueList[0]]
        volumeAttached = gateObject.param["Attach to volume"].valueList[0]

        result += f"{sourceVariable} = sim.add_source(\"{sourceType}\", \"{gateObject.name}\")\n"

        match sourceType:
            case "GenericSource":
                result += ExportOpenGate10._addTextInput(f"{sourceVariable}.activity", gateObject, "Activity")
                result += f"{sourceVariable}.attached_to = \"{volumeAttached}\"\n"
                particle = gateObject.param["Particle"].valueList[0]
                if particle == "user defined":
                    result += f"{sourceVariable}.particle = \"ion {gateObject.param["User Defined Ion(Z,A,Q,E_keV)"].valueList[0]} {gateObject.param["User Defined Ion(Z,A,Q,E_keV)"].valueList[1]}\"\n"
                else:
                    result += f"{sourceVariable}.particle = \"{particle}\"\n"
                
                match gateObject.param["Domain"].valueList[0]:
                    case "Point" | "Beam":
                        # Treat the shape as if it is a point
                        result += f"{sourceVariable}.position.type = \"point\"\n"
                    case "Surface" | "Volume":
                        match gateObject.param["Shape"].valueList[0]:
                            case "Sphere" | "Ellipsoid":
                                # Treat the shape as if it is a sphere
                                result += f"{sourceVariable}.position.type = \"sphere\"\n"
                                result += ExportOpenGate10._addTextInput(f"{sourceVariable}.position.radius", gateObject, "Radius")
                                
                            case "Cylinder":
                                # Treat the shape as if it is a cylinder
                                result += f"{sourceVariable}.position.type = \"cylinder\"\n"
                                result += ExportOpenGate10._addTextInput(f"{sourceVariable}.position.radius", gateObject, "Radius")
                                result += ExportOpenGate10._addTextInput(f"{sourceVariable}.position.dz", gateObject, "Half z")
                                
                            case "Para":
                                # Treat the shape as if it is a box
                                result += f"{sourceVariable}.position.type = \"box\"\n"
                                result += f"{sourceVariable}.position.size[0] = {gateObject.param["Half x"].valueList[0]} * gate.g4_units.{gateObject.param["Half x"].unitList[gateObject.param["Half x"].defaultUnitIndex]} * 2.0\n"
                                result += f"{sourceVariable}.position.size[1] = {gateObject.param["Half y"].valueList[0]} * gate.g4_units.{gateObject.param["Half y"].unitList[gateObject.param["Half y"].defaultUnitIndex]} * 2.0\n"
                                result += f"{sourceVariable}.position.size[2] = {gateObject.param["Half z"].valueList[0]} * gate.g4_units.{gateObject.param["Half z"].unitList[gateObject.param["Half z"].defaultUnitIndex]} * 2.0\n"

                    case "Plane":
                        match gateObject.param["Shape"].valueList[0]:
                            case "Circle", "Annulus", "Ellipsoid":
                                # Treat the shape as if it is a disc
                                result += f"{sourceVariable}.position.type = \"cylinder\"\n"
                                result += ExportOpenGate10._addTextInput(f"{sourceVariable}.position.radius", gateObject, "Radius")
                            case _:
                                # Treat the shape as if it is a point
                                result += f"{sourceVariable}.position.type = \"point\"\n"

                result += f"{sourceVariable}.position.translation[0] = {gateObject.param["Position (x,y,z)"].valueList[0]} * gate.g4_units.{gateObject.param["Position (x,y,z)"].unitList[gateObject.param["Position (x,y,z)"].defaultUnitIndex]}\n"
                result += f"{sourceVariable}.position.translation[1] = {gateObject.param["Position (x,y,z)"].valueList[1]} * gate.g4_units.{gateObject.param["Position (x,y,z)"].unitList[gateObject.param["Position (x,y,z)"].defaultUnitIndex]}\n"
                result += f"{sourceVariable}.position.translation[2] = {gateObject.param["Position (x,y,z)"].valueList[2]} * gate.g4_units.{gateObject.param["Position (x,y,z)"].unitList[gateObject.param["Position (x,y,z)"].defaultUnitIndex]}\n"
                
                # Particle initial direction
                match gateObject.param["Angular type"].valueList[0]:
                    case "iso":
                        result += f"{sourceVariable}.direction.type = \"iso\"\n"
                        result += ExportOpenGate10._addTextInput(f"{sourceVariable}.direction.theta[0]", gateObject, "Min theta")
                        result += ExportOpenGate10._addTextInput(f"{sourceVariable}.direction.theta[1]", gateObject, "Max theta")
                        result += ExportOpenGate10._addTextInput(f"{sourceVariable}.direction.phi[0]", gateObject, "Min phi")
                        result += ExportOpenGate10._addTextInput(f"{sourceVariable}.direction.phi[1]", gateObject, "Max phi")

                result += ExportOpenGate10._addTextInput(f"{sourceVariable}.half_life", gateObject, "Half-life")

                # Energy Definition
                match gateObject.param["Energy distribution"].valueList[0]:
                    case "Mono":
                        result += f"{sourceVariable}.energy.type = \"mono\"\n"
                        result += ExportOpenGate10._addTextInput(f"{sourceVariable}.energy.mono", gateObject, "Mono energy")

                        


            case "IonPencilBeamSource":
                result += f"{sourceVariable}.energy.type = \"mono\"\n"
                result += ExportOpenGate10._addTextInput(f"{sourceVariable}.energy.mono", gateObject, "Mean Energy")

                particle = gateObject.param["Particle"].valueList[0]
                if particle == "user defined":
                    result += f"{sourceVariable}.particle = \"ion {gateObject.param["User Defined Ion(Z,A,Q,E_keV)"].valueList[0]} {gateObject.param["User Defined Ion(Z,A,Q,E_keV)"].valueList[1]}\"\n"
                else:
                    result += f"{sourceVariable}.particle = \"{particle}\"\n"

                result += f"{sourceVariable}.position.translation[0] = {gateObject.param["Centre (x,y,z)"].valueList[0]} * gate.g4_units.{gateObject.param["Centre (x,y,z)"].unitList[gateObject.param["Centre (x,y,z)"].defaultUnitIndex]}\n"
                result += f"{sourceVariable}.position.translation[1] = {gateObject.param["Centre (x,y,z)"].valueList[1]} * gate.g4_units.{gateObject.param["Centre (x,y,z)"].unitList[gateObject.param["Centre (x,y,z)"].defaultUnitIndex]}\n"
                result += f"{sourceVariable}.position.translation[2] = {gateObject.param["Centre (x,y,z)"].valueList[2]} * gate.g4_units.{gateObject.param["Centre (x,y,z)"].unitList[gateObject.param["Centre (x,y,z)"].defaultUnitIndex]}\n"

                result += ExportOpenGate10._addTextInput(f"{sourceVariable}.number_of_primaries", gateObject, "Total Number of Primaries")

                result += ExportOpenGate10._addTextInput(f"{sourceVariable}.direction.partPhSp_x[0]", gateObject, "Sigma X")
                result += ExportOpenGate10._addTextInput(f"{sourceVariable}.direction.partPhSp_x[1]", gateObject, "Sigma Theta")
                result += f"{sourceVariable}.direction.partPhSp_x[2] = {gateObject.param["Emittance X-Theta (mm*mrad)"].valueList[0]} * gate.g4_units.mm * gate.g4_units.mrad\n"
                #result += ExportOpenGate10._addTextInput(f"{sourceVariable}.direction.partPhSp_x[3]", gateObject, "Sigma ")
                result += ExportOpenGate10._addTextInput(f"{sourceVariable}.direction.partPhSp_y[0]", gateObject, "Sigma Y")
                result += ExportOpenGate10._addTextInput(f"{sourceVariable}.direction.partPhSp_y[1]", gateObject, "Sigma Phi")
                result += f"{sourceVariable}.direction.partPhSp_y[2] = {gateObject.param["Emittance Y-Phi (mm*mrad)"].valueList[0]} * gate.g4_units.mm * gate.g4_units.mrad\n"
                #result += ExportOpenGate10._addTextInput(f"{sourceVariable}.direction.partPhSp_y[3]", gateObject, "Sigma X")


            case "TreatmentPlanPBSource":
                pass
            case "fastI124":
                pass
            case "fastY90":
                pass
            case "PositroniumSource":
                pass
    

        
        result += f"{sourceVariable}.visualization.count = {gateObject.param["Visualize (count, px)"].valueList[0]}\n"
        result += f"{sourceVariable}.visualization.size = {gateObject.param["Visualize (count, px)"].valueList[1]}\n"
        result += f"{sourceVariable}.visualization.color = \"{gateObject.param["Visualize (color)"].valueList[0]}\"\n"

    @staticmethod
    def _addDigitizer(gateObject: GateObjectInterface, tab: str) -> str:
        result = ""


    @staticmethod
    def _addTextInput(variable: str, gateObject: GateObjectInterface, parameterLabel: str):
        if gateObject.param[parameterLabel].defaultUnitIndex is None:
            return f"{variable} = {gateObject.param[parameterLabel].valueList[0]}\n"
        else:
            unit = gateObject.param[parameterLabel].unitList[gateObject.param[parameterLabel].defaultUnitIndex]
            return f"{variable} = {gateObject.param[parameterLabel].valueList[0]} * gate.g4_units.{unit}\n"

    @staticmethod
    def _addSelectInput(variable: str, gateObject: GateObjectInterface, parameterLabel: str):
        return f"{variable} = {gateObject.param[parameterLabel].valueList[0]}"

    @staticmethod
    def _addDropdownInput(variable: str, gateObject: GateObjectInterface, parameterLabel: str):
        return f"{variable} = {gateObject.param[parameterLabel].valueList[0]}"
