"""
RAG (Retrieval-Augmented Generation) Mixin for SuperOptiX Pipelines

This mixin provides RAG capabilities to DSPy pipelines, supporting:
- ChromaDB, LanceDB, FAISS, Weaviate, Qdrant, Milvus, Pinecone
- Automatic document ingestion and chunking
- Semantic search and retrieval
- Integration with DSPy ReAct agents
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

try:
    import dspy  # noqa: F401
    from dspy.retrieve import Retrieve  # noqa: F401

    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False

# Vector database imports with graceful fallbacks
try:
    import chromadb  # noqa: F401

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import lancedb  # noqa: F401

    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False

try:
    import faiss  # noqa: F401

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import weaviate  # noqa: F401

    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

try:
    import qdrant_client  # noqa: F401

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

try:
    import pymilvus  # noqa: F401

    MILVUS_AVAILABLE = True
except ImportError:
    MILVUS_AVAILABLE = False

try:
    import pinecone  # noqa: F401

    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

logger = logging.getLogger(__name__)


class RAGMixin:
    """Mixin providing RAG capabilities to SuperOptiX pipelines."""

    def setup_rag(self, spec_data: Dict[str, Any]) -> bool:
        """Setup RAG system based on playbook configuration."""
        try:
            # Check if RAG is enabled
            rag_config = spec_data.get("rag", {})
            retrieval_config = spec_data.get("retrieval", {})

            # Support both 'rag' and 'retrieval' keys for backward compatibility
            if not rag_config and not retrieval_config:
                logger.info("ℹ️ RAG not configured - skipping setup")
                return False

            config = rag_config or retrieval_config

            if not config.get("enabled", True):
                logger.info("ℹ️ RAG disabled in configuration")
                return False

            # Get retriever type for better error messages
            retriever_type = config.get(
                "retriever_type", config.get("vector_database", "chroma")
            ).lower()

            # Setup vector database
            self.vector_db = self._setup_vector_database(config)
            if not self.vector_db:
                logger.warning(
                    f"⚠️ Failed to setup vector database for {retriever_type}"
                )
                return False

            # Setup document processor
            self.doc_processor = self._setup_document_processor(config)

            logger.info(f"✅ RAG system initialized with {retriever_type}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to setup RAG: {e}")
            return False

    def _setup_vector_database(self, config: Dict[str, Any]):
        """Setup vector database based on configuration."""
        # Support both 'retriever_type' and 'vector_database' keys for backward compatibility
        retriever_type = config.get(
            "retriever_type", config.get("vector_database", "chroma")
        ).lower()

        # Normalize retriever type names for consistency
        if retriever_type in ["chroma", "chromadb"]:
            retriever_type = "chroma"
        elif retriever_type in ["lancedb", "lance"]:
            retriever_type = "lancedb"

        # Support both nested vector_store and direct config
        vector_store = config.get("vector_store", {})
        if not vector_store:
            # If no nested vector_store, use the config directly
            vector_store = config

        try:
            if retriever_type == "chroma":
                if not CHROMADB_AVAILABLE:
                    self._print_dependency_help("chromadb", "ChromaDB")
                    return None
                return self._setup_chromadb(vector_store)
            elif retriever_type == "lancedb":
                if not LANCEDB_AVAILABLE:
                    self._print_dependency_help("lancedb", "LanceDB")
                    return None
                return self._setup_lancedb(vector_store)
            elif retriever_type == "faiss":
                if not FAISS_AVAILABLE:
                    self._print_dependency_help("faiss-cpu", "FAISS")
                    return None
                return self._setup_faiss(vector_store)
            elif retriever_type == "weaviate":
                if not WEAVIATE_AVAILABLE:
                    self._print_dependency_help("weaviate-client", "Weaviate")
                    return None
                return self._setup_weaviate(vector_store)
            elif retriever_type == "qdrant":
                if not QDRANT_AVAILABLE:
                    self._print_dependency_help("qdrant-client", "Qdrant")
                    return None
                return self._setup_qdrant(vector_store)
            elif retriever_type == "milvus":
                if not MILVUS_AVAILABLE:
                    self._print_dependency_help("pymilvus", "Milvus")
                    return None
                return self._setup_milvus(vector_store)
            elif retriever_type == "pinecone":
                if not PINECONE_AVAILABLE:
                    self._print_dependency_help("pinecone-client", "Pinecone")
                    return None
                return self._setup_pinecone(vector_store)
            else:
                logger.error(f"❌ Unsupported retriever type: {retriever_type}")
                logger.error(
                    "Supported types: chroma, lancedb, faiss, weaviate, qdrant, milvus, pinecone"
                )
                return None

        except Exception as e:
            logger.error(f"❌ Failed to setup vector database {retriever_type}: {e}")
            return None

    def _print_dependency_help(self, package_name: str, db_name: str):
        """Print helpful installation instructions for missing dependencies."""
        print(f"\n❌ {db_name} is not installed!")
        print(f"🔧 To enable RAG with {db_name}, install the required dependencies:")
        print("")
        print("   # Option 1: Install specific package")
        print(f"   pip install {package_name} sentence-transformers")
        print("")
        print("   # Option 2: Install via SuperOptiX extras")
        print(f"   pip install superoptix[{package_name.replace('-', '')}]")
        print("")
        print("   # Option 3: Install all vector databases")
        print("   pip install superoptix[vectordb]")
        print("")
        print(
            "📚 For more information, see: https://superoptix.readthedocs.io/rag-setup"
        )
        print("")

    def _setup_chromadb(self, config: Dict[str, Any]):
        """Setup ChromaDB vector database."""
        try:
            import chromadb
            from chromadb.config import Settings

            collection_name = config.get("collection_name", "default_collection")
            persist_directory = config.get("persist_directory", ".superoptix/chromadb")

            # Create client
            client = chromadb.PersistentClient(
                path=persist_directory, settings=Settings(anonymized_telemetry=False)
            )

            # Get or create collection
            collection = client.get_or_create_collection(
                name=collection_name, metadata={"hnsw:space": "cosine"}
            )

            return {
                "type": "chromadb",
                "client": client,
                "collection": collection,
                "config": config,
            }

        except Exception as e:
            logger.error(f"ChromaDB setup failed: {e}")
            return None

    def _setup_lancedb(self, config: Dict[str, Any]):
        """Setup LanceDB vector database."""
        try:
            import lancedb

            db_path = config.get("db_path", ".superoptix/lancedb")
            collection_name = config.get("collection_name", "default_collection")

            # Create database
            db = lancedb.connect(db_path)

            # Get or create table
            try:
                table = db.open_table(collection_name)
            except FileNotFoundError:
                # Create table with schema
                schema = {
                    "id": "string",
                    "text": "string",
                    "embedding": "float32[384]",  # Default embedding size
                    "metadata": "json",
                }
                table = db.create_table(collection_name, schema=schema)

            return {"type": "lancedb", "db": db, "table": table, "config": config}

        except Exception as e:
            logger.error(f"LanceDB setup failed: {e}")
            return None

    def _setup_faiss(self, config: Dict[str, Any]):
        """Setup FAISS vector database."""
        try:
            import faiss

            db_path = config.get("db_path", ".superoptix/faiss")
            index_path = Path(db_path) / "faiss.index"

            # Create directory
            Path(db_path).mkdir(parents=True, exist_ok=True)

            # Load or create index
            if index_path.exists():
                index = faiss.read_index(str(index_path))
            else:
                # Create new index
                dimension = config.get("embedding_dimension", 384)
                index = faiss.IndexFlatIP(
                    dimension
                )  # Inner product for cosine similarity

            return {
                "type": "faiss",
                "index": index,
                "index_path": index_path,
                "config": config,
            }

        except Exception as e:
            logger.error(f"FAISS setup failed: {e}")
            return None

    def _setup_weaviate(self, config: Dict[str, Any]):
        """Setup Weaviate vector database."""
        try:
            import weaviate

            url = config.get("url", "http://localhost:8080")
            collection_name = config.get("collection_name", "Documents")

            # Create client
            client = weaviate.Client(url)

            # Check if collection exists
            if not client.schema.exists(collection_name):
                # Create collection schema
                schema = {
                    "class": collection_name,
                    "properties": [
                        {"name": "content", "dataType": ["text"]},
                        {"name": "metadata", "dataType": ["text"]},
                    ],
                    "vectorizer": "text2vec-transformers",
                }
                client.schema.create_class(schema)

            return {
                "type": "weaviate",
                "client": client,
                "collection_name": collection_name,
                "config": config,
            }

        except Exception as e:
            logger.error(f"Weaviate setup failed: {e}")
            return None

    def _setup_qdrant(self, config: Dict[str, Any]):
        """Setup Qdrant vector database."""
        try:
            import qdrant_client
            from qdrant_client.models import Distance, VectorParams

            url = config.get("url", "http://localhost:6333")
            collection_name = config.get("collection_name", "knowledge_base")

            # Create client
            client = qdrant_client.QdrantClient(url=url)

            # Check if collection exists
            collections = client.get_collections()
            if collection_name not in [c.name for c in collections.collections]:
                # Create collection
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )

            return {
                "type": "qdrant",
                "client": client,
                "collection_name": collection_name,
                "config": config,
            }

        except Exception as e:
            logger.error(f"Qdrant setup failed: {e}")
            return None

    def _setup_milvus(self, config: Dict[str, Any]):
        """Setup Milvus vector database."""
        try:
            from pymilvus import (
                connections,
                Collection,
                FieldSchema,
                CollectionSchema,
                DataType,
                utility,
            )

            host = config.get("host", "localhost")
            port = config.get("port", "19530")
            collection_name = config.get("collection_name", "knowledge_base")

            # Connect to Milvus
            connections.connect(host=host, port=port)

            # Check if collection exists
            if not utility.has_collection(collection_name):
                # Create collection schema
                fields = [
                    FieldSchema(
                        name="id", dtype=DataType.INT64, is_primary=True, auto_id=True
                    ),
                    FieldSchema(
                        name="content", dtype=DataType.VARCHAR, max_length=65535
                    ),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
                ]
                schema = CollectionSchema(
                    fields=fields, description="Knowledge base collection"
                )
                collection = Collection(name=collection_name, schema=schema)

                # Create index
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 1024},
                }
                collection.create_index(
                    field_name="embedding", index_params=index_params
                )
            else:
                collection = Collection(collection_name)

            return {
                "type": "milvus",
                "collection": collection,
                "collection_name": collection_name,
                "config": config,
            }

        except Exception as e:
            logger.error(f"Milvus setup failed: {e}")
            return None

    def _setup_pinecone(self, config: Dict[str, Any]):
        """Setup Pinecone vector database."""
        try:
            import pinecone

            api_key = config.get("api_key")
            environment = config.get("environment")
            index_name = config.get("collection_name", "knowledge-base")

            if not api_key or not environment:
                logger.error("Pinecone requires api_key and environment")
                return None

            # Initialize Pinecone
            pinecone.init(api_key=api_key, environment=environment)

            # Check if index exists
            if index_name not in pinecone.list_indexes():
                # Create index
                pinecone.create_index(name=index_name, dimension=384, metric="cosine")

            # Get index
            index = pinecone.Index(index_name)

            return {
                "type": "pinecone",
                "index": index,
                "index_name": index_name,
                "config": config,
            }

        except Exception as e:
            logger.error(f"Pinecone setup failed: {e}")
            return None

    def _setup_dspy_retriever(self, config: Dict[str, Any]):
        """Setup DSPy retriever."""
        if not DSPY_AVAILABLE:
            logger.error("DSPy not available for retriever setup")
            return None

        try:
            top_k = config.get("config", {}).get("top_k", 5)

            # Create a custom retriever that works with our vector database
            class CustomRetriever:
                def __init__(self, vector_db, k=5):
                    self.vector_db = vector_db
                    self.k = k

                def __call__(self, query, k=None):
                    k = k if k is not None else self.k
                    # This will be called by DSPy's Retrieve class
                    # We'll implement the actual retrieval in our mixin methods
                    return self.forward(query, k)

                def forward(self, query, k=None):
                    k = k if k is not None else self.k
                    # Return a list of dotdict objects with long_text attribute
                    # This matches what DSPy expects
                    from dspy.dsp.utils import dotdict

                    # For now, return empty results - actual retrieval will be done in our mixin
                    return [dotdict({"long_text": ""})]

            # Create custom retriever
            retriever = CustomRetriever(self.vector_db, top_k)

            return retriever

        except Exception as e:
            logger.error(f"Failed to setup DSPy retriever: {e}")
            return None

    def _setup_document_processor(self, config: Dict[str, Any]):
        """Setup document processor for chunking and embedding."""
        try:
            chunk_size = config.get("config", {}).get("chunk_size", 512)
            chunk_overlap = config.get("config", {}).get("chunk_overlap", 50)
            embedding_model = config.get("vector_store", {}).get(
                "embedding_model", "all-MiniLM-L6-v2"
            )

            return {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "embedding_model": embedding_model,
            }

        except Exception as e:
            logger.error(f"Failed to setup document processor: {e}")
            return None

    async def retrieve_context(self, query: str, top_k: int = None) -> List[str]:
        """Retrieve relevant context for a query."""
        try:
            if not self.vector_db:
                logger.warning("No vector database available")
                return []

            # Use configured top_k or default
            if top_k is None:
                top_k = (
                    self.vector_db.get("config", {}).get("config", {}).get("top_k", 5)
                )

            # Retrieve documents directly from vector database
            return await self._query_vector_db(query, top_k)

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []

    async def _query_vector_db(self, query: str, top_k: int) -> List[str]:
        """Query vector database directly."""
        try:
            if not self.vector_db:
                return []

            db_type = self.vector_db["type"]

            if db_type == "chromadb":
                return await self._query_chromadb(query, top_k)
            elif db_type == "lancedb":
                return await self._query_lancedb(query, top_k)
            elif db_type == "faiss":
                return await self._query_faiss(query, top_k)
            elif db_type == "weaviate":
                return await self._query_weaviate(query, top_k)
            elif db_type == "qdrant":
                return await self._query_qdrant(query, top_k)
            elif db_type == "milvus":
                return await self._query_milvus(query, top_k)
            elif db_type == "pinecone":
                return await self._query_pinecone(query, top_k)
            else:
                logger.warning(f"Unknown vector database type: {db_type}")
                return []

        except Exception as e:
            logger.error(f"Vector database query failed: {e}")
            return []

    async def _query_chromadb(self, query: str, top_k: int) -> List[str]:
        """Query ChromaDB."""
        try:
            collection = self.vector_db["collection"]
            results = collection.query(query_texts=[query], n_results=top_k)
            return results["documents"][0] if results["documents"] else []
        except Exception as e:
            logger.error(f"ChromaDB query failed: {e}")
            return []

    async def _query_lancedb(self, query: str, top_k: int) -> List[str]:
        """Query LanceDB."""
        try:
            table = self.vector_db["table"]
            # LanceDB query implementation
            # This is a simplified version - actual implementation would need embedding
            results = table.search(query).limit(top_k).to_list()
            return [r["text"] for r in results]
        except Exception as e:
            logger.error(f"LanceDB query failed: {e}")
            return []

    async def _query_faiss(self, query: str, top_k: int) -> List[str]:
        """Query FAISS."""
        try:
            # FAISS query implementation
            # This would require embedding the query and searching the index
            logger.warning("FAISS query not fully implemented")
            return []
        except Exception as e:
            logger.error(f"FAISS query failed: {e}")
            return []

    async def _query_weaviate(self, query: str, top_k: int) -> List[str]:
        """Query Weaviate."""
        try:
            client = self.vector_db["client"]
            collection_name = self.vector_db["collection_name"]

            results = (
                client.query.get(collection_name, ["content"])
                .with_near_text({"concepts": [query]})
                .with_limit(top_k)
                .do()
            )

            return [r["content"] for r in results["data"]["Get"][collection_name]]
        except Exception as e:
            logger.error(f"Weaviate query failed: {e}")
            return []

    async def _query_qdrant(self, query: str, top_k: int) -> List[str]:
        """Query Qdrant."""
        try:
            _ = self.vector_db["client"]  # noqa: F841
            _ = self.vector_db["collection_name"]  # noqa: F841

            # This would require embedding the query first
            logger.warning("Qdrant query not fully implemented")
            return []
        except Exception as e:
            logger.error(f"Qdrant query failed: {e}")
            return []

    async def _query_milvus(self, query: str, top_k: int) -> List[str]:
        """Query Milvus."""
        try:
            _ = self.vector_db["collection"]  # noqa: F841
            # Milvus query implementation
            logger.warning("Milvus query not fully implemented")
            return []
        except Exception as e:
            logger.error(f"Milvus query failed: {e}")
            return []

    async def _query_pinecone(self, query: str, top_k: int) -> List[str]:
        """Query Pinecone."""
        try:
            _ = self.vector_db["index"]  # noqa: F841
            # Pinecone query implementation
            logger.warning("Pinecone query not fully implemented")
            return []
        except Exception as e:
            logger.error(f"Pinecone query failed: {e}")
            return []

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector database."""
        try:
            if not self.vector_db:
                logger.warning("No vector database available")
                return False

            db_type = self.vector_db["type"]

            if db_type == "chromadb":
                return self._add_documents_chromadb(documents)
            elif db_type == "lancedb":
                return self._add_documents_lancedb(documents)
            elif db_type == "faiss":
                return self._add_documents_faiss(documents)
            elif db_type == "weaviate":
                return self._add_documents_weaviate(documents)
            elif db_type == "qdrant":
                return self._add_documents_qdrant(documents)
            elif db_type == "milvus":
                return self._add_documents_milvus(documents)
            elif db_type == "pinecone":
                return self._add_documents_pinecone(documents)
            else:
                logger.warning(f"Unknown vector database type: {db_type}")
                return False

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False

    def _add_documents_chromadb(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to ChromaDB."""
        try:
            collection = self.vector_db["collection"]

            texts = [doc["content"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            ids = [doc.get("id", f"doc_{i}") for i, doc in enumerate(documents)]

            collection.add(documents=texts, metadatas=metadatas, ids=ids)

            logger.info(f"Added {len(documents)} documents to ChromaDB")
            return True

        except Exception as e:
            logger.error(f"ChromaDB add documents failed: {e}")
            return False

    def _add_documents_lancedb(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to LanceDB."""
        try:
            table = self.vector_db["table"]

            # Convert documents to LanceDB format
            data = []
            for doc in documents:
                data.append(
                    {
                        "id": doc.get("id", f"doc_{len(data)}"),
                        "text": doc["content"],
                        "metadata": doc.get("metadata", {}),
                    }
                )

            table.add(data)

            logger.info(f"Added {len(documents)} documents to LanceDB")
            return True

        except Exception as e:
            logger.error(f"LanceDB add documents failed: {e}")
            return False

    def _add_documents_faiss(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to FAISS."""
        try:
            # FAISS add documents implementation
            logger.warning("FAISS add documents not fully implemented")
            return False
        except Exception as e:
            logger.error(f"FAISS add documents failed: {e}")
            return False

    def _add_documents_weaviate(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to Weaviate."""
        try:
            client = self.vector_db["client"]
            collection_name = self.vector_db["collection_name"]

            # Add documents to Weaviate
            for doc in documents:
                client.data_object.create(
                    data_object={
                        "content": doc["content"],
                        "metadata": doc.get("metadata", {}),
                    },
                    class_name=collection_name,
                )

            logger.info(f"Added {len(documents)} documents to Weaviate")
            return True

        except Exception as e:
            logger.error(f"Weaviate add documents failed: {e}")
            return False

    def _add_documents_qdrant(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to Qdrant."""
        try:
            # Qdrant add documents implementation
            logger.warning("Qdrant add documents not fully implemented")
            return False
        except Exception as e:
            logger.error(f"Qdrant add documents failed: {e}")
            return False

    def _add_documents_milvus(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to Milvus."""
        try:
            # Milvus add documents implementation
            logger.warning("Milvus add documents not fully implemented")
            return False
        except Exception as e:
            logger.error(f"Milvus add documents failed: {e}")
            return False

    def _add_documents_pinecone(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to Pinecone."""
        try:
            # Pinecone add documents implementation
            logger.warning("Pinecone add documents not fully implemented")
            return False
        except Exception as e:
            logger.error(f"Pinecone add documents failed: {e}")
            return False

    def get_rag_status(self) -> Dict[str, Any]:
        """Get RAG system status."""
        try:
            if not hasattr(self, "vector_db") or not self.vector_db:
                return {
                    "enabled": False,
                    "reason": "Vector database not initialized",
                    "vector_db_type": None,
                    "document_count": 0,
                    "setup_required": True,
                }

            db_type = self.vector_db["type"]
            document_count = 0

            # Try to get document count based on database type
            try:
                if db_type == "chromadb":
                    collection = self.vector_db["collection"]
                    document_count = collection.count()
                elif db_type == "lancedb":
                    table = self.vector_db["table"]
                    document_count = len(table)
                # Add other database types as needed
            except Exception:
                document_count = "unknown"

            return {
                "enabled": True,
                "vector_db_type": db_type,
                "document_count": document_count,
                "config": self.vector_db.get("config", {}),
                "setup_required": False,
                "doc_processor_available": hasattr(self, "doc_processor")
                and self.doc_processor is not None,
            }

        except Exception as e:
            return {
                "enabled": False,
                "reason": f"Error getting status: {str(e)}",
                "vector_db_type": None,
                "document_count": 0,
                "setup_required": True,
            }
