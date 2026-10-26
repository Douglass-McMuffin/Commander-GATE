from abc import ABC, abstractmethod


class GateObjectInterface(ABC):
    """Interface to implement the caracteristics of a gate object."""

    ### Properties ###
    @property
    @abstractmethod
    def path(self) -> str:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def parent(self) -> GateObjectInterface:
        pass  

    @property
    @abstractmethod
    def param(self) -> dict[str, GateParameterInterface]:
        pass

    @property
    @abstractmethod
    def children(self) -> dict[str, GateObjectInterface]:
        pass

    ### Abstract Methods ###
    def getObjectFromGateObjectPath(self, gateObjectPath: str) -> GateObjectInterface:
        pass

    ### Methods ###
    def addChild(self, child: GateObjectInterface):
        """
        Add child gate object to itself.

        child -- new gate object child
        """
        child.parent = self
        child.path = self.path + "/" + child.name
        self.children[child.name] = child

    def __getitem__(self, key: str):
        return self.children[key]

from src.Model.DynamicData.Interface.GateParameterInterface import GateParameterInterface