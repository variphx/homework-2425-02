from abc import abstractmethod, ABC


class VectorDb(ABC):
    @abstractmethod
    def __init__(self, location: str = ":memory:"): ...

    @abstractmethod
    def insert(self, values): ...

    @abstractmethod
    def query(self, embeddings): ...
