import os
import yaml
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import chromadb
from pathlib import Path

class RAGEngine:
    def __init__(self, config_path: str = "config/ollama_config.yaml"):
        """初始化RAG引擎"""
        self.config = self._load_config(config_path)
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
        model_name = self.config['embedding']['model']
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def load_documents(self, data_dirs: List[str]) -> List[Document]:
        """加载文档"""
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
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config['embedding']['chunk_size'],
            chunk_overlap=self.config['embedding']['chunk_overlap'],
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(documents)
        print(f"文档分割完成，共 {len(split_docs)} 个片段")
        return split_docs
    
    def create_vectorstore(self, documents: List[Document]):
        """创建向量数据库"""
        persist_directory = self.config['vector_db']['persist_directory']
        collection_name = self.config['vector_db']['collection_name']
        
        # 确保目录存在
        os.makedirs(persist_directory, exist_ok=True)
        
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        
        # 持久化向量数据库
        self.vectorstore.persist()
        print(f"向量数据库创建完成，保存在 {persist_directory}")
    
    def load_vectorstore(self):
        """加载已存在的向量数据库"""
        persist_directory = self.config['vector_db']['persist_directory']
        collection_name = self.config['vector_db']['collection_name']
        
        if os.path.exists(persist_directory):
            self.vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings,
                collection_name=collection_name
            )
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
    
    def retrieve_documents(self, query: str) -> List[Document]:
        """检索相关文档"""
        if self.retriever is None:
            raise ValueError("检索器未初始化")
        
        relevant_docs = self.retriever.invoke(query)
        return relevant_docs
    
    def initialize_rag(self, data_dirs: List[str], force_rebuild: bool = False):
        """初始化RAG系统"""
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
            print(f"文档 {i+1}: {doc.page_content[:100]}...")