from abc import ABC, abstractmethod

class GateObjectInterface(ABC):


    ### Properties ###
    @property
    @abstractmethod
    def path(self):
        pass
    
    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def parent(self):
        pass  

    @property
    @abstractmethod
    def param(self):
        pass

    @property
    @abstractmethod
    def children(self):
        pass

    ### Methods ###
    def addChild(self, child: GateObjectInterface):
        child.parent = self
        self.children[child.name] = child