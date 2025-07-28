"""
DREAM Business Analysis AI - RAG Engine
Retrieval-Augmented Generation engine for business knowledge base
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

# Disable ChromaDB telemetry to avoid posthog errors
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"

# Additional environment variables for cloud compatibility
os.environ["CHROMA_DB_IMPL"] = "duckdb+parquet"
os.environ["CHROMA_API_IMPL"] = "chromadb.api.segment.SegmentAPI"

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import ChromaDB dependencies, fall back if they fail
try:
    import chromadb
    from chromadb.config import Settings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
    from langchain_core.documents import Document
    CHROMADB_AVAILABLE = True
    logger.info("✅ ChromaDB dependencies loaded successfully")
except Exception as e:
    CHROMADB_AVAILABLE = False
    logger.warning(f"⚠️ ChromaDB dependencies failed to load: {e}")
    logger.info("🔄 Will use fallback TF-IDF implementation")

# Always import fallback engine for potential use
try:
    from .rag_engine_fallback import FallbackRAGEngine
except ImportError:
    # Handle relative import issues
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from rag_engine_fallback import FallbackRAGEngine

class RAGEngine:
    """RAG Engine for DREAM Business Analysis knowledge base with automatic fallback"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.embeddings = None
        self.vectorstore = None
        self.text_splitter = None
        self.knowledge_base_path = Path(__file__).parent.parent / "data"
        self.fallback_engine = None
        self.use_fallback = False
        
    async def initialize(self):
        """Initialize the RAG engine components with automatic fallback"""
        if not CHROMADB_AVAILABLE:
            logger.info("🔄 ChromaDB not available, using fallback engine")
            await self._initialize_fallback()
            return
            
        try:
            await self._initialize_chromadb()
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {e}")
            logger.info("🔄 Falling back to TF-IDF implementation")
            await self._initialize_fallback()
    
    async def _initialize_chromadb(self):
        """Initialize ChromaDB-based RAG engine"""
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.config["embedding"]["model"],
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config["embedding"]["chunk_size"],
            chunk_overlap=self.config["embedding"]["chunk_overlap"],
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )
        
        # Initialize vector store
        persist_directory = Path(__file__).parent.parent / self.config["vector_db"]["persist_directory"]
        persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Create ChromaDB client with cloud-compatible settings
        try:
            # Try with DuckDB backend for better cloud compatibility
            chroma_client = chromadb.PersistentClient(
                path=str(persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    chroma_db_impl="duckdb+parquet",
                    chroma_api_impl="chromadb.api.segment.SegmentAPI"
                )
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to create DuckDB client, trying SQLite: {e}")
            # Fallback to SQLite with minimal settings
            try:
                chroma_client = chromadb.PersistentClient(
                    path=str(persist_directory),
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                        is_persistent=True
                    )
                )
            except Exception as e2:
                logger.warning(f"⚠️ SQLite client also failed, using in-memory: {e2}")
                # Last resort: in-memory client
                chroma_client = chromadb.Client(
                    settings=Settings(
                        anonymized_telemetry=False,
                        chroma_db_impl="duckdb",
                        chroma_api_impl="chromadb.api.segment.SegmentAPI"
                    )
                )
        
        self.vectorstore = Chroma(
            collection_name=self.config["vector_db"]["collection_name"],
            embedding_function=self.embeddings,
            persist_directory=str(persist_directory),
            client=chroma_client
        )
        
        # Load knowledge base if vector store is empty
        try:
            collection_count = self.vectorstore._collection.count()
            if collection_count == 0:
                await self.load_knowledge_base()
        except Exception as count_error:
            logger.warning(f"⚠️ Could not check collection count: {count_error}")
            # Try to load knowledge base anyway
            await self.load_knowledge_base()
        
        logger.info("✅ ChromaDB RAG Engine initialized successfully")
    
    async def _initialize_fallback(self):
        """Initialize fallback TF-IDF engine"""
        self.use_fallback = True
        self.fallback_engine = FallbackRAGEngine(self.config)
        await self.fallback_engine.initialize()
        logger.info("✅ Fallback RAG Engine initialized successfully")
    
    async def load_knowledge_base(self):
        """Load business knowledge base into vector store"""
        if self.use_fallback:
            # Fallback engine handles its own knowledge base loading
            logger.info("📚 Knowledge base loading handled by fallback engine")
            return
            
        try:
            documents = []
            
            # Load frameworks
            frameworks_path = self.knowledge_base_path / "frameworks"
            if frameworks_path.exists():
                documents.extend(await self._load_documents_from_directory(frameworks_path, "framework"))
            
            # Load case studies
            case_studies_path = self.knowledge_base_path / "case_studies"
            if case_studies_path.exists():
                documents.extend(await self._load_documents_from_directory(case_studies_path, "case_study"))
            
            # Load templates
            templates_path = self.knowledge_base_path / "templates"
            if templates_path.exists():
                documents.extend(await self._load_documents_from_directory(templates_path, "template"))
            
            # Load benchmarks
            benchmarks_path = self.knowledge_base_path / "benchmarks"
            if benchmarks_path.exists():
                documents.extend(await self._load_documents_from_directory(benchmarks_path, "benchmark"))
            
            if documents:
                # Split documents into chunks
                chunks = self.text_splitter.split_documents(documents)
                
                # Add to vector store
                self.vectorstore.add_documents(chunks)
                logger.info(f"✅ Loaded {len(chunks)} document chunks into knowledge base")
            else:
                logger.warning("⚠️ No documents found in knowledge base directories")
                
        except Exception as e:
            logger.error(f"❌ Failed to load knowledge base: {e}")
            raise
    
    async def _load_documents_from_directory(self, directory: Path, doc_type: str) -> List:
        """Load documents from a specific directory"""
        if not CHROMADB_AVAILABLE:
            # This method should not be called when using fallback
            logger.error("❌ _load_documents_from_directory called without ChromaDB dependencies")
            return []
            
        documents = []
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.md', '.txt']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(file_path),
                            "type": doc_type,
                            "filename": file_path.name
                        }
                    )
                    documents.append(doc)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {file_path}: {e}")
        
        return documents
    
    async def search_knowledge(self, query: str, k: int = 5, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant information"""
        if self.use_fallback:
            return await self.fallback_engine.search_knowledge(query, k, filter_type)
            
        try:
            # Prepare search filter
            where_filter = None
            if filter_type:
                where_filter = {"type": filter_type}
            
            # Perform similarity search
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=where_filter
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": float(score)
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Knowledge search failed: {e}")
            return []
    
    async def get_dream_framework_context(self, component: str) -> str:
        """Get specific DREAM framework component context"""
        if self.use_fallback:
            return await self.fallback_engine.get_dream_framework_context(component)
            
        component_queries = {
            "demand": "需求分析 目标用户 市场规模 用户验证",
            "resolution": "解决方案 价值主张 产品内核 最小可行产品",
            "earning": "商业模式 单位经济学 盈利能力 财务模型",
            "acquisition": "增长策略 客户获取 AARRR漏斗 规模化",
            "moat": "竞争优势 壁垒 护城河 可防御性"
        }
        
        query = component_queries.get(component.lower(), component)
        results = await self.search_knowledge(query, k=3, filter_type="framework")
        
        context = ""
        for result in results:
            context += f"{result['content']}\n\n"
        
        return context.strip()
    
    async def get_hypothesis_validation_context(self) -> str:
        """Get context for hypothesis validation methodology"""
        if self.use_fallback:
            return await self.fallback_engine.get_hypothesis_validation_context()
            
        results = await self.search_knowledge("假设验证 关键假设 验证方法", k=3)
        
        context = ""
        for result in results:
            context += f"{result['content']}\n\n"
        
        return context.strip()
    
    async def get_industry_benchmarks(self, industry: str) -> List[Dict[str, Any]]:
        """Get industry-specific benchmarks and metrics"""
        if self.use_fallback:
            return await self.fallback_engine.get_industry_benchmarks(industry)
            
        query = f"{industry} 行业基准 指标 数据"
        results = await self.search_knowledge(query, k=5, filter_type="benchmark")
        return results
    
    async def rebuild_knowledge_base(self):
        """Rebuild the entire knowledge base"""
        if self.use_fallback:
            return await self.fallback_engine.rebuild_knowledge_base()
            
        try:
            # Clear existing collection by deleting and recreating it
            collection_name = self.config["vector_db"]["collection_name"]
            
            # Get all document IDs first
            try:
                existing_docs = self.vectorstore._collection.get()
                if existing_docs and 'ids' in existing_docs and existing_docs['ids']:
                    # Delete all existing documents
                    self.vectorstore._collection.delete(ids=existing_docs['ids'])
                    logger.info(f"✅ Cleared {len(existing_docs['ids'])} existing documents")
            except Exception as delete_error:
                logger.warning(f"⚠️ Could not clear existing documents: {delete_error}")
                # If deletion fails, try to recreate the collection
                try:
                    self.vectorstore._client.delete_collection(collection_name)
                    logger.info("✅ Deleted existing collection")
                except Exception as recreate_error:
                    logger.warning(f"⚠️ Could not delete collection: {recreate_error}")
                
                # Reinitialize vectorstore
                persist_directory = Path(__file__).parent.parent / self.config["vector_db"]["persist_directory"]
                
                # Create ChromaDB client with cloud-compatible settings
                try:
                    chroma_client = chromadb.PersistentClient(
                        path=str(persist_directory),
                        settings=Settings(
                            anonymized_telemetry=False,
                            chroma_db_impl="duckdb+parquet",
                            chroma_api_impl="chromadb.api.segment.SegmentAPI"
                        )
                    )
                except Exception:
                    # Fallback to basic settings
                    chroma_client = chromadb.PersistentClient(
                        path=str(persist_directory),
                        settings=Settings(
                            anonymized_telemetry=False,
                            allow_reset=True,
                            is_persistent=True
                        )
                    )
                
                self.vectorstore = Chroma(
                    collection_name=collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=str(persist_directory),
                    client=chroma_client
                )
            
            # Reload knowledge base
            await self.load_knowledge_base()
            
            logger.info("✅ Knowledge base rebuilt successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to rebuild knowledge base: {e}")
            raise