from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import httpx
import asyncio

app = FastAPI(title="CosData Smart Search")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COSDATA_URL = "http://localhost:8443"
COLLECTION_NAME = "smart_search"

class DocumentRequest(BaseModel):
    id: str
    text: str

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

def generate_embedding(text: str, dimension: int = 384) -> List[float]:
    seed = hash(text) % (2**32)
    np.random.seed(seed)
    embedding = np.random.randn(dimension)
    embedding = embedding / np.linalg.norm(embedding)
    return embedding.tolist()

async def test_endpoints():
    """Test different endpoint structures to find what works"""
    print("\n🔍 Testing CosData endpoints...")
    
    endpoints_to_test = [
        "/collections",
        "/api/collections",
        "/api/v1/collections",
        "/v1/collections",
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in endpoints_to_test:
            try:
                url = f"{COSDATA_URL}{endpoint}"
                print(f"Testing: {url}")
                response = await client.get(url)
                print(f"  ✅ Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"  ✅ WORKING ENDPOINT FOUND: {endpoint}")
                    print(f"  Response: {response.text[:200]}")
                    return endpoint
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
    
    return None

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting CosData Smart Search...")
    
    # Test to find working endpoint
    working_endpoint = await test_endpoints()
    
    if working_endpoint:
        print(f"\n✅ Found working endpoint: {working_endpoint}")
    else:
        print("\n⚠️  Could not find working endpoint")
    
    print("\n✅ Server started, but you may need to manually configure endpoints")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Server is running"}

@app.post("/api/documents")
async def add_document(doc: DocumentRequest):
    embedding = generate_embedding(doc.text)
    
    # Try different endpoint patterns
    endpoints_to_try = [
        f"/collections/{COLLECTION_NAME}/vectors",
        f"/collections/{COLLECTION_NAME}/vectors/upsert",
        f"/api/collections/{COLLECTION_NAME}/vectors",
        f"/api/v1/collections/{COLLECTION_NAME}/vectors",
        f"/v1/collections/{COLLECTION_NAME}/upsert",
    ]
    
    vector_data = {
        "id": doc.id,
        "values": embedding,
        "metadata": {"text": doc.text}
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints_to_try:
            try:
                url = f"{COSDATA_URL}{endpoint}"
                print(f"Trying: {url}")
                
                # Try both single object and array
                for payload in [vector_data, [vector_data]]:
                    response = await client.post(url, json=payload)
                    print(f"  Status: {response.status_code}")
                    
                    if response.status_code in [200, 201]:
                        print(f"  ✅ SUCCESS with endpoint: {endpoint}")
                        return {
                            "success": True,
                            "message": "Document added",
                            "id": doc.id,
                            "endpoint_used": endpoint
                        }
                        
            except Exception as e:
                print(f"  Error: {str(e)}")
                continue
    
    raise HTTPException(status_code=500, detail="Could not find working endpoint")

@app.post("/api/search")
async def search_documents(req: SearchRequest):
    query_embedding = generate_embedding(req.query)
    
    endpoints_to_try = [
        f"/collections/{COLLECTION_NAME}/search",
        f"/api/collections/{COLLECTION_NAME}/search",
        f"/api/v1/collections/{COLLECTION_NAME}/search",
        f"/v1/collections/{COLLECTION_NAME}/query",
    ]
    
    search_data = {
        "vector": query_embedding,
        "top_k": req.top_k,
        "k": req.top_k
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints_to_try:
            try:
                url = f"{COSDATA_URL}{endpoint}"
                print(f"Trying search: {url}")
                response = await client.post(url, json=search_data)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ SUCCESS with endpoint: {endpoint}")
                    return {
                        "success": True,
                        "results": response.json(),
                        "query": req.query,
                        "endpoint_used": endpoint
                    }
                    
            except Exception as e:
                print(f"  Error: {str(e)}")
                continue
    
    raise HTTPException(status_code=500, detail="Could not find working search endpoint")

@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🚀 CosData Endpoint Discovery Mode")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=3000, log_level="info")