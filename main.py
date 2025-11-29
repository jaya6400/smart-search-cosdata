from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import numpy as np
import time

from cosdata import Client

app = FastAPI(title="CosData Smart Search")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COLLECTION_NAME = "smart_search"
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

    print("\n" + "="*60)
    print("🚀 Initializing CosData Smart Search")
    print("="*60)
    
    try:
        # Connect to CosData
        cosdata_client = Client(
            host="http://127.0.0.1:8443",
            username="admin",
            password="admin",  # CHANGE THIS to your admin key
            verify=False
        )
        print("✅ Connected to CosData")

        # List existing collections
        existing = cosdata_client.list_collections()
        print(f"📋 Found {len(existing)} existing collection(s)")

        # Try to get existing collection
        collection_exists = False
        for col_info in existing:
            if col_info.get('name') == COLLECTION_NAME:
                collection_exists = True
                break

        if collection_exists:
            print(f"✅ Using existing collection: {COLLECTION_NAME}")
            collection = cosdata_client.get_collection(COLLECTION_NAME)
        else:
            # Create new collection
            print(f"📝 Creating collection: {COLLECTION_NAME}")
            collection = cosdata_client.create_collection(
                name=COLLECTION_NAME,
                dimension=VECTOR_DIM,
                description="Smart search collection"
            )
            print(f"✅ Collection created")
            
            # Wait for collection to be ready
            time.sleep(1)
            
            # Create index
            print("📝 Creating index...")
            try:
                collection.create_index(
                    distance_metric="cosine",
                    num_layers=10,
                    max_cache_size=1000,
                    ef_construction=128,
                    ef_search=64,
                    neighbors_count=32,
                    level_0_neighbors_count=64
                )
                print("✅ Index created")
            except Exception as idx_err:
                print(f"⚠️  Index warning: {idx_err}")

        print("="*60)
        print("✅ Initialization Complete - Ready to use!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()


@app.get("/api/health")
async def health():
    if not cosdata_client or not collection:
        raise HTTPException(status_code=503, detail="CosData not ready")
    
    try:
        collections = cosdata_client.list_collections()
        return {
            "status": "healthy",
            "collection": COLLECTION_NAME,
            "total_collections": len(collections)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/api/documents")
async def add_document(doc: DocumentRequest):
    if not collection:
        raise HTTPException(status_code=503, detail="Collection not ready")

    try:
        embedding = generate_embedding(doc.text)

        with collection.transaction() as txn:
            txn.batch_upsert_vectors([{
                "id": doc.id,
                "dense_values": embedding,
                "metadata": {"text": doc.text}
            }])

        print(f"✅ Document added: {doc.id}")
        return {"success": True, "id": doc.id}

    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search")
async def search(req: SearchRequest):
    if not collection:
        raise HTTPException(status_code=503, detail="Collection not ready")

    try:
        q = generate_embedding(req.query)

        results = collection.search.dense(
            query_vector=q,
            top_k=req.top_k,
            return_raw_text=True
        )

        print(f"✅ Search: found {len(results)} results")
        return {"success": True, "results": results, "query": req.query}

    except Exception as e:
        print(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def serve():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000, log_level="info")