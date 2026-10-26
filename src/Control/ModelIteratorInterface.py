from abc import ABC, abstractmethod
from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface

class ModelIteratorInterface(ABC):

    @abstractmethod
    def getNext(self) -> GateObjectInterface:
        """Get the next gate object of the iterator."""
        pass 

    @abstractmethod
    def hasMore(self) -> bool:
        """Check if there is still gates objects left to iterate."""
        pass