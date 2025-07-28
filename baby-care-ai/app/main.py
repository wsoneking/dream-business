from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import yaml
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import from api
sys.path.append(str(Path(__file__).parent.parent))

from api.routes import router
from app.chain import BabyCareChain

# 创建FastAPI应用
app = FastAPI(
    title="BabyCareAI 育儿顾问系统",
    description="基于Ollama本地大模型和LangChain构建的育儿AI助手",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(router, prefix="/api/v1", tags=["BabyCare"])

# 全局变量
baby_care_chain = None

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    print("🚀 BabyCareAI 育儿顾问系统启动中...")
    
    # Get the project root directory (parent of app directory)
    project_root = Path(__file__).parent.parent
    
    # 检查必要的目录和文件
    required_dirs = ["data/knowledge", "data/faq", "config"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            print(f"⚠️  警告: 目录 {dir_path} 不存在")
    
    required_files = ["config/ollama_config.yaml", "config/custom_prompt.txt"]
    for file_name in required_files:
        file_path = project_root / file_name
        if not file_path.exists():
            print(f"⚠️  警告: 文件 {file_path} 不存在")
    
    print("✅ BabyCareAI 育儿顾问系统启动完成！")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔍 ReDoc文档: http://localhost:8000/redoc")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    print("👋 BabyCareAI 育儿顾问系统正在关闭...")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """根路径，返回简单的HTML页面"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BabyCareAI 育儿顾问系统</title>
        <style>
            body {
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f7fa;
                color: #333;
            }
            .header {
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .api-link {
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin: 5px;
                transition: background 0.3s;
            }
            .api-link:hover {
                background: #45a049;
            }
            .feature {
                margin: 10px 0;
                padding: 10px;
                background: #f8f9fa;
                border-left: 4px solid #667eea;
            }
            .example {
                background: #e8f4fd;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🍼 BabyCareAI 育儿顾问系统</h1>
            <p>基于Ollama本地大模型和LangChain构建的智能育儿助手</p>
        </div>
        
        <div class="card">
            <h2>📚 系统功能</h2>
            <div class="feature">
                <strong>🤖 智能问答：</strong>基于RAG技术，结合本地知识库提供专业育儿建议
            </div>
            <div class="feature">
                <strong>👶 个性化服务：</strong>支持宝宝信息记录，提供针对性建议
            </div>
            <div class="feature">
                <strong>🔒 隐私保护：</strong>本地部署，数据安全可控
            </div>
            <div class="feature">
                <strong>📖 知识丰富：</strong>涵盖新生儿护理、喂养、睡眠、健康等各个方面
            </div>
        </div>
        
        <div class="card">
            <h2>🔗 API接口</h2>
            <a href="/docs" class="api-link">📖 Swagger文档</a>
            <a href="/redoc" class="api-link">📋 ReDoc文档</a>
            <a href="/api/v1/health" class="api-link">💚 健康检查</a>
            <a href="/api/v1/example-questions" class="api-link">❓ 示例问题</a>
        </div>
        
        <div class="card">
            <h2>🚀 快速开始</h2>
            <div class="example">
                <h3>1. 健康检查</h3>
                <code>GET /api/v1/health</code>
            </div>
            <div class="example">
                <h3>2. 提问示例</h3>
                <code>POST /api/v1/ask</code>
                <pre>{
  "question": "新生儿一天要喂几次奶？",
  "baby_info": {
    "age": "2个月",
    "weight": "5.5kg",
    "gender": "男"
  }
}</pre>
            </div>
        </div>
        
        <div class="card">
            <h2>⚙️ 系统要求</h2>
            <ul>
                <li>✅ 已安装并运行 Ollama</li>
                <li>✅ 已拉取 LLaMA 或 Mistral 模型</li>
                <li>✅ Python 3.8+</li>
                <li>✅ 安装所需依赖包</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>💝 用心呵护每一个宝宝的成长 💝</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def load_config():
    """加载配置"""
    try:
        # Get the project root directory (parent of app directory)
        project_root = Path(__file__).parent.parent
        config_path = project_root / "config" / "ollama_config.yaml"
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print("⚠️  配置文件不存在，使用默认配置")
        return {
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": True
            }
        }

if __name__ == "__main__":
    # 加载配置
    config = load_config()
    api_config = config.get("api", {})
    
    # 启动服务
    uvicorn.run(
        "app.main:app",
        host=api_config.get("host", "0.0.0.0"),
        port=api_config.get("port", 8000),
        reload=api_config.get("debug", True),
        log_level="info"
    )