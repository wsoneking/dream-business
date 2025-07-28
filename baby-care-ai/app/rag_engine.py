"""
Baby Care AI - RAG Engine with ChromaDB Fallback
Retrieval-Augmented Generation engine for baby care knowledge base
"""

import os
import yaml
from typing import List, Dict, Any
from pathlib import Path

# Disable ChromaDB telemetry to avoid posthog errors
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import ChromaDB dependencies, fall back if they fail
try:
    import chromadb
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import DirectoryLoader, TextLoader
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_core.documents import Document
    from langchain_core.retrievers import BaseRetriever
    CHROMADB_AVAILABLE = True
    logger.info("✅ ChromaDB dependencies loaded successfully")
except Exception as e:
    CHROMADB_AVAILABLE = False
    logger.warning(f"⚠️ ChromaDB dependencies failed to load: {e}")
    logger.info("🔄 Will use fallback TF-IDF implementation")
    # Create a mock BaseRetriever for fallback
    class BaseRetriever:
        pass
    # Create mock Document class
    class Document:
        def __init__(self, page_content="", metadata=None):
            self.page_content = page_content
            self.metadata = metadata or {}

# Fallback engine removed - ChromaDB is now working properly

# FallbackRetriever removed - ChromaDB is now working properly

class ChromaDBWrapper:
    """Custom ChromaDB wrapper to bypass LangChain deprecated configuration"""
    
    def __init__(self, client, collection, embedding_function):
        self.client = client
        self.collection = collection
        self.embedding_function = embedding_function
    
    def add_documents(self, documents):
        """Add documents to the collection"""
        if not documents:
            logger.warning("No documents to add")
            return
            
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Generate unique IDs to avoid conflicts
        import time
        timestamp = int(time.time() * 1000)
        ids = [f"doc_{timestamp}_{i}" for i in range(len(documents))]
        
        try:
            # Generate embeddings
            embeddings = self.embedding_function.embed_documents(texts)
            
            # Add to collection in batches to avoid memory issues
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_end = min(i + batch_size, len(documents))
                batch_embeddings = embeddings[i:batch_end]
                batch_texts = texts[i:batch_end]
                batch_metadatas = metadatas[i:batch_end]
                batch_ids = ids[i:batch_end]
                
                self.collection.add(
                    embeddings=batch_embeddings,
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                logger.info(f"Added batch {i//batch_size + 1}: {len(batch_texts)} documents")
                
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def similarity_search(self, query, k=4):
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_function.embed_query(query)
            
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(k, 10)  # Limit to reasonable number
            )
            
            # Convert results to Document objects
            documents = []
            if results and 'documents' in results and results['documents'] and results['documents'][0]:
                for i, doc_text in enumerate(results['documents'][0]):
                    metadata = {}
                    if results.get('metadatas') and results['metadatas'][0] and i < len(results['metadatas'][0]):
                        metadata = results['metadatas'][0][i] or {}
                    
                    if CHROMADB_AVAILABLE:
                        doc = Document(page_content=doc_text, metadata=metadata)
                    else:
                        doc = type('Document', (), {
                            'page_content': doc_text,
                            'metadata': metadata
                        })()
                    documents.append(doc)
            
            logger.info(f"Found {len(documents)} similar documents for query")
            return documents
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def as_retriever(self, search_type="similarity", search_kwargs=None):
        """Return a retriever interface"""
        if search_kwargs is None:
            search_kwargs = {"k": 4}
        return ChromaDBRetriever(self, search_kwargs.get("k", 4))

class ChromaDBRetriever:
    """Custom retriever for ChromaDB wrapper"""
    
    def __init__(self, vectorstore, k=4):
        self.vectorstore = vectorstore
        self.k = k
        self.search_type = "similarity"
        self.search_kwargs = {"k": k}
    
    def get_relevant_documents(self, query):
        """Get relevant documents for a query"""
        return self.vectorstore.similarity_search(query, k=self.k)
    
    def invoke(self, query):
        """Invoke method for compatibility"""
        return self.get_relevant_documents(query)

class RAGEngine:
    """RAG Engine for Baby Care AI knowledge base with automatic fallback"""
    
    def __init__(self, config_path: str = None):
        """初始化RAG引擎"""
        if config_path is None:
            # Get the project root directory (parent of app directory)
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "ollama_config.yaml"
        self.config = self._load_config(str(config_path))
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        self._setup_embeddings()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def _setup_embeddings(self):
        """设置嵌入模型"""
        if not CHROMADB_AVAILABLE:
            logger.info("🔄 ChromaDB not available, skipping embeddings setup")
            return
            
        try:
            model_name = self.config['embedding']['model']
            self.embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info("✅ Embeddings model initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to setup embeddings: {e}")
            logger.info("🔄 Will use fallback implementation")
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB-based RAG engine"""
        try:
            # Initialize vector store
            persist_directory = self.config['vector_db']['persist_directory']
            collection_name = self.config['vector_db']['collection_name']
            
            # Ensure directory exists
            os.makedirs(persist_directory, exist_ok=True)
            
            # Create ChromaDB persistent client to save to disk
            try:
                # Use PersistentClient to save data to disk
                self.chroma_client = chromadb.PersistentClient(path=persist_directory)
                logger.info(f"✅ ChromaDB PersistentClient created successfully at {persist_directory}")
                
                # Get or create collection with error handling
                try:
                    self.collection = self.chroma_client.get_collection(name=collection_name)
                    logger.info(f"✅ Retrieved existing collection: {collection_name}")
                except Exception as get_error:
                    logger.info(f"Collection doesn't exist, creating new one: {get_error}")
                    try:
                        self.collection = self.chroma_client.create_collection(
                            name=collection_name,
                            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
                        )
                        logger.info(f"✅ Created new collection: {collection_name}")
                    except Exception as create_error:
                        logger.warning(f"Failed to create collection with metadata, trying simple creation: {create_error}")
                        self.collection = self.chroma_client.create_collection(name=collection_name)
                        logger.info(f"✅ Created new collection (simple): {collection_name}")
                
                # Create a custom vectorstore wrapper
                self.vectorstore = ChromaDBWrapper(
                    client=self.chroma_client,
                    collection=self.collection,
                    embedding_function=self.embeddings
                )
                
                logger.info("✅ ChromaDB RAG Engine initialized successfully")
                
            except Exception as e:
                logger.error(f"❌ ChromaDB PersistentClient initialization failed: {e}")
                # Fallback to in-memory client if persistent fails
                logger.info("🔄 Falling back to in-memory ChromaDB client")
                try:
                    self.chroma_client = chromadb.Client()
                    logger.info("✅ ChromaDB in-memory Client created successfully")
                    
                    # Get or create collection
                    try:
                        self.collection = self.chroma_client.get_collection(name=collection_name)
                        logger.info(f"✅ Retrieved existing collection: {collection_name}")
                    except:
                        self.collection = self.chroma_client.create_collection(name=collection_name)
                        logger.info(f"✅ Created new collection: {collection_name}")
                    
                    # Create a custom vectorstore wrapper
                    self.vectorstore = ChromaDBWrapper(
                        client=self.chroma_client,
                        collection=self.collection,
                        embedding_function=self.embeddings
                    )
                    
                    logger.info("✅ ChromaDB RAG Engine initialized successfully (in-memory)")
                except Exception as fallback_error:
                    logger.error(f"❌ Even in-memory ChromaDB failed: {fallback_error}")
                    raise
            
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {e}")
            raise
    
    def _initialize_fallback(self):
        """Fallback initialization removed - ChromaDB is now working properly"""
        logger.error("❌ ChromaDB initialization failed and fallback has been removed")
        raise RuntimeError("ChromaDB initialization failed and no fallback available")
    
    def load_documents(self, data_dirs: List[str]) -> List:
        """加载文档"""
        if not CHROMADB_AVAILABLE:
            logger.error("❌ load_documents called without ChromaDB dependencies")
            return []
            
        documents = []
        
        for data_dir in data_dirs:
            if not os.path.exists(data_dir):
                print(f"警告: 目录 {data_dir} 不存在")
                continue
                
            # 加载markdown文件
            if any(Path(data_dir).glob("*.md")):
                md_loader = DirectoryLoader(
                    data_dir,
                    glob="*.md",
                    loader_cls=TextLoader,
                    loader_kwargs={'encoding': 'utf-8'}
                )
                documents.extend(md_loader.load())
            
            # 加载txt文件
            if any(Path(data_dir).glob("*.txt")):
                txt_loader = DirectoryLoader(
                    data_dir,
                    glob="*.txt",
                    loader_cls=TextLoader,
                    loader_kwargs={'encoding': 'utf-8'}
                )
                documents.extend(txt_loader.load())
        
        print(f"成功加载 {len(documents)} 个文档")
        return documents
    
    def split_documents(self, documents: List) -> List:
        """分割文档"""
        if not CHROMADB_AVAILABLE:
            logger.error("❌ split_documents called without ChromaDB dependencies")
            return []
            
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config['embedding']['chunk_size'],
            chunk_overlap=self.config['embedding']['chunk_overlap'],
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(documents)
        print(f"文档分割完成，共 {len(split_docs)} 个片段")
        return split_docs
    
    def create_vectorstore(self, documents: List):
        """创建向量数据库"""
        # Add documents to the existing vectorstore
        if hasattr(self, 'vectorstore') and self.vectorstore:
            self.vectorstore.add_documents(documents)
            print(f"向量数据库创建完成，添加了 {len(documents)} 个文档")
        else:
            logger.error("❌ Vectorstore not initialized")
    
    def load_vectorstore(self):
        """加载已存在的向量数据库"""
        # The vectorstore is already initialized in _initialize_chromadb
        if hasattr(self, 'vectorstore') and self.vectorstore:
            print("向量数据库加载成功")
        else:
            print("向量数据库不存在，需要先创建")
    
    def setup_retriever(self, k: int = 4):
        """设置检索器"""
        if self.vectorstore is None:
            raise ValueError("向量数据库未初始化")
        
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        print(f"检索器设置完成，返回top-{k}相关文档")
    
    def retrieve_documents(self, query: str) -> List:
        """检索相关文档"""
        if self.retriever is None:
            raise ValueError("检索器未初始化")
        
        relevant_docs = self.retriever.invoke(query)
        return relevant_docs
    
    def initialize_rag(self, data_dirs: List[str], force_rebuild: bool = False):
        """初始化RAG系统"""
        if not CHROMADB_AVAILABLE:
            logger.error("❌ ChromaDB dependencies not available")
            return False
            
        try:
            self._initialize_chromadb()
            
            persist_directory = self.config['vector_db']['persist_directory']
            
            # 检查是否需要重建向量数据库
            if force_rebuild or not os.path.exists(persist_directory):
                print("开始构建向量数据库...")
                documents = self.load_documents(data_dirs)
                if documents:
                    split_docs = self.split_documents(documents)
                    self.create_vectorstore(split_docs)
                else:
                    print("没有找到文档，无法构建向量数据库")
                    return False
            else:
                print("加载现有向量数据库...")
                self.load_vectorstore()
            
            # 设置检索器
            self.setup_retriever()
            return True
            
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {e}")
            return False

if __name__ == "__main__":
    # 测试RAG引擎
    rag_engine = RAGEngine()
    data_dirs = ["data/knowledge", "data/faq"]
    
    if rag_engine.initialize_rag(data_dirs, force_rebuild=True):
        # 测试检索
        query = "新生儿喂养"
        docs = rag_engine.retrieve_documents(query)
        print(f"\n检索结果 (查询: {query}):")
        for i, doc in enumerate(docs):
            if hasattr(doc, 'page_content'):
                print(f"文档 {i+1}: {doc.page_content[:100]}...")
            else:
                print(f"文档 {i+1}: {doc.get('content', '')[:100]}...")