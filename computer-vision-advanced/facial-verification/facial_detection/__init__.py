import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis

from ..typing import Face


class FaceDetector:
    def __init__(self):
        self._detector = FaceAnalysis(providers=["CPUExecutionProvider"])
        self._detector.prepare(ctx_id=0, det_size=(640, 640))

    def detect(self, image: str) -> list[Face]:
        image_read = cv2.imread(image)
        detections = []
        for detection in self._detector.get(image_read):
            bbox = detection["bbox"]
            embedding = detection["embedding"]
            detections.append(
                Face(image=image, bbox=bbox, embedding=embedding)
            )
        return detections
