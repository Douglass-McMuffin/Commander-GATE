from abc import ABC, abstractmethod

class GateParameterInterface(ABC):

    @property
    def path(self) -> str:
        pass

    @property
    def displayedLabel(self) -> str:
        pass

    @property
    def inputTypeList(self) -> str:
        pass

    @property
    def defaultValueList(self) -> list[str] | list[float]:
        pass

    @property
    def valueList(self) -> list[str] | list[float]:
        pass

    @property
    def unitList(self) -> list[str]:
        pass

    @property
    def defaultUnitIndex(self) -> int:
        pass