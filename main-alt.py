from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
import numpy as np
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

COSDATA_URL = "http://127.0.0.1:8443"
COLLECTION = "my_collection3"

class Doc(BaseModel):
    id: str
    text: str

class Search(BaseModel):
    query: str
    top_k: int = 5

def embed(text):
    seed = hash(text) % (2**32)
    np.random.seed(seed)
    v = np.random.randn(384)
    v /= np.linalg.norm(v)
    return v.tolist()

@app.post("/api/documents")
async def add_doc(doc: Doc):
    payload = [{
        "id": doc.id,
        "values": embed(doc.text),
        "metadata": {"text": doc.text}
    }]

    async with httpx.AsyncClient() as client:
        for endpoint in [
            f"/collections/{COLLECTION}/vectors/upsert",
            f"/collections/{COLLECTION}/vectors",
            f"/v1/collections/{COLLECTION}/upsert"
        ]:
            url = COSDATA_URL + endpoint
            try:
                r = await client.post(url, json=payload)
                if r.status_code in (200, 201):
                    return {"success": True, "endpoint": endpoint}
            except:
                pass

    raise HTTPException(500, "No working endpoint")

@app.post("/api/search")
async def search(body: Search):
    payload = {
        "vector": embed(body.query),
        "top_k": body.top_k
    }

    async with httpx.AsyncClient() as client:
        for endpoint in [
            f"/collections/{COLLECTION}/search",
            f"/v1/collections/{COLLECTION}/query",
        ]:
            url = COSDATA_URL + endpoint
            try:
                r = await client.post(url, json=payload)
                if r.status_code == 200:
                    return {"success": True, "results": r.json()}
            except:
                pass

    raise HTTPException(500, "Search endpoint not found")

@app.get("/")
def home():
    return FileResponse("static/index.html")
