from abc import ABCMeta
from src.Model.DynamicData.Concreate.GateParameter import GateParameter
from enum import Enum, EnumMeta

class FrozenEnumMeta(EnumMeta):
    def __setattr__(cls, name, value):
        if name in cls._member_map_:
            raise AttributeError(f"{cls.__name__}.{name} is read-only")
        super().__setattr__(name, value)

class DynamicSignal(Enum, metaclass=FrozenEnumMeta):
    ATTACHED_VOLUME = "ATTACHED_VOLUME"

class SingletonMeta(ABCMeta):
    """Singleton design pattern."""
    _instances = {}
    _lock = None  # Initialize in __new__ or use a lock for thread safety

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class SignalBroker(metaclass=SingletonMeta):

    def setup(self):
        """Setup the broker to handle the publisher and subscriber. For static publisher, the link is made directly into the gate object itself."""
        self.dynamicPublisherDict: dict[str, DynamicSignal] = {} #For each publisher (publisher's path), link it to a signal
        self.dynamicSubscriberDict: dict[DynamicSignal, set[GateParameter]] = {} #For each signal, link it to a set of subscribers to update

    @staticmethod
    def hashParam(parameter: GateParameter):
        """
        return a string that is unique to the parameter

        Args:
            parameter: gate parameter
        """
        return parameter.displayedLabel

    def addDynamicPublisher(self, publisherParameter: GateParameter, signal: DynamicSignal):
        """
        Add a publisher that emit a signal when changed.

        Args:
            publisherObject: gate parameter that is emitting a signal when its value is changed
            signal: signal that is emitted
        """

        self.dynamicPublisherDict[self.hashParam(publisherParameter)] = signal

    def addDynamicSubscriber(self, subscriberParameter: GateParameter, signal: DynamicSignal):
        """
        Add a subscriber to update when a signal emitted.
        
        Args:
            subcriberObject: gate object to updated
            signal: signal that is emitted
        """
        if self.dynamicSubscriberDict.get(signal) is None:
            self.dynamicSubscriberDict[signal] = set()
        self.dynamicSubscriberDict[signal].add(subscriberParameter)

    def emitSignal(self, signal: DynamicSignal):
        subscribers = self.dynamicSubscriberDict.get(signal, [])      
        for subscriber in subscribers:
            subscriber.receiveNotification()

    def emitSignalFromPublisher(self, publisherParameter):
        signal = self.dynamicPublisherDict.get(self.hashParam(publisherParameter), None)
        if signal is None:
            return
        self.emitSignal(signal)

    
