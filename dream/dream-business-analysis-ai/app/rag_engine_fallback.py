"""
DREAM Business Analysis AI - Fallback RAG Engine
Simple fallback implementation for cloud environments where ChromaDB fails
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FallbackRAGEngine:
    """Fallback RAG Engine using TF-IDF for similarity search"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.documents = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.knowledge_base_path = Path(__file__).parent.parent / "data"
        
    async def initialize(self):
        """Initialize the fallback RAG engine components"""
        try:
            logger.info("🔄 Initializing Fallback RAG Engine (TF-IDF based)")
            
            # Load knowledge base
            await self.load_knowledge_base()
            
            # Initialize TF-IDF vectorizer
            if self.documents:
                texts = [doc['content'] for doc in self.documents]
                self.vectorizer = TfidfVectorizer(
                    max_features=5000,
                    stop_words=None,  # Keep Chinese characters
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.95
                )
                self.tfidf_matrix = self.vectorizer.fit_transform(texts)
                logger.info(f"✅ TF-IDF vectorizer initialized with {len(texts)} documents")
            
            logger.info("✅ Fallback RAG Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Fallback RAG Engine: {e}")
            raise
    
    async def load_knowledge_base(self):
        """Load business knowledge base into memory"""
        try:
            self.documents = []
            
            # Load frameworks
            frameworks_path = self.knowledge_base_path / "frameworks"
            if frameworks_path.exists():
                self.documents.extend(await self._load_documents_from_directory(frameworks_path, "framework"))
            
            # Load case studies
            case_studies_path = self.knowledge_base_path / "case_studies"
            if case_studies_path.exists():
                self.documents.extend(await self._load_documents_from_directory(case_studies_path, "case_study"))
            
            # Load templates
            templates_path = self.knowledge_base_path / "templates"
            if templates_path.exists():
                self.documents.extend(await self._load_documents_from_directory(templates_path, "template"))
            
            # Load benchmarks
            benchmarks_path = self.knowledge_base_path / "benchmarks"
            if benchmarks_path.exists():
                self.documents.extend(await self._load_documents_from_directory(benchmarks_path, "benchmark"))
            
            if self.documents:
                logger.info(f"✅ Loaded {len(self.documents)} documents into fallback knowledge base")
            else:
                logger.warning("⚠️ No documents found in knowledge base directories")
                
        except Exception as e:
            logger.error(f"❌ Failed to load knowledge base: {e}")
            raise
    
    async def _load_documents_from_directory(self, directory: Path, doc_type: str) -> List[Dict[str, Any]]:
        """Load documents from a specific directory"""
        documents = []
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    content = ""
                    if file_path.suffix in ['.md', '.txt']:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    elif file_path.suffix == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Extract text content from JSON
                            if isinstance(data, dict):
                                content = self._extract_text_from_dict(data)
                            else:
                                content = str(data)
                    
                    if content.strip():
                        doc = {
                            "content": content,
                            "metadata": {
                                "source": str(file_path),
                                "type": doc_type,
                                "filename": file_path.name
                            }
                        }
                        documents.append(doc)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {file_path}: {e}")
        
        return documents
    
    def _extract_text_from_dict(self, data: dict) -> str:
        """Extract text content from dictionary recursively"""
        text_parts = []
        
        for key, value in data.items():
            if isinstance(value, str):
                text_parts.append(f"{key}: {value}")
            elif isinstance(value, dict):
                text_parts.append(self._extract_text_from_dict(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        text_parts.append(item)
                    elif isinstance(item, dict):
                        text_parts.append(self._extract_text_from_dict(item))
        
        return "\n".join(text_parts)
    
    async def search_knowledge(self, query: str, k: int = 5, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant information using TF-IDF"""
        try:
            if not self.vectorizer or not self.documents:
                logger.warning("⚠️ Knowledge base not initialized")
                return []
            
            # Filter documents by type if specified
            filtered_docs = self.documents
            if filter_type:
                filtered_docs = [doc for doc in self.documents if doc['metadata']['type'] == filter_type]
                if not filtered_docs:
                    return []
            
            # Transform query using the same vectorizer
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            if filter_type:
                # Need to recalculate TF-IDF for filtered documents
                filtered_texts = [doc['content'] for doc in filtered_docs]
                filtered_tfidf = self.vectorizer.transform(filtered_texts)
                similarities = cosine_similarity(query_vector, filtered_tfidf).flatten()
                relevant_docs = filtered_docs
            else:
                similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
                relevant_docs = self.documents
            
            # Get top k results
            top_indices = np.argsort(similarities)[::-1][:k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include documents with some similarity
                    results.append({
                        "content": relevant_docs[idx]['content'],
                        "metadata": relevant_docs[idx]['metadata'],
                        "relevance_score": float(similarities[idx])
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Knowledge search failed: {e}")
            return []
    
    async def get_dream_framework_context(self, component: str) -> str:
        """Get specific DREAM framework component context"""
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
        results = await self.search_knowledge("假设验证 关键假设 验证方法", k=3)
        
        context = ""
        for result in results:
            context += f"{result['content']}\n\n"
        
        return context.strip()
    
    async def get_industry_benchmarks(self, industry: str) -> List[Dict[str, Any]]:
        """Get industry-specific benchmarks and metrics"""
        query = f"{industry} 行业基准 指标 数据"
        results = await self.search_knowledge(query, k=5, filter_type="benchmark")
        return results
    
    async def rebuild_knowledge_base(self):
        """Rebuild the entire knowledge base"""
        try:
            logger.info("🔄 Rebuilding fallback knowledge base...")
            await self.load_knowledge_base()
            
            # Reinitialize TF-IDF
            if self.documents:
                texts = [doc['content'] for doc in self.documents]
                self.tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            logger.info("✅ Fallback knowledge base rebuilt successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to rebuild knowledge base: {e}")
            raise