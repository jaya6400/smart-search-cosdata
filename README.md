# 📦 Smart Search App with CosData Vector Database

A complete AI-powered semantic search application built with FastAPI and CosData OSS. This project enables you to store documents as vector embeddings and search them using similarity matching - all running locally without any paid APIs!

**Website:**

**Demo Link:**

## 🌟 Features

- ✅ **Vector-based semantic search** - Find similar documents using embeddings
- ✅ **CosData integration** - Open-source vector database
- ✅ **Real AI embeddings** - Using sentence-transformers (all-MiniLM-L6-v2)
- ✅ **Offline operation** - No OpenAI or external API required
- ✅ **FastAPI backend** - Modern, fast Python API
- ✅ **Beautiful UI** - Clean, responsive frontend with keyword highlighting
- ✅ **Docker setup** - One command to start the database
- ✅ **Windows compatible** - Works with Git Bash
- ✅ **In-memory document store** - Reliable text retrieval

---

<img width="765" height="403" alt="Captureweb" src="https://github.com/user-attachments/assets/9e2185a8-a960-48bb-80b1-761a530537eb" />

## 📋 Prerequisites

Before you begin, ensure you have:

- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Git Bash** (Windows) - [Download here](https://git-scm.com/downloads)
- **~500MB disk space** - For sentence-transformers model

---

## 🐳 Step 1: Start CosData Server

### Pull and run the Docker container:
```bash
# Pull the latest CosData image
docker pull cosdataio/cosdata:latest

# Run CosData in interactive mode
docker run -it --name cosdata-server -p 8443:8443 -p 50051:50051 cosdataio/cosdata:latest
```

### When prompted, set your admin key:
```
Enter admin key: my-secret-key-123
Re-enter admin key: my-secret-key-123
```

**Save this admin key - you'll need it later!**

### Verify the server is running:

You should see logs like:
```
[INFO] starting HTTP server at http://0.0.0.0:8443
[INFO] gRPC server listening on [::1]:50051
```

**Keep this terminal open!** Press `Ctrl+C` to stop, then restart in background:
```bash
# Remove the container
docker rm cosdata-server

# Run in detached mode (background)
docker run -d --name cosdata-server -p 8443:8443 -p 50051:50051 cosdataio/cosdata:latest
```

### CosData is now available at:
- **HTTP API:** `http://localhost:8443`
- **gRPC:** `localhost:50051`

---

## 🛠️ Step 2: Project Setup

### Clone the repository:
```bash
git clone https://github.com/jaya6400/smart-search-cosdata.git
cd smart-search-cosdata
```

### Create a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows Git Bash)
source venv/Scripts/activate

# On Windows CMD
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

---

## 📦 Step 3: Install Dependencies

The `requirements.txt` includes:
```txt
fastapi==0.104.1
uvicorn==0.24.0
numpy==1.24.3
python-multipart==0.0.6
sentence-transformers==2.2.2
cosdata-client
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

**Note:** First run will download the `all-MiniLM-L6-v2` model (~80MB). This happens automatically.

---

## ▶️ Step 4: Run the Backend

### Update the admin key in `main.py`:

Find this line and replace with your actual admin key:
```python
password="my-secret-key-123",  # Replace with YOUR admin key
```

### Start the FastAPI server:
```bash
python main.py
```

### You should see:
```
Loading MiniLM model...
✅ MiniLM loaded!
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:3000
✅ Connected to CosData server
✅ Using existing collection: smartsearch
✅ HNSW index created
```

### Backend is now running at:
**http://localhost:3000**

---

## 🎨 Step 5: Access the Frontend

Open your browser and navigate to:
```
http://localhost:3000
```

You should see the Smart Search interface with:
- **Add Document** section with 5 sample data buttons
- **Search Documents** section
- Beautiful gradient UI with result highlighting

---

## 📝 Step 6: Using the Application

### Adding Documents:

1. Click one of the sample data buttons (AI Technology, Climate Change, Space Exploration, Renewable Energy, Machine Learning)
2. Or manually enter:
   - **Document ID:** `doc_1`
   - **Document Text:** `Your text content here`
3. Click **Add Document**
4. You should see: ✅ Document added successfully!

### Searching Documents:

1. Enter a search query (e.g., "machine learning", "climate", "space exploration")
2. Click **Search** or press Enter
3. View ranked results with:
   - Similarity scores (higher = better match)
   - Document IDs
   - Full document text with highlighted keywords
   - Debug panel showing raw API response

---

## 🔌 API Endpoints

### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "running",
  "collection_ready": true,
  "stored_docs": 5,
  "document_ids": ["doc_ai_1", "doc_climate_1", "doc_space_1", "doc_energy_1", "doc_ml_1"]
}
```

### Add Document
```http
POST /api/documents
Content-Type: application/json

{
  "id": "doc_1",
  "text": "Your document content here"
}
```

**Response:**
```json
{
  "success": true,
  "id": "doc_1"
}
```

### Search Documents
```http
POST /api/search
Content-Type: application/json

{
  "query": "your search query",
  "top_k": 5
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": "doc_1",
      "score": 0.8534,
      "text": "Document content..."
    }
  ],
  "query": "your search query",
  "debug": {
    "raw_results_type": "<class 'list'>",
    "documents_in_store": ["doc_1", "doc_2"]
  }
}
```

### List All Documents
```http
GET /api/documents
```

**Response:**
```json
{
  "success": true,
  "count": 3,
  "documents": [
    {"id": "doc_1", "text": "Document 1 content"},
    {"id": "doc_2", "text": "Document 2 content"}
  ]
}
```

---

## 🗂️ Project Structure
```
smart-search-cosdata/
│
├── main.py                 # FastAPI backend with sentence-transformers
├── static/
│   └── index.html         # Frontend UI with search highlighting
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── venv/                  # Virtual environment (not committed)
└── .gitignore            # Git ignore file
```

---

## 🧠 How It Works

### 1. **Embedding Generation**
- Uses `sentence-transformers/all-MiniLM-L6-v2` model
- Converts text to 384-dimensional vectors
- Normalized for cosine similarity search

### 2. **Document Storage**
- **CosData Vector DB:** Stores embeddings for fast similarity search
- **In-Memory Store:** Stores original text for retrieval
- Dual storage ensures reliable text recovery

### 3. **Semantic Search**
- Query converted to embedding using same model
- CosData performs HNSW (Hierarchical Navigable Small World) search
- Returns top-k most similar documents
- Results enhanced with stored text content

---

## 🚀 Deployment (If need in production)

### Backend Deployment:

The backend requires a long-running server. Deploy to:

1. **Railway.app** (Recommended)

2. **Render.com**

3. **Fly.io**

4. **AWS EC2 / Google Cloud Run / Azure**

### Frontend Deployment:
1. **Vercel**
2. **Netlify**

**Important:** Update API URLs in `index.html` to point to your deployed backend.

---

## 🐛 Troubleshooting

### CosData container not starting:
```bash
# Check container logs
docker logs cosdata-server

# Restart container
docker restart cosdata-server

# Fresh start
docker stop cosdata-server
docker rm cosdata-server
docker run -d --name cosdata-server -p 8443:8443 -p 50051:50051 cosdataio/cosdata:latest
```

### Backend won't start:
```bash
# Check if port 3000 is in use
netstat -ano | findstr "3000"

# Try a different port
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Model download issues:
```bash
# Manually download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### "Collection not ready" errors:

1. Verify CosData is running: `docker ps`
2. Check backend logs for initialization errors
3. Restart backend: `python main.py`

### No text in search results:

- Documents added before the in-memory store won't have text
- Solution: Re-add your documents
- The in-memory store persists only during server runtime

---

## 🔧 Configuration

### Change CosData host/port:

In `main.py`:
```python
cosdata_client = Client(
    host="http://your-cosdata-host:8443",
    username="admin",
    password="your-admin-key",
    verify=False
)
```

### Use a different embedding model:
```python
# Available models: https://www.sbert.net/docs/pretrained_models.html
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')  # Multilingual
# or
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')  # Higher quality, slower
```

**Note:** Change `VECTOR_DIM` to match your model's output dimension.

### Change collection name:
```python
COLLECTION_NAME = "my_custom_collection"
```

---

## 📚 Advanced Features

### Batch Document Upload:
```python
# Add to main.py
@app.post("/api/documents/batch")
async def add_documents_batch(docs: List[DocumentRequest]):
    results = []
    for doc in docs:
        try:
            embedding = generate_embedding(doc.text)
            documents_store[doc.id] = {"id": doc.id, "text": doc.text}
            # ... insert into CosData
            results.append({"id": doc.id, "success": True})
        except Exception as e:
            results.append({"id": doc.id, "success": False, "error": str(e)})
    return {"results": results}
```

### File Upload Support:
```bash
pip install python-multipart PyPDF2 python-docx
```

### Persistent Document Storage:

Replace in-memory store with SQLite or PostgreSQL for production.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/jaya6400/smart-search-cosdata/issues)
- **CosData Docs:** [https://docs.cosdata.io](https://docs.cosdata.io)
- **FastAPI Docs:** [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Sentence Transformers:** [https://www.sbert.net](https://www.sbert.net)

---

## Acknowledgments

- [CosData](https://cosdata.io) - Open-source vector database
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [Sentence Transformers](https://www.sbert.net) - State-of-the-art embeddings
- All contributors and users of this project

---

## 📊 Model Performance

**all-MiniLM-L6-v2** specifications:
- **Size:** ~80MB
- **Dimensions:** 384
- **Speed:** ~14,000 sentences/second (GPU), ~3,000 (CPU)
- **Quality:** Optimized for semantic similarity
- **Languages:** English only

For other languages or better quality, see [SBERT Pretrained Models](https://www.sbert.net/docs/pretrained_models.html).

---

## Screenshots
- <img width="676" height="421" alt="Captureweb2" src="https://github.com/user-attachments/assets/3a3b395e-6275-43c7-8322-5bfc0ccc6e90" />
- <img width="593" height="400" alt="Captureterminal" src="https://github.com/user-attachments/assets/0ca3e152-073e-45a5-ae23-37f97231ab06" />



**Author: Jaya Dubey**

**Last Updated:** November 30, 2025
