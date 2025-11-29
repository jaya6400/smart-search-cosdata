from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import numpy as np

# Import CosData SDK
from cosdata import Client

app = FastAPI(title="CosData Smart Search")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CosData configuration
COLLECTION_NAME = "my_collection3"
cosdata_client = None
collection = None

# Request models
class DocumentRequest(BaseModel):
    id: str
    text: str

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

# Generate embedding function
def generate_embedding(text: str, dimension: int = 384) -> List[float]:
    """Generate a deterministic embedding based on text."""
    seed = hash(text) % (2**32)
    np.random.seed(seed)
    embedding = np.random.randn(dimension)
    embedding = embedding / np.linalg.norm(embedding)
    return embedding.tolist()

# Initialize CosData on startup
@app.on_event("startup")
async def startup_event():
    global cosdata_client, collection
    
    print("🚀 Starting CosData Smart Search...")
    
    try:
        # Initialize CosData client
        cosdata_client = Client(
            host="http://127.0.0.1:8443",
            username="admin",
            password="admin",  # Use your actual admin key
            verify=False
        )
        print("✅ CosData client initialized")
        
        # Try to get existing collection or create new one
        try:
            collection = cosdata_client.get_collection(COLLECTION_NAME)
            print(f"✅ Collection '{COLLECTION_NAME}' found")
        except Exception:
            # Collection doesn't exist, create it
            collection = cosdata_client.create_collection(
                name=COLLECTION_NAME,
                dimension=384,
                description="Smart search collection"
            )
            print(f"✅ Collection '{COLLECTION_NAME}' created")
        
        print("✅ Initialization complete!")
        
    except Exception as e:
        print(f"❌ Initialization error: {str(e)}")
        print("⚠️  Make sure CosData server is running on http://localhost:8443")

# Health check
@app.get("/api/health")
async def health_check():
    if not cosdata_client:
        raise HTTPException(status_code=503, detail="CosData client not initialized")
    
    try:
        collections = cosdata_client.list_collections()
        return {
            "status": "healthy",
            "cosdata": "connected",
            "collections": len(collections)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"CosData unavailable: {str(e)}")

# Add document
@app.post("/api/documents")
async def add_document(doc: DocumentRequest):
    if not collection:
        raise HTTPException(status_code=503, detail="Collection not initialized")
    
    try:
        # Generate embedding
        embedding = generate_embedding(doc.text)
        
        # Upsert vector using SDK
        collection.upsert_vectors([{
            "id": doc.id,
            "values": embedding,
            "metadata": {"text": doc.text}
        }])
        
        return {
            "success": True,
            "message": "Document added successfully",
            "id": doc.id
        }
        
    except Exception as e:
        print(f"Error adding document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Search documents
@app.post("/api/search")
async def search_documents(req: SearchRequest):
    if not collection:
        raise HTTPException(status_code=503, detail="Collection not initialized")
    
    try:
        # Generate query embedding
        query_embedding = generate_embedding(req.query)
        
        # Search using SDK
        results = collection.search(
            vector=query_embedding,
            top_k=req.top_k
        )
        
        return {
            "success": True,
            "results": results,
            "query": req.query
        }
        
    except Exception as e:
        print(f"Error searching: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend
@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🚀 Starting CosData Smart Search Server")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=3000, log_level="info")