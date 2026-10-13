from abc import ABC, abstractmethod
from src.Model.DynamicData.Concreate.GateParameter import GateParameter

class GateObjectInterface(ABC):


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
    def param(self) -> list[GateParameter]:
        pass

    @property
    @abstractmethod
    def children(self) -> list[GateObjectInterface]:
        pass

    ### Methods ###
    def addChild(self, child: GateObjectInterface):
        child.parent = self
        child.path = self.path + "/" + child.name
        self.children[child.name] = child

    def __getitem__(self, key: str):
        return self.children[key]