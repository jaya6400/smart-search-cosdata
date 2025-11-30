import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from cosdata import Client

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title="Smart Search with CosData")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Embedding Model
# -----------------------------
VECTOR_DIM = 384
print("Loading MiniLM model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("✅ MiniLM loaded!")

def generate_embedding(text: str) -> List[float]:
    vec = model.encode(text)
    vec = vec / np.linalg.norm(vec)
    return vec.tolist()

# -----------------------------
# CosData Setup
# -----------------------------
COLLECTION_NAME = "smartsearch"
cosdata_client = None
collection = None

# Memory store for document text
documents_store = {}  # { id: {"id": id, "text": text} }

def init_cosdata():
    global cosdata_client, collection
    try:
        cosdata_client = Client(
            host="http://127.0.0.1:8443",
            username="admin",
            password="admin",
            verify=False
        )
        print("✅ Connected to CosData server")

        # Check if collection exists
        existing_collections = cosdata_client.list_collections()
        collection_names = [c["name"] for c in existing_collections]
        if COLLECTION_NAME in collection_names:
            collection = cosdata_client.get_collection(COLLECTION_NAME)
            print(f"✅ Using existing collection: {COLLECTION_NAME}")
        else:
            # Create collection
            collection = cosdata_client.create_collection(
                name=COLLECTION_NAME,
                dimension=VECTOR_DIM,
                description="Smart Search Collection"
            )
            print(f"✅ Collection created: {COLLECTION_NAME}")

        # Create HNSW index if not exists
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
            print("✅ HNSW index created")
        except Exception as idx_err:
            print(f"⚠️  Index creation warning: {idx_err}")

    except Exception as e:
        print("❌ CosData init error:", e)

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    init_cosdata()

# -----------------------------
# Request Models
# -----------------------------
class DocumentRequest(BaseModel):
    id: str
    text: str

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

# -----------------------------
# Add document
# -----------------------------
@app.post("/api/documents")
async def add_document(doc: DocumentRequest):
    if not collection:
        raise HTTPException(status_code=503, detail="CosData collection not ready")

    try:
        embedding = generate_embedding(doc.text)

        # Store in memory
        documents_store[doc.id] = {"id": doc.id, "text": doc.text}
        print(f"✅ Stored in memory: {doc.id}")

        # Insert into CosData
        with collection.transaction() as txn:
            txn.batch_upsert_vectors([{
                "id": doc.id,
                "dense_values": embedding,
                "metadata": {"text": doc.text}
            }])

        print(f"✅ Added to CosData: {doc.id}")
        print(f"📊 Total documents in memory: {len(documents_store)}")

        return {"success": True, "id": doc.id}

    except Exception as e:
        print("❌ Add document error:", e)
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Search
# -----------------------------
@app.post("/api/search")
async def search(req: SearchRequest):
    if not collection:
        raise HTTPException(status_code=503, detail="CosData collection not ready")

    try:
        query_vec = generate_embedding(req.query)

        # Search dense vectors
        print(f"🔍 Searching for: {req.query}")
        raw_results = collection.search.dense(
            query_vector=query_vec,
            top_k=req.top_k
        )

        print(f"📦 Raw results type: {type(raw_results)}")
        print(f"📦 Raw results: {raw_results}")

        final_results = []

        # Handle different result formats
        if isinstance(raw_results, dict):
            # If it's a dict, look for common keys
            print("📦 Results is a dict")
            if "results" in raw_results:
                results_list = raw_results["results"]
            elif "matches" in raw_results:
                results_list = raw_results["matches"]
            else:
                results_list = [raw_results]
        elif isinstance(raw_results, list):
            results_list = raw_results
        else:
            print(f"⚠️ Unexpected result type: {type(raw_results)}")
            results_list = []

        print(f"📊 Processing {len(results_list)} results")

        for idx, item in enumerate(results_list):
            print(f"  Result {idx}: {item} (type: {type(item)})")
            
            if isinstance(item, dict):
                # Extract ID
                doc_id = (item.get("id") or 
                         item.get("vector_id") or 
                         item.get("document_id") or
                         f"unknown_{idx}")
                
                # Extract score/distance
                score = (item.get("score") or 
                        item.get("distance") or 
                        item.get("similarity") or 
                        0)
                
                # Try to get text from memory store first
                text = ""
                if doc_id in documents_store:
                    text = documents_store[doc_id]["text"]
                    print(f"    ✅ Found text in memory for {doc_id}")
                else:
                    # Try metadata
                    metadata = item.get("metadata", {})
                    text = metadata.get("text", "")
                    print(f"    ⚠️ No text in memory for {doc_id}, metadata: {metadata}")
                
            elif isinstance(item, str):
                doc_id = item
                score = 0
                text = documents_store.get(doc_id, {}).get("text", "")
            else:
                print(f"    ⚠️ Unknown item type: {type(item)}")
                continue

            final_results.append({
                "id": doc_id,
                "score": score,
                "text": text
            })

        print(f"✅ Returning {len(final_results)} final results")
        print(f"📊 Documents in memory: {list(documents_store.keys())}")
        
        return {
            "success": True,
            "results": final_results,
            "query": req.query,
            "debug": {
                "raw_results_type": str(type(raw_results)),
                "documents_in_store": list(documents_store.keys())
            }
        }

    except Exception as e:
        print("❌ Search error:", e)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# List documents
# -----------------------------
@app.get("/api/documents")
async def list_documents():
    return {
        "success": True,
        "count": len(documents_store),
        "documents": list(documents_store.values())
    }

# -----------------------------
# Health check
# -----------------------------
@app.get("/api/health")
async def health():
    ready = collection is not None
    return {
        "status": "running",
        "collection_ready": ready,
        "stored_docs": len(documents_store),
        "document_ids": list(documents_store.keys())
    }

# -----------------------------
# Serve frontend
# -----------------------------
@app.get("/")
async def serve():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000, log_level="info")