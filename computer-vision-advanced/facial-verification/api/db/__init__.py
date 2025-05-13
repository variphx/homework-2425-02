from abc import ABC, abstractmethod

from common.face import Face


class Db(ABC):
    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def insert(self, face: Face): ...

    @abstractmethod
    async def query(self, embeddings: list[list[float]], bboxes: list[list[int]]): ...
