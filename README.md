# 📦 Smart Search App with CosData Vector Database

A complete AI-powered semantic search application built with FastAPI and CosData OSS. This project enables you to store documents as vector embeddings and search them using similarity matching - all running locally without any paid APIs!

## 🌟 Features

- ✅ **Vector-based semantic search** - Find similar documents using embeddings
- ✅ **CosData integration** - Open-source vector database
- ✅ **Offline embeddings** - No OpenAI or external API required
- ✅ **FastAPI backend** - Modern, fast Python API
- ✅ **Beautiful UI** - Clean, responsive frontend
- ✅ **Docker setup** - One command to start the database
- ✅ **Windows compatible** - Works with Git Bash
- ✅ **Vercel ready** - Deploy frontend easily

---

## 📋 Prerequisites

Before you begin, ensure you have:

- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Git Bash** (Windows) - [Download here](https://git-scm.com/downloads)

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

### Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📦 Step 3: Dependencies

Create a `requirements.txt` file with:
```txt
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
numpy==1.24.3
python-multipart==0.0.6
```

Then install:
```bash
pip install -r requirements.txt
```

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
==================================================
🚀 Starting CosData Smart Search Server
==================================================
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:3000
🚀 Starting CosData Smart Search...
✅ CosData client initialized
✅ Collection 'smart_search' created
✅ Initialization complete!
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
- **Add Document** section
- **Search Documents** section
- Sample data buttons for quick testing

---

## 📝 Step 6: Using the Application

### Adding Documents:

1. Click one of the sample data buttons (AI Technology, Climate Change, or Space Exploration)
2. Or manually enter:
   - **Document ID:** `doc_1`
   - **Document Text:** `Your text content here`
3. Click **Add Document**

### Searching Documents:

1. Enter a search query (e.g., "machine learning", "climate", "space")
2. Click **Search**
3. View ranked results with similarity scores

---

## 🔌 API Endpoints

### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "cosdata": "connected",
  "collections": 1
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
  "message": "Document added successfully",
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
      "score": 0.9234,
      "metadata": {
        "text": "Document content..."
      }
    }
  ],
  "query": "your search query"
}
```

---

## 🗂️ Project Structure
```
smart-search-cosdata/
│
├── main.py                 # FastAPI backend server
├── static/
│   └── index.html         # Frontend UI
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── venv/                  # Virtual environment (not committed)
└── .gitignore            # Git ignore file
```

---

## 🚀 Deployment

### Backend:
Deploy to Railway.app, Render.com, Fly.io, or any platform supporting Python web apps.

### Frontend (Vercel):

Create `vercel.json`:
```json
{
  "routes": [
    { "src": "/(.*)", "dest": "/static/$1" }
  ]
}
```

Deploy:
```bash
npm install -g vercel
vercel
```

**Note:** Update frontend to point to your deployed backend URL.

---

## 🐛 Troubleshooting

### CosData container not starting:
```bash
# Check container logs
docker logs cosdata-server

# Restart container
docker restart cosdata-server

# Remove and recreate
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

### Module not found errors:
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify virtual environment is activated
which python  # Should show path to venv
```

### Connection refused errors:

1. Verify CosData is running: `docker ps`
2. Check if ports are accessible: `curl http://localhost:8443`
3. Ensure no firewall is blocking ports 8443, 50051, or 3000

---

## 🔧 Configuration

### Change CosData host/port:

In `main.py`:
```python
COSDATA_URL = "http://your-cosdata-host:8443"
```

### Change embedding dimension:
```python
def generate_embedding(text: str, dimension: int = 768):  # Change from 384
    # ... rest of code
```

### Change collection name:
```python
COLLECTION_NAME = "my_custom_collection"
```

---

## 📚 Next Steps & Enhancements

### Use Real Embeddings:

Replace the dummy embedding function with a real model:
```bash
pip install sentence-transformers
```
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str) -> List[float]:
    return model.encode(text).tolist()
```

### Add Authentication:
```bash
pip install python-jose passlib
```

### Add File Upload:

Support PDF, DOCX, TXT file uploads for automatic indexing.

### Add Metadata Filtering:

Filter search results by date, category, author, etc.

### Add Batch Import:

Upload CSV/JSON files with multiple documents at once.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/smart-search-cosdata/issues)
- **CosData Docs:** [https://docs.cosdata.io](https://docs.cosdata.io)
- **FastAPI Docs:** [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

## 🙏 Acknowledgments

- [CosData](https://cosdata.io) - Open-source vector database
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- All contributors and users of this project

---

**Author: Jaya Dubey**

**Last Updated:** November 30, 2025