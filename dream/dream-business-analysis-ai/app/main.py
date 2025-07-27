"""
DREAM Business Analysis AI - FastAPI Application Entry Point
Main application server for business analysis using DREAM framework
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import yaml
import os
from pathlib import Path

# Import our modules
from .business_analyzer import DreamBusinessAnalyzer
from .rag_engine import RAGEngine

# Load configuration
config_path = Path(__file__).parent.parent / "config" / "ollama_config.yaml"
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Initialize FastAPI app
app = FastAPI(
    title="DREAM Business Analysis AI",
    description="专为中国市场设计的智能商业分析AI助手，使用DREAM框架方法论分析商业案例",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the application components on startup"""
    try:
        # Initialize RAG engine
        rag_engine = RAGEngine(config)
        await rag_engine.initialize()
        
        # Initialize business analyzer
        business_analyzer = DreamBusinessAnalyzer(config, rag_engine)
        
        # Store in app state to avoid circular imports
        app.state.rag_engine = rag_engine
        app.state.business_analyzer = business_analyzer
        
        print("✅ DREAM Business Analysis AI initialized successfully!")
        print(f"🚀 Server running on http://{config['api']['host']}:{config['api']['port']}")
        print("📚 API Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        raise

# Import and include API routes after app initialization to avoid circular imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.routes import router as api_router
from api.business_routes import router as business_router

app.include_router(api_router, prefix="/api/v1")
app.include_router(business_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with welcome message"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DREAM Business Analysis AI</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .feature { margin: 20px 0; padding: 15px; background: #ecf0f1; border-radius: 5px; }
            .api-link { display: inline-block; margin: 10px; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }
            .api-link:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 DREAM Business Analysis AI</h1>
            <p style="text-align: center; font-size: 18px; color: #7f8c8d;">
                专为中国市场设计的智能商业分析AI助手
            </p>
            
            <div class="feature">
                <h3>🔍 DREAM框架分析</h3>
                <p>使用需求(Demand) → 解决方案(Resolution) → 商业模式(Earning) → 增长(Acquisition) → 壁垒(Moat)五步法进行全面商业分析</p>
            </div>
            
            <div class="feature">
                <h3>🧠 假设驱动方法论</h3>
                <p>科学的假设识别、优先级评估和快速验证机制</p>
            </div>
            
            <div class="feature">
                <h3>📊 单位经济学建模</h3>
                <p>精确的财务建模和商业可行性分析</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/docs" class="api-link">📖 API文档</a>
                <a href="/redoc" class="api-link">📋 ReDoc文档</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    rag_engine = getattr(app.state, 'rag_engine', None)
    business_analyzer = getattr(app.state, 'business_analyzer', None)
    
    return {
        "status": "healthy",
        "service": "DREAM Business Analysis AI",
        "version": "1.0.0",
        "rag_engine": "initialized" if rag_engine else "not_initialized",
        "business_analyzer": "initialized" if business_analyzer else "not_initialized"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config["api"]["host"],
        port=config["api"]["port"],
        reload=config["api"]["debug"]
    )