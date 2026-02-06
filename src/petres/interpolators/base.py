from abc import ABC, abstractmethod
class InterpolatorBase(ABC):
    """
    Maps sparse domain data (e.g. well logs, zone values)
    to a grid or surface.
    """

    @abstractmethod
    def fit(self, data, geometry):
        ...

    @abstractmethod
    def interpolate(self, target):
        ...

    @abstractmethod
    def validate(self):
        ...