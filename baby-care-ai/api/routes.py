from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
from app.chain import BabyCareChain

# 创建路由器
router = APIRouter()

# 全局链实例
baby_care_chain = None

# 请求模型
class QuestionRequest(BaseModel):
    question: str
    baby_info: Optional[Dict[str, Any]] = None

class BabyInfo(BaseModel):
    age: Optional[str] = None
    weight: Optional[str] = None
    gender: Optional[str] = None
    special_conditions: Optional[str] = None

class SimpleQuestionRequest(BaseModel):
    question: str

class RebuildRequest(BaseModel):
    force_rebuild: bool = True

# 响应模型
class QuestionResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]
    question: str
    baby_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    message: str
    initialized: bool

async def initialize_chain():
    """异步初始化链"""
    global baby_care_chain
    try:
        baby_care_chain = BabyCareChain()
        data_dirs = ["data/knowledge", "data/faq"]
        success = baby_care_chain.setup_rag_chain(data_dirs, force_rebuild=False)
        return success
    except Exception as e:
        print(f"初始化链时出错: {str(e)}")
        return False

@router.on_event("startup")
async def startup_event():
    """启动时初始化"""
    print("正在初始化育儿顾问系统...")
    success = await initialize_chain()
    if success:
        print("育儿顾问系统初始化成功！")
    else:
        print("育儿顾问系统初始化失败！")

@router.get("/", response_model=StatusResponse)
async def root():
    """根路径，返回系统状态"""
    global baby_care_chain
    return StatusResponse(
        status="running",
        message="BabyCareAI 育儿顾问系统正在运行",
        initialized=baby_care_chain is not None and baby_care_chain.qa_chain is not None
    )

@router.get("/health", response_model=StatusResponse)
async def health_check():
    """健康检查"""
    global baby_care_chain
    
    if baby_care_chain is None:
        return StatusResponse(
            status="error",
            message="系统未初始化",
            initialized=False
        )
    
    try:
        # 简单测试LLM连接
        test_response = baby_care_chain.get_simple_answer("你好")
        return StatusResponse(
            status="healthy",
            message="系统运行正常",
            initialized=True
        )
    except Exception as e:
        return StatusResponse(
            status="error",
            message=f"系统异常: {str(e)}",
            initialized=False
        )

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """处理用户问题（使用RAG）"""
    global baby_care_chain
    
    if baby_care_chain is None:
        raise HTTPException(status_code=503, detail="系统未初始化，请稍后再试")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    try:
        # 异步处理问题
        result = baby_care_chain.ask_question(
            question=request.question,
            baby_info=request.baby_info
        )
        
        return QuestionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理问题时出错: {str(e)}")

@router.post("/ask-simple")
async def ask_simple_question(request: SimpleQuestionRequest):
    """简单问答（不使用RAG）"""
    global baby_care_chain
    
    if baby_care_chain is None:
        raise HTTPException(status_code=503, detail="系统未初始化，请稍后再试")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    try:
        answer = baby_care_chain.get_simple_answer(request.question)
        return {
            "answer": answer,
            "question": request.question,
            "type": "simple"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理问题时出错: {str(e)}")

@router.post("/rebuild-knowledge")
async def rebuild_knowledge_base(request: RebuildRequest, background_tasks: BackgroundTasks):
    """重建知识库"""
    global baby_care_chain
    
    if baby_care_chain is None:
        raise HTTPException(status_code=503, detail="系统未初始化")
    
    def rebuild_task():
        try:
            data_dirs = ["data/knowledge", "data/faq"]
            success = baby_care_chain.setup_rag_chain(data_dirs, force_rebuild=request.force_rebuild)
            print(f"知识库重建{'成功' if success else '失败'}")
        except Exception as e:
            print(f"重建知识库时出错: {str(e)}")
    
    background_tasks.add_task(rebuild_task)
    
    return {
        "message": "知识库重建任务已启动，请稍后查看系统状态",
        "status": "started"
    }

@router.get("/baby-info-template")
async def get_baby_info_template():
    """获取宝宝信息模板"""
    return {
        "template": {
            "age": "例如：2个月、6个月、1岁",
            "weight": "例如：5.5kg、8kg",
            "gender": "男/女",
            "special_conditions": "例如：早产、过敏体质等特殊情况"
        },
        "example": {
            "age": "3个月",
            "weight": "6kg",
            "gender": "女",
            "special_conditions": "轻微湿疹"
        }
    }

@router.get("/knowledge-stats")
async def get_knowledge_stats():
    """获取知识库统计信息"""
    global baby_care_chain
    
    if baby_care_chain is None or baby_care_chain.rag_engine is None:
        raise HTTPException(status_code=503, detail="系统未初始化")
    
    try:
        # 获取向量数据库信息
        vectorstore = baby_care_chain.rag_engine.vectorstore
        if vectorstore:
            collection = vectorstore._collection
            count = collection.count()
            return {
                "document_count": count,
                "status": "ready",
                "message": f"知识库包含 {count} 个文档片段"
            }
        else:
            return {
                "document_count": 0,
                "status": "not_ready",
                "message": "知识库未就绪"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息时出错: {str(e)}")

# 示例问题
@router.get("/example-questions")
async def get_example_questions():
    """获取示例问题"""
    return {
        "examples": [
            {
                "category": "新生儿护理",
                "questions": [
                    "新生儿一天要喂几次奶？",
                    "宝宝哭闹不止怎么办？",
                    "如何给新生儿洗澡？"
                ]
            },
            {
                "category": "喂养问题",
                "questions": [
                    "什么时候开始添加辅食？",
                    "如何判断宝宝是否吃饱了？",
                    "宝宝不爱吃奶怎么办？"
                ]
            },
            {
                "category": "睡眠问题",
                "questions": [
                    "宝宝睡觉时需要开灯吗？",
                    "如何建立宝宝的睡眠规律？",
                    "宝宝夜醒频繁怎么办？"
                ]
            },
            {
                "category": "健康问题",
                "questions": [
                    "宝宝发烧了怎么办？",
                    "如何预防宝宝湿疹？",
                    "宝宝便秘怎么办？"
                ]
            }
        ]
    }