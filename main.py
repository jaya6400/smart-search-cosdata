from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import numpy as np

from cosdata import Client

app = FastAPI(title="CosData Smart Search")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COLLECTION_NAME = "my_collection376"
VECTOR_DIM = 384

cosdata_client = None
collection = None


class DocumentRequest(BaseModel):
    id: str
    text: str


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


def generate_embedding(text: str, dimension: int = VECTOR_DIM) -> List[float]:
    seed = hash(text) % (2**32)
    np.random.seed(seed)
    v = np.random.randn(dimension)
    v = v / np.linalg.norm(v)
    return v.tolist()


@app.on_event("startup")
async def startup_event():
    global cosdata_client, collection

    try:
        cosdata_client = Client(
            host="http://127.0.0.1:8443",
            username="admin",
            password="admin",
            verify=False
        )

        try:
            collection = cosdata_client.get_collection(COLLECTION_NAME)
            print("Collection found:", COLLECTION_NAME)
        except Exception:
            collection = cosdata_client.create_collection(
                name=COLLECTION_NAME,
                dimension=VECTOR_DIM,
                description="Smart search collection"
            )
            print("Collection created:", COLLECTION_NAME)

    except Exception as e:
        print("Startup error:", e)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/documents")
async def add_document(doc: DocumentRequest):
    if not collection:
        raise HTTPException(status_code=500, detail="Collection not ready")

    try:
        embedding = generate_embedding(doc.text)

        # Correct batch insert method (transaction required)
        with collection.transaction() as txn:
            txn.batch_upsert_vectors([{
                "id": doc.id,
                "dense_values": embedding,
                "metadata": {"text": doc.text}
            }])

        return {"success": True, "id": doc.id}

    except Exception as e:
        print("Insert error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search")
async def search(req: SearchRequest):
    if not collection:
        raise HTTPException(status_code=500, detail="Collection not ready")

    try:
        q = generate_embedding(req.query)

        results = collection.search.dense(
            query_vector=q,
            top_k=req.top_k,
            return_raw_text=True
        )

        return {"success": True, "results": results}

    except Exception as e:
        print("Search error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def serve():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
