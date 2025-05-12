import numpy as np
from typing import TypedDict


class Face(TypedDict):
    embeddings: np.typing.NDArray[np.float32]
    bbox: list[int]
    name: str | None = None
    src: str | None = None
