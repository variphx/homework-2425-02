import cv2
import numpy as np


class Face:
    def __init__(
        self,
        *,
        image: str,
        bbox: np.typing.NDArray[np.float32],
        embedding: np.typing.NDArray[np.float32],
        name: str | None = None
    ) -> None:
        self._image = image
        self._bbox = [int(x) for x in bbox]
        self._embedding = embedding
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def image(self):
        return self._image

    @property
    def face(self):
        x1, y1, x2, y2 = self._bbox
        image = cv2.imread(self._image)
        return image[y1:y2, x1:x2]

    @property
    def embedding(self):
        return self._embedding
