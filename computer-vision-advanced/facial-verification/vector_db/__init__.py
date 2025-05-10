import faiss
import numpy as np
from pathlib import Path


class DbIndex:
    def __init__(self, *, d: int) -> None:
        self._index = faiss.IndexFlatL2(d)
        self._persist_dir = Path.cwd()

    def add(self, entries_num: int, entries: np.typing.NDArray[np.float32]):
        self._index.add(entries_num, entries)

    def search(self, embedding: np.typing.NDArray[np.float32]):
        ...

    def persist(self):
        faiss.write_index(self._index, self._persist_dir / "faces.index")
