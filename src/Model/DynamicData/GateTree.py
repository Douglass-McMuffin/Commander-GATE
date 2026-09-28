"""
The GateTree represent the tree structure of the GATE simulation.
The main purpose of this class is to provide a convenient way to access the GATE simulation data and to perform various operations on it.
"""
from GateObject import GateObject
from GateParameter import GateParameter


class GateTree():

    def __init__(self):
        self.root: GateObject = GateObject("Gate")
        self.children: list[GateObject] = []

        # Initialise the fondamental GateObject
        self.verbosity: list[GateParameter] = 
