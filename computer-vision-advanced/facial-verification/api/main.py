import time
import sqlite3
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile

from relational_db.sqlite import RelationalDb
from vector_db.chromadb import VectorDb
from face_analyzer.insightface import FaceAnalyzer

shutil.rmtree("chromadb", ignore_errors=True)
shutil.rmtree("sqlite.db", ignore_errors=True)

app = FastAPI()

FACE_ANALYZER = FaceAnalyzer()
RELATIONAL_DB_CONN = sqlite3.connect("sqlite.db")
VECTOR_DB_PERSIST_DIR = str(Path(__file__).parent.joinpath("chromadb"))

RELALTIONAL_DB = RelationalDb(RELATIONAL_DB_CONN)
VECTOR_DB = VectorDb(VECTOR_DB_PERSIST_DIR)

for subdir in Path(__file__).parent.joinpath(".data", "train").iterdir():
    name = subdir.name
    for image_src in subdir.iterdir():
        face = FACE_ANALYZER.analyze(src=image_src, name=name)[0]
        (rowid,) = RELALTIONAL_DB.insert(face)
        VECTOR_DB.insert([{"embeddings": face["embeddings"], "rowid": str(rowid)}])


@app.post("/api/v1/predictions")
async def predict(file: UploadFile):
    io = file.file
    start_ts = time.time_ns()
    face = FACE_ANALYZER.analyze(io=io)[0]
    rowid = int(VECTOR_DB.query({"embeddings": face["embeddings"], "top_k": 1})[0][0])
    name = RELALTIONAL_DB.fetch({"rowid": rowid, "get_name": True})["name"]
    end_ts = time.time_ns()
    return {"name": name, "time": end_ts - start_ts}
