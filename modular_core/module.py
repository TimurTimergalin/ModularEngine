from abc import ABC, abstractmethod


class FunctionalModule(ABC):
    @abstractmethod
    def start(self, obj):
        pass

    @abstractmethod
    def run(self, obj, events):
        pass


class CosmeticModule(ABC):
    @abstractmethod
    def run(self, surf):
        pass
