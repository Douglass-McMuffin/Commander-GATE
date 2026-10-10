from abc import ABC, abstractmethod
from src.Model.DynamicData.Interface.GateObjectInterface import GateObjectInterface

class ModelIteratorInterface(ABC):

    @abstractmethod
    def getNext(self) -> GateObjectInterface:
        """Get the next item in the collection"""
        pass 

    @abstractmethod
    def hasMore(self) -> bool:
        """Return True if there is more item to go through the collection"""
        pass