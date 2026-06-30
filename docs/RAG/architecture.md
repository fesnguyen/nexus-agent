# RAG Architecture V3 (Current implementation)

                    RAGService
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
 Query Rewrite     Index Manager     Context Compression
        │               │
        │               ▼
        │        Knowledge Loading
        │               │
        │      ┌────────┴────────┐
        │      │                 │
        │   Loader            Chunker
        │      │                 ▲
        │      ▼                 │
        │    Parser ─────────────┘
        │
        ▼
      Embedder
        │
        ▼
    Faiss Store
        │
        ▼
   Search Results
        │
        ▼
 Context Compressor
        │
        ▼
     Final Context