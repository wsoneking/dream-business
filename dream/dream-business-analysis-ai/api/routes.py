"""
DREAM Business Analysis AI - Main API Routes
General API endpoints for system management
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response Models
class KnowledgeSearchRequest(BaseModel):
    query: str
    k: int = 5
    filter_type: Optional[str] = None

class KnowledgeSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    total_results: int
    status: str

class SystemStatusResponse(BaseModel):
    status: str
    components: Dict[str, str]
    version: str
    uptime: str

# Helper function to get components from app state
def get_app_components(request: Request):
    """Get RAG engine and business analyzer from app state"""
    app = request.app
    rag_engine = getattr(app.state, 'rag_engine', None)
    business_analyzer = getattr(app.state, 'business_analyzer', None)
    return rag_engine, business_analyzer

# System Management Endpoints
@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(request: Request):
    """Get system status and component health"""
    try:
        rag_engine, business_analyzer = get_app_components(request)
        
        return SystemStatusResponse(
            status="healthy",
            components={
                "rag_engine": "initialized" if rag_engine else "not_initialized",
                "business_analyzer": "initialized" if business_analyzer else "not_initialized",
                "vector_db": "connected" if rag_engine and hasattr(rag_engine, 'vectorstore') and rag_engine.vectorstore else "disconnected",
                "llm": "connected" if business_analyzer and hasattr(business_analyzer, 'llm') and business_analyzer.llm else "disconnected"
            },
            version="1.0.0",
            uptime="running"
        )
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"System status check failed: {str(e)}")

@router.post("/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_knowledge_base(request: Request, search_request: KnowledgeSearchRequest):
    """Search the business knowledge base"""
    try:
        rag_engine, _ = get_app_components(request)
        if not rag_engine:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")
        
        results = await rag_engine.search_knowledge(
            query=search_request.query,
            k=search_request.k,
            filter_type=search_request.filter_type
        )
        
        return KnowledgeSearchResponse(
            results=results,
            query=search_request.query,
            total_results=len(results),
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Knowledge search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Knowledge search failed: {str(e)}")

@router.post("/knowledge/rebuild")
async def rebuild_knowledge_base(request: Request):
    """Rebuild the knowledge base from source files"""
    try:
        rag_engine, _ = get_app_components(request)
        if not rag_engine:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")
        
        await rag_engine.rebuild_knowledge_base()
        
        return {
            "status": "success",
            "message": "Knowledge base rebuilt successfully"
        }
        
    except Exception as e:
        logger.error(f"Knowledge base rebuild failed: {e}")
        raise HTTPException(status_code=500, detail=f"Knowledge base rebuild failed: {str(e)}")

@router.get("/knowledge/stats")
async def get_knowledge_base_stats(request: Request):
    """Get knowledge base statistics"""
    try:
        rag_engine, _ = get_app_components(request)
        if not rag_engine:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")
        
        # Get collection stats
        count = 0
        if hasattr(rag_engine, 'vectorstore') and rag_engine.vectorstore and hasattr(rag_engine.vectorstore, '_collection'):
            count = rag_engine.vectorstore._collection.count()
        
        return {
            "total_documents": count,
            "collection_name": rag_engine.config["vector_db"]["collection_name"],
            "embedding_model": rag_engine.config["embedding"]["model"],
            "chunk_size": rag_engine.config["embedding"]["chunk_size"],
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Knowledge base stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Knowledge base stats failed: {str(e)}")

# Framework Context Endpoints
@router.get("/framework/dream/{component}")
async def get_dream_component_context(request: Request, component: str):
    """Get DREAM framework component context"""
    try:
        rag_engine, _ = get_app_components(request)
        if not rag_engine:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")
        
        valid_components = ["demand", "resolution", "earning", "acquisition", "moat"]
        if component.lower() not in valid_components:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid component. Must be one of: {', '.join(valid_components)}"
            )
        
        context = await rag_engine.get_dream_framework_context(component)
        
        return {
            "component": component,
            "context": context,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DREAM component context failed: {e}")
        raise HTTPException(status_code=500, detail=f"DREAM component context failed: {str(e)}")

@router.get("/framework/hypothesis")
async def get_hypothesis_validation_context(request: Request):
    """Get hypothesis validation methodology context"""
    try:
        rag_engine, _ = get_app_components(request)
        if not rag_engine:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")
        
        context = await rag_engine.get_hypothesis_validation_context()
        
        return {
            "context": context,
            "methodology": "hypothesis_validation",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Hypothesis validation context failed: {e}")
        raise HTTPException(status_code=500, detail=f"Hypothesis validation context failed: {str(e)}")

@router.get("/benchmarks/{industry}")
async def get_industry_benchmarks(request: Request, industry: str):
    """Get industry-specific benchmarks and metrics"""
    try:
        rag_engine, _ = get_app_components(request)
        if not rag_engine:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")
        
        benchmarks = await rag_engine.get_industry_benchmarks(industry)
        
        return {
            "industry": industry,
            "benchmarks": benchmarks,
            "total_benchmarks": len(benchmarks),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Industry benchmarks failed: {e}")
        raise HTTPException(status_code=500, detail=f"Industry benchmarks failed: {str(e)}")

# Utility Endpoints
@router.get("/config")
async def get_system_config(request: Request):
    """Get system configuration (non-sensitive parts)"""
    try:
        rag_engine, business_analyzer = get_app_components(request)
        
        if not rag_engine or not business_analyzer:
            raise HTTPException(status_code=503, detail="System not fully initialized")
        
        config = {
            "api": {
                "version": "1.0.0",
                "host": rag_engine.config["api"]["host"],
                "port": rag_engine.config["api"]["port"]
            },
            "vector_db": {
                "type": rag_engine.config["vector_db"]["type"],
                "collection_name": rag_engine.config["vector_db"]["collection_name"]
            },
            "embedding": {
                "model": rag_engine.config["embedding"]["model"],
                "chunk_size": rag_engine.config["embedding"]["chunk_size"],
                "chunk_overlap": rag_engine.config["embedding"]["chunk_overlap"]
            },
            "business_analysis": rag_engine.config["business_analysis"]
        }
        
        return {
            "config": config,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Config retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Config retrieval failed: {str(e)}")

@router.get("/ping")
async def ping():
    """Simple ping endpoint for health checks"""
    return {
        "message": "pong",
        "service": "DREAM Business Analysis AI",
        "status": "healthy",
        "timestamp": "2025-01-27T18:45:00Z"
    }