import asyncio
import sqlite3
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, WebSocket
from io import BytesIO


from relational_db.sqlite import RelationalDb
from vector_db.chromadb import VectorDb
from db.milvus import Db
from face_analyzer.insightface import FaceAnalyzer

shutil.rmtree("chroma", ignore_errors=True)
shutil.rmtree("sqlite.db", ignore_errors=True)

app = FastAPI()

FACE_ANALYZER = FaceAnalyzer()
# RELATIONAL_DB_CONN = sqlite3.connect("sqlite.db")
# VECTOR_DB_PERSIST_DIR = str(Path(__file__).parent.joinpath("chroma"))

# RELALTIONAL_DB = RelationalDb(RELATIONAL_DB_CONN)
# VECTOR_DB = VectorDb(VECTOR_DB_PERSIST_DIR)

DB = Db("milvus.db")


async def prepare_database():
    for subdir in Path(__file__).parent.joinpath(".data", "train").iterdir():
        name = subdir.name
        for image_src in subdir.iterdir():
            async for face in FACE_ANALYZER.analyze(src=image_src, name=name):
                await DB.insert([face])
                # (rowid,) = await RELALTIONAL_DB.insert(face)
                # await VECTOR_DB.insert(
                #     [{"embeddings": face["embeddings"], "rowid": str(rowid)}]
                # )


asyncio.run(prepare_database())


@app.post("/predictions")
async def predictions(file: UploadFile):
    data = file.file

    faces = [x async for x in FACE_ANALYZER.analyze(io=data)]
    if not faces:
        return []

    embeddings = [x["embeddings"] for x in faces]
    bboxes = [x["bbox"] for x in faces]
    predictions = [x async for x in DB.query(embeddings=embeddings, bboxes=bboxes)]

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
        predictions = [x async for x in DB.query(embeddings=embeddings, bboxes=bboxes)]

        await websocket.send_json(predictions)
