from abc import ABC, abstractmethod

class BaseParser(ABC):

    @abstractmethod
    def fetch(self, url: str):
        pass

    @abstractmethod
    def parse(self, html, url) -> dict:
        pass

    @abstractmethod
    def collect(self):
        pass

    def save_to_excel(self):
        pass
