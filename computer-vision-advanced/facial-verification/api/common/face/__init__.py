import numpy as np
from typing import TypedDict
from dataclasses import dataclass


@dataclass
class Face(TypedDict):
    embeddings: np.typing.NDArray[np.float32]
    name: str | None = None
    src: str | None = None
