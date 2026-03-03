# NYC Restaurant Search - Project Plan

## Goal
Build a vector-based retrieval system to find restaurants in NYC that match a user's natural language description.

## Tech Stack
### Core
- **Language**: Python 3.10+
- **Database**: PostgreSQL with `pgvector` extension
    - **Why**: Standard relational database features plus efficient vector similarity search using IVFFlat or HNSW indexing.
- **Environment**: Managed via `venv` or `conda`.

### Vector Search & Embeddings
- **Embedding Model**: OpenAI `text-embedding-3-small`
    - **Why**: High quality, affordable, easy to implement.
    - **Alternative**: `sentence-transformers/all-MiniLM-L6-v2` (Local, free logic).
- **Vector Store**: `pgvector` in PostgreSQL.

### Backend API
- **Framework**: FastAPI
    - **Why**: High performance, easy async support, auto-generated docs, great for ML/Data apps.

### Information Retrieval
- **Hybrid Search (Optional but recommended)**: Combine vector search with keyword search (BM25) for better precision.
- **Reranking (Optional)**: Re-rank top-k results using a cross-encoder model for better relevance.

### Frontend
- **Framework**: Streamlit
    - **Why**: Fastest way to build data/ML prototypes. Easy to visualize tables, maps, and text.
    - **Status**: Suggested (vs React which is more complex).

## Implementation Phases
1.  **Setup & Data Acquisition**
    -   Initialize project structure.
    -   Set up PostgreSQL and `pgvector`.
    -   Acquire NYC restaurant dataset (e.g., Yelp dataset subset or scrape).
2.  **Data Processing & Embedding**
    -   Clean and preprocess restaurant text data (reviews, descriptions, categories).
    -   Generate embeddings for each restaurant using the chosen model.
    -   Store embeddings in Postgres.
3.  **Retrieval System**
    -   Implement the search endpoint: Query embedding -> Cosine similarity search.
    -   Add filters (e.g., by price, location, rating).
4.  **User Interface**
    -   Build a Streamlit app to accept queries and display results.
    -   Show restaurant details (name, rating, address, similarity score).
