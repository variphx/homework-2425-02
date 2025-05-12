from face_analyzer import FaceAnalyzer as AbstractFaceAnalyzer
from common.face import Face

import insightface
import numpy as np
from typing import BinaryIO
from pathlib import Path
from PIL import Image


class FaceAnalyzer(AbstractFaceAnalyzer):
    def __init__(self, analyzer: insightface.app.FaceAnalysis | None = None):
        if analyzer:
            self._analyzer = analyzer
            return

        self._analyzer = insightface.app.FaceAnalysis()
        self._analyzer.prepare(ctx_id=1)

    def analyze(
        self,
        *,
        src: str | Path | None = None,
        io: BinaryIO | None = None,
        name: str | None = None,
    ) -> list[Face]:
        if src:
            image = Image.open(src)
        if io:
            image = Image.open(io)

        image = np.array(image, dtype=np.uint8)

        faces = []
        outputs = self._analyzer.get(image)
        for output in outputs:
            face: Face = {
                "embeddings": output["embedding"],
                "bbox": output["bbox"].tolist(),
                "src": src,
                "name": name,
            }
            faces.append(face)

        return faces
