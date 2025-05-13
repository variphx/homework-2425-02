from db import Db as AbstractDb
from common.face import Face

import numpy as np
from pymilvus import MilvusClient, DataType
from typing import TypedDict


class QueryOutput(TypedDict):
    name: str
    score: str


class Db(AbstractDb):
    def __init__(self, location: str):
        self._client = MilvusClient(location)

        # schema = MilvusClient.create_schema(auto_id=True, enable_dynamic_field=True)
        # schema.add_field("id", datatype=DataType.INT64, is_primary=True, auto_id=True)
        # schema.add_field("vector", datatype=DataType.FLOAT_VECTOR, dim=512)
        # # schema.add_field("name", datatype=DataType.STRING, max_length=30)
        # # schema.add_field("src", datatype=DataType.STRING, max_length=512)

        # index_params = MilvusClient.prepare_index_params()
        # index_params.add_index(
        #     "vector", index_type="FLAT", metric_type="COSINE", index_name="vector_index"
        # )

        if self._client.has_collection(collection_name="faces"):
            self._client.drop_collection(collection_name="faces")
        self._client.create_collection(
            collection_name="faces",
            dimension=512,
            auto_id=True,
            # collection_name="faces", schema=schema, index_params=index_params
        )

    async def insert(self, faces: list[Face]):
        data = [
            {"vector": x["embeddings"], "name": x["name"], "src": x["src"]}
            for x in faces
        ]
        self._client.insert(collection_name="faces", data=data)

    async def query(
        self, embeddings: list[list[float]], bboxes: list[list[int]] | None = None
    ):
        outputs = self._client.search(
            collection_name="faces",
            anns_field="vector",
            data=embeddings,
            limit=1,
            output_fields=["name"],
        )

        if bboxes:
            for output, bbox in zip(outputs, bboxes):
                (output,) = output
                yield QueryOutput(
                    {
                        "name": output["entity"]["name"],
                        "bbox": bbox,
                        "score": output["distance"],
                    }
                )

        else:
            for output in output:
                (output,) = output
                yield QueryOutput(
                    {"name": output["entity"]["name"], "score": output["distance"]}
                )
