from vector_db import VectorDb as AbstractVectorDb

import numpy as np
import chromadb
from pathlib import Path
from typing import TypedDict


class Value(TypedDict):
    embeddings: np.typing.NDArray[np.float32]
    rowid: str


class QueryRequest(TypedDict):
    embeddings: np.typing.NDArray[np.float32]
    top_k: int = 5


class VectorDb(AbstractVectorDb):
    def __init__(self, location: str | Path = ":memory:"):
        if location == ":memory:":
            self._client = chromadb.EphemeralClient()
        else:
            self._client = chromadb.PersistentClient(path=location)

        self._collection = self._client.create_collection("faces")

    async def insert(self, values: list[Value]):
        ids = [x["rowid"] for x in values]
        embeddings = [x["embeddings"] for x in values]
        self._collection.add(ids=ids, embeddings=embeddings)

    async def query(self, request: QueryRequest) -> list[list[str]]:
        results = self._collection.query(
            query_embeddings=request["embeddings"],
            n_results=request["top_k"],
            include=[],
        )

        return results["ids"]
