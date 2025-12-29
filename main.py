from fastapi import FastAPI, UploadFile
import shutil, os
from ingest import ingest_pdfs
from rag_chain import get_answer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")

app = FastAPI()
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload(files: list[UploadFile], user_id: str = "default"):
    paths = []
    for f in files:
        path = os.path.join(UPLOAD_DIR, f.filename)
        with open(path, "wb") as out:
            shutil.copyfileobj(f.file, out)
        paths.append(path)
    ingest_pdfs(paths, user_id)
    return {"status": "Indexed"}

@app.post("/ask")
async def ask(q: str, user_id: str = "default"):
    return {"answer": get_answer(q, user_id)}
