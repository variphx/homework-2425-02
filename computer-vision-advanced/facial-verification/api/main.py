import asyncio
import sqlite3
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, WebSocket
from io import BytesIO


from relational_db.sqlite import RelationalDb
from vector_db.chromadb import VectorDb
from face_analyzer.insightface import FaceAnalyzer

shutil.rmtree("chroma", ignore_errors=True)
shutil.rmtree("sqlite.db", ignore_errors=True)

app = FastAPI()

FACE_ANALYZER = FaceAnalyzer()
RELATIONAL_DB_CONN = sqlite3.connect("sqlite.db")
VECTOR_DB_PERSIST_DIR = str(Path(__file__).parent.joinpath("chroma"))

RELALTIONAL_DB = RelationalDb(RELATIONAL_DB_CONN)
VECTOR_DB = VectorDb(VECTOR_DB_PERSIST_DIR)


async def prepare_database():
    for subdir in Path(__file__).parent.joinpath(".data", "train").iterdir():
        name = subdir.name
        for image_src in subdir.iterdir():
            async for face in FACE_ANALYZER.analyze(src=image_src, name=name):
                (rowid,) = await RELALTIONAL_DB.insert(face)
                await VECTOR_DB.insert(
                    [{"embeddings": face["embeddings"], "rowid": str(rowid)}]
                )


asyncio.run(prepare_database())


@app.post("/predictions")
async def predictions(file: UploadFile):
    data = file.file

    faces = [x async for x in FACE_ANALYZER.analyze(io=data)]
    embeddings = [x["embeddings"] for x in faces]
    bboxes = [x["bbox"] for x in faces]
    query_outputs = await VECTOR_DB.query({"embeddings": embeddings, "top_k": 1})
    rowids = [int(x[0]) for x in query_outputs]
    reldb_fetches = await asyncio.gather(
        *[RELALTIONAL_DB.fetch({"rowid": rowid, "get_name": True}) for rowid in rowids]
    )
    predictions = [
        {"label": fetch["name"], "bbox": bbox, "score": 0.5}
        for fetch, bbox in zip(reldb_fetches, bboxes)
    ]

    return predictions


@app.websocket("/ws")
async def endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        data = BytesIO(data)

        faces = [x async for x in FACE_ANALYZER.analyze(io=data)]
        if not faces:
            await websocket.send_json([])
            continue

        embeddings = [x["embeddings"] for x in faces]
        bboxes = [x["bbox"] for x in faces]
        query_outputs = await VECTOR_DB.query({"embeddings": embeddings, "top_k": 1})
        rowids = [int(x[0]) for x in query_outputs]
        reldb_fetches = await asyncio.gather(
            *[
                RELALTIONAL_DB.fetch({"rowid": rowid, "get_name": True})
                for rowid in rowids
            ]
        )
        predictions = [
            {"label": fetch["name"][0], "bbox": bbox, "score": 0.5}
            for fetch, bbox in zip(reldb_fetches, bboxes)
        ]

        await websocket.send_json(predictions)
