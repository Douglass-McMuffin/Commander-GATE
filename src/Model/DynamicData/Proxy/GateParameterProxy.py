from src.Model.DynamicData.Interface.GateParameterInterface import GateParameterInterface
from sys import stderr

class GateParameterProxy():
    """Implementation of the GateParameterInterface that only give read acces to itself."""

    def __init__(self, gateParameter: GateParameterInterface):
        self._gateParameter = gateParameter

        ### GateParameterInterface Implementation
    @property
    def path(self) -> str:
        return self._gateParameter.path

    @property
    def displayedLabel(self) -> str:
        return self._gateParameter.displayedLabel

    @property
    def inputType(self) -> str:
        return self._gateParameter.inputType

    @property
    def defaultValueList(self) -> list[str] | list[float]:
        return self._gateParameter.defaultValueList

    @property
    def valueList(self) -> list[str] | list[float]:
        return self._gateParameter.valueList

    @property
    def unitList(self) -> list[str]:
        return self._gateParameter.unitList

    @property
    def defaultUnitIndex(self) -> int:
        return self._gateParameter.defaultUnitIndex

    @path.setter
    def path(self, path: str):
        print(f"\033[33mCannot change path attribute of {str(self)} since it is a proxy.\033[0m", file=stderr)

    @displayedLabel.setter
    def displayedLabel(self, displayedLabel: str):
        print(f"\033[33mCannot change displayedLabel attribute of {str(self)} since it is a proxy.\033[0m", file=stderr)

    @inputType.setter
    def inputType(self, inputType: str):
        print(f"\033[33mCannot change inputType attribute of {str(self)} since it is a proxy.\033[0m", file=stderr)

    @defaultValueList.setter
    def defaultValueList(self, defaultValueList: list[str] | list[float]):
        print(f"\033[33mCannot change defaultValueList attribute of {str(self)} since it is a proxy.\033[0m", file=stderr)

    @valueList.setter
    def valueList(self, valueList: list[str] | list[float]):
        print(f"\033[33mCannot change valueList attribute of {str(self)} since it is a proxy.\033[0m", file=stderr)

    @unitList.setter
    def unitList(self, unitList: list[str]):
        print(f"\033[33mCannot change unitList attribute of {str(self)} since it is a proxy.\033[0m", file=stderr)

    @defaultUnitIndex.setter
    def defaultUnitIndex(self, defaultUnitIndex: int):
        print(f"\033[33mCannot change defaultUnitIndex attribute of {str(self)} since it is a proxy.\033[0m", file=stderr)