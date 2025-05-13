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

        self._analyzer = insightface.app.FaceAnalysis(
            providers=["CUDAExecutionProvider"]
        )
        self._analyzer.prepare(ctx_id=1)

    async def analyze(
        self,
        *,
        src: str | Path | None = None,
        io: BinaryIO | None = None,
        name: str | None = None,
    ):
        if src:
            image = Image.open(src)
        if io:
            image = Image.open(io)

        image = np.array(image, dtype=np.uint8)

        outputs = self._analyzer.get(image)
        for output in outputs:
            face = Face(
                {
                    "embeddings": output["embedding"].tolist(),
                    "bbox": output["bbox"].astype(np.int64).tolist(),
                    "src": str(src),
                    "name": name,
                }
            )

            yield face
