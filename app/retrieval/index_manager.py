"""
Index manager.

Responsibilities
----------------
Coordinate the entire indexing pipeline.

Current implementation
----------------------
- Full rebuild

Future implementation
---------------------
- Incremental indexing
- Detect modified files
- Remove deleted files
- Re-embed changed files
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.models.embedding_manager import EmbeddingManager
from app.retrieval.ingestion.file_hasher import FileHasher
from app.retrieval.ingestion.loader import Loader
from app.retrieval.processing.chunker import Chunker
from app.retrieval.processing.embedder import Embedder
from app.retrieval.schema import Chunk, Document, SyncPlan
from app.retrieval.storage.chunk_store import ChunkStore
from app.retrieval.storage.faiss_store import FaissStore
from app.retrieval.storage.file_index_store import (
    FileIndexStore,
    IndexedFile,
)
from app.retrieval.storage.mapping_store import (
    MappingStore,
    VectorMapping,
)


@dataclass(slots=True)
class IndexResult:
    """
    Result of a complete indexing run.
    """

    documents: list[Document]

    chunks: list[Chunk]

    embeddings: np.ndarray


class IndexManager:
    """
    Coordinate the indexing pipeline.
    """

    def __init__(
        self,
        loader: Loader,
        chunker: Chunker,
        embedder: Embedder,
        chunk_store: ChunkStore,
        file_index_store: FileIndexStore,
        mapping_store: MappingStore,
        vector_store: FaissStore,
    ) -> None:

        self._loader = loader
        self._chunker = chunker
        self._embedder = embedder

        self._chunk_store = chunk_store
        self._file_index_store = file_index_store
        self._mapping_store = mapping_store
        self._vector_store = vector_store

    def build(self) -> IndexResult:
        """
        Perform a complete rebuild.

        Future versions will replace this with
        incremental indexing without changing
        the public API.
        """

        #
        # Load documents
        #
        documents = self._loader.load()

        #
        # Chunk documents
        #
        chunks = self._chunker.chunk_documents(
            documents
        )

        #
        # Generate embeddings
        #
        embeddings = self._embedder.embed(
            chunks
        )

        # IP map for chunks
        vector_ids = self._mapping_store.allocate_vector_ids(
            len(chunks)
        )

        #
        # Build FAISS
        #
        self._vector_store.build(
            embeddings,
            vector_ids,
        )

        self._vector_store.save()

        #
        # Store chunks
        #
        self._chunk_store.clear()

        self._chunk_store.add_many(
            chunks
        )

        #
        # Store file index
        #
        self._file_index_store.clear()

        for document in documents:

            chunk_count = sum(
                chunk.source == document.source
                for chunk in chunks
            )

            self._file_index_store.add(
                IndexedFile(
                    source=document.source,
                    content_hash=FileHasher.sha256(
                        document.source
                    ),
                    embedding_model=self._embedder.model_name,
                    chunk_count=chunk_count,
                )
            )

        #
        # Store vector mapping
        #
        self._mapping_store.clear()

        for vector_id, chunk in enumerate(chunks):

            self._mapping_store.add(
                VectorMapping(
                    chunk_id=chunk.id,
                    vector_store="faiss",
                    embedding_model=self._embedder.model_name,
                    vector_id=vector_id,
                )
            )

        return IndexResult(
            documents=documents,
            chunks=chunks,
            embeddings=embeddings,
        )
    
    def load(self) -> IndexResult:
        """
        Load an existing retrieval index.
        """

        #
        # Load FAISS
        #
        self._vector_store.load()

        #
        # Load chunks
        #
        chunks = self._chunk_store.get_all()

        #
        # Load documents
        #
        documents = self._loader.load()

        return IndexResult(
            documents=documents,
            chunks=chunks,
            embeddings=None,
        )
    
        
    def exists(self) -> bool:
        """
        Temporary check if the faiss store exist
        """
        return self._vector_store.exists()
    
    
    def detect_changes(self) -> SyncPlan:
        """
        Compare current files on disk against the indexed metadata store 
        to compute a delta synchronization plan.

        Returns:
            SyncPlan: An object containing categorized lists of added, 
                    modified, and deleted files to reconcile state.
        """
        # Load the live state of files currently present in the source directories
        documents = self._loader.load()

        # Map existing database records by their source path for O(1) lookups
        indexed = {
            item.source: item
            for item in self._file_index_store.get_all()
        }

        # Map live documents by their absolute file path
        current = {
            document.source: document
            for document in documents
        }

        added: list[Document] = []
        modified: list[Document] = []
        deleted: list[IndexedFile] = []

        # Identify files that are either newly introduced or mutated
        for path, document in current.items():
            record = indexed.get(path)

            # Case 1: Path does not exist in index -> File was newly added
            if record is None:
                added.append(document)
                continue

            # Case 2: Path exists, check content state via a fresh cryptographic hash
            content_hash = FileHasher.sha256(path)

            # If hashes diverge, the contents were modified since the last index run
            if content_hash != record.content_hash:
                modified.append(document)

        # Identify files that exist in the index but are no longer present on disk
        for path, record in indexed.items():
            # Case 3: Path missing from active disk lookup -> File was deleted
            if path not in current:
                deleted.append(record)

        return SyncPlan(
            added=added,
            modified=modified,
            deleted=deleted,
        )
    

    def sync(self) -> None:
        """
        Synchronize the index with the knowledge source.
        """

        # Bootstrap the index.
        if not self.exists():
            self.build()
            return

        # Load the current index.
        self.load()

        # Detect changes.
        plan = self.detect_changes()

        # Apply additions.
        for document in plan.added:
            self._add_document(document)

        # Apply deletions.
        for indexed_file in plan.deleted:
            self._remove_document(indexed_file)

        # Apply modifications.
        for document in plan.modified:
            self._update_document(document)

        # Persist the updated index.
        self._vector_store.save()

    
    def _add_document(
        self,
        document: Document,
    ) -> None:
        """
        Index a document.
        """

        # Chunk document.
        chunks = self._chunker.chunk_document(
            document
        )

        # Empty file, return
        if len(chunks) == 0:
            return

        # Generate embeddings.
        embeddings = self._embedder.embed(
            chunks
        )

        # Allocate vector IDs.
        vector_ids = (
            self._mapping_store.allocate_vector_ids(
                len(chunks)
            )
        )

        # Store vectors.
        self._vector_store.add(
            embeddings=embeddings,
            vector_ids=vector_ids,
        )

        # Store chunks.
        self._chunk_store.add_many(
            chunks
        )

        # Store vector mappings.
        self._mapping_store.add_many(
            self._create_mappings(
                chunks,
                vector_ids,
            )
        )

        # Store file metadata.
        self._file_index_store.add(
            IndexedFile(
                source=document.source,
                content_hash=FileHasher.sha256(
                    document.source,
                ),
                embedding_model=self._embedder.model_name,
                chunk_count=len(chunks),
            )
        )

    def _create_mappings(
        self,
        chunks: list[Chunk],
        vector_ids: np.ndarray,
    ) -> list[VectorMapping]:
        """
        Create vector mappings for indexed chunks.
        """

        return [
            VectorMapping(
                chunk_id=chunk.id,
                vector_store="faiss",
                embedding_model=self._embedder.model_name,
                vector_id=int(vector_id),
            )
            for chunk, vector_id in zip(
                chunks,
                vector_ids,
                strict=True,
            )
        ]


    def _remove_document(
        self,
        indexed_file: IndexedFile,
    ) -> None:
        """
        Remove an indexed document.
        """

        # Find all chunks belonging to the document.
        chunks = self._chunk_store.get_by_source(
            indexed_file.source
        )

        # Nothing indexed.
        if not chunks:
            return

        # Find their vector mappings.
        mappings = self._mapping_store.get_by_chunks(
            [
                chunk.id
                for chunk in chunks
            ]
        )

        # Remove vectors from FAISS.
        self._vector_store.remove(
            np.array(
                [
                    mapping.vector_id
                    for mapping in mappings
                ],
                dtype=np.int64,
            )
        )

        # Remove mappings.
        self._mapping_store.delete_many(
            [
                mapping.chunk_id
                for mapping in mappings
            ]
        )

        # Remove chunks.
        self._chunk_store.delete_by_source(
            indexed_file.source
        )

        # Remove file metadata.
        self._file_index_store.delete(
            indexed_file.source
        )


    def _update_document(
        self,
        document: Document,
    ) -> None:
        """
        Re-index a modified document.
        """

        record = self._file_index_store.get(
            document.source
        )

        if record is None:
            raise RuntimeError(
                f"Indexed file not found: {document.source}"
            )

        self._remove_document(
            record
        )

        self._add_document(
            document
        )