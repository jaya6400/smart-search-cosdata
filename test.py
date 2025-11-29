from cosdata import Client

# Initialize the client with your server details
client = Client(
    host="http://127.0.0.1:8443",  # Default host
    username="admin",               # Default username
    password="admin",               # Default password
    verify=False                    # SSL verification
)

# Create a collection for storing 768-dimensional vectors
collection = client.create_collection(
    name="my_collection3",
    dimension=768,                  # Vector dimension
    description="My vector collection"
)

# Create an index with custom parameters
index = collection.create_index(
    distance_metric="cosine",       # Default: cosine
    num_layers=10,                  # Default: 10
    max_cache_size=1000,           # Default: 1000
    ef_construction=128,           # Default: 128
    ef_search=64,                  # Default: 64
    neighbors_count=32,            # Default: 32
    level_0_neighbors_count=64     # Default: 64
)

# Generate and insert vectors
import numpy as np

def generate_random_vector(id: int, dimension: int) -> dict:
    values = np.random.uniform(-1, 1, dimension).tolist()
    return {
        "id": f"vec_{id}",
        "dense_values": values,
        "document_id": f"doc_{id//10}",  # Group vectors into documents
        "metadata": {  # Optional metadata
            "created_at": "2024-03-20",
            "category": "example"
        }
    }

# Generate and insert vectors
vectors = [generate_random_vector(i, 768) for i in range(100)]

# Add vectors using a transaction
# with collection.transaction() as txn:
#     # Single vector upsert
#     txn.upsert_vector(vectors[0])
#     # Batch upsert for remaining vectors
#     txn.batch_upsert_vectors(vectors[1:])

# Search for similar vectors
results = collection.search.dense(
    query_vector=vectors[0]["dense_values"],  # Use first vector as query
    top_k=5,                                  # Number of nearest neighbors
    return_raw_text=True
)

print("client created:", results)