from src.Model.DynamicData.Interface.GateParameterInterface import GateParameterInterface
from sys import stderr

class GateParameterProxy():

    def __init__(self, gateParameter: GateParameterInterface):
        self._gateParameter = gateParameter

        ### GateParameterInterface Implementation
    @property
    def path(self) -> str:
        return self._path

    @property
    def displayedLabel(self) -> str:
        return self._gateParameter.displayedLabel

    @property
    def inputTypeList(self) -> str:
        return self._gateParameter.inputTypeList

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
        print(f"Cannot change path attribute of {str(self)} since it is a proxy.", file=stderr)

    @displayedLabel.setter
    def displayedLabel(self, displayedLabel: str):
        print(f"Cannot change displayedLabel attribute of {str(self)} since it is a proxy.", file=stderr)

    @inputTypeList.setter
    def inputTypeList(self, inputTypeList: str):
        print(f"Cannot change inputTypeList attribute of {str(self)} since it is a proxy.", file=stderr)

    @defaultValueList.setter
    def defaultValueList(self, defaultValueList: list[str] | list[float]):
        print(f"Cannot change defaultValueList attribute of {str(self)} since it is a proxy.", file=stderr)

    @valueList.setter
    def valueList(self, valueList: list[str] | list[float]):
        print(f"Cannot change valueList attribute of {str(self)} since it is a proxy.", file=stderr)

    @unitList.setter
    def unitList(self, unitList: list[str]):
        print(f"Cannot change unitList attribute of {str(self)} since it is a proxy.", file=stderr)

    @defaultUnitIndex.setter
    def defaultUnitIndex(self, defaultUnitIndex: int):
        print(f"Cannot change defaultUnitIndex attribute of {str(self)} since it is a proxy.", file=stderr)