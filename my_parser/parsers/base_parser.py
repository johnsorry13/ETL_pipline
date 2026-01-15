from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def fetch(self):
        pass

    @abstractmethod
    def parse(self):
        pass

    @abstractmethod
    def collect(self):
        pass

    def save_to_excel(self):
        pass
