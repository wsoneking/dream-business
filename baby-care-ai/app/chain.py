import yaml
from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from app.rag_engine import RAGEngine
from app.llm_provider import LLMProvider

class FallbackQAChain:
    """Custom QA Chain for fallback retriever that bypasses Pydantic validation"""
    
    def __init__(self, llm, retriever, prompt):
        self.llm = llm
        self.retriever = retriever
        self.prompt = prompt
    
    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process the QA chain call"""
        query = inputs.get("query", "")
        
        # Retrieve relevant documents
        docs = self.retriever.get_relevant_documents(query)
        
        # Format context from documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Format the prompt
        formatted_prompt = self.prompt.format(context=context, question=query)
        
        # Get LLM response
        response = self.llm.invoke(formatted_prompt)
        
        # Extract text content from response (handle AIMessage objects)
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        return {
            "result": response_text,
            "source_documents": docs
        }
    
    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Alternative invoke method"""
        return self.__call__(inputs)

class BabyCareChain:
    def __init__(self, config_path: str = "config/ollama_config.yaml"):
        """初始化育儿顾问链"""
        self.config = self._load_config(config_path)
        self.llm_provider = None
        self.rag_engine = None
        self.qa_chain = None
        self.custom_prompt = self._load_custom_prompt()
        self._setup_llm()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def _load_custom_prompt(self) -> str:
        """加载自定义提示词"""
        try:
            with open("config/custom_prompt.txt", 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            return "你是一位专业的育儿顾问，请为用户提供专业、温暖的育儿建议。"
    
    def _setup_llm(self):
        """设置LLM提供商"""
        self.llm_provider = LLMProvider(self.config)
        provider_info = self.llm_provider.get_provider_info()
        print(f"LLM 初始化完成，提供商: {provider_info['provider']}, 模型: {provider_info['model']}")
    
    def setup_rag_chain(self, data_dirs: List[str], force_rebuild: bool = False):
        """设置RAG链"""
        self.rag_engine = RAGEngine(config_path="config/ollama_config.yaml")
        
        if not self.rag_engine.initialize_rag(data_dirs, force_rebuild):
            print("RAG引擎初始化失败")
            return False
        
        # 创建提示词模板
        prompt_template = f"""
{self.custom_prompt}

CRITICAL INSTRUCTIONS:
1. Respond in the SAME LANGUAGE as the user's question
2. Do NOT show any thinking process, <think> tags, or internal reasoning
3. Do NOT mix languages
4. Respond directly and naturally

Based on the following relevant information, answer the user's question:

Relevant information:
{{context}}

User question: {{question}}

Provide detailed, practical advice directly in the SAME LANGUAGE as the user's question (no thinking process):
"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # 创建QA链 - 统一使用自定义QA链避免Pydantic兼容性问题
        self.qa_chain = FallbackQAChain(
            llm=self.llm_provider.llm,
            retriever=self.rag_engine.retriever,
            prompt=PROMPT
        )
        
        print("RAG链设置完成")
        return True
    
    def ask_question(self, question: str, baby_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理用户问题"""
        if self.qa_chain is None:
            return {
                "answer": "系统尚未初始化，请稍后再试。",
                "sources": [],
                "error": "Chain not initialized"
            }
        
        try:
            # 如果有宝宝信息，添加到问题中
            enhanced_question = question
            if baby_info:
                baby_context = self._format_baby_info(baby_info)
                enhanced_question = f"{baby_context}\n\n{question}"
            
            # 调用QA链
            result = self.qa_chain({"query": enhanced_question})
            
            # 提取源文档信息
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    sources.append({
                        "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        "source": doc.metadata.get("source", "未知来源")
                    })
            
            return {
                "answer": result["result"],
                "sources": sources,
                "question": question,
                "baby_info": baby_info
            }
            
        except Exception as e:
            print(f"处理问题时出错: {str(e)}")
            return {
                "answer": "抱歉，处理您的问题时遇到了一些技术问题。请稍后再试，或者咨询专业医生。",
                "sources": [],
                "error": str(e)
            }
    
    def _format_baby_info(self, baby_info: Dict[str, Any]) -> str:
        """格式化宝宝信息"""
        info_parts = []
        
        if baby_info.get("age"):
            info_parts.append(f"宝宝年龄：{baby_info['age']}")
        
        if baby_info.get("weight"):
            info_parts.append(f"体重：{baby_info['weight']}")
        
        if baby_info.get("gender"):
            info_parts.append(f"性别：{baby_info['gender']}")
        
        if baby_info.get("special_conditions"):
            info_parts.append(f"特殊情况：{baby_info['special_conditions']}")
        
        if info_parts:
            return "宝宝信息：" + "，".join(info_parts)
        
        return ""
    
    def get_simple_answer(self, question: str) -> str:
        """获取简单回答（不使用RAG）"""
        try:
            prompt = f"""
{self.custom_prompt}

CRITICAL INSTRUCTIONS:
1. Respond in the SAME LANGUAGE as the user's question
2. Do NOT show any thinking process, <think> tags, or internal reasoning
3. Respond directly and naturally

User question: {question}

Provide professional, warm parenting advice directly in the SAME LANGUAGE as the user's question (no thinking process):
"""
            response = self.llm_provider.invoke(prompt)
            return response
        except Exception as e:
            print(f"获取简单回答时出错: {str(e)}")
            return "抱歉，我现在无法回答您的问题。建议您咨询专业医生或育儿专家。"

if __name__ == "__main__":
    # 测试链
    chain = BabyCareChain()
    
    # 设置RAG链
    data_dirs = ["data/knowledge", "data/faq"]
    if chain.setup_rag_chain(data_dirs, force_rebuild=True):
        # 测试问答
        baby_info = {
            "age": "2个月",
            "weight": "5.5kg",
            "gender": "男"
        }
        
        result = chain.ask_question("宝宝晚上总是哭闹，怎么办？", baby_info)
        print(f"问题: {result['question']}")
        print(f"回答: {result['answer']}")
        print(f"参考来源数量: {len(result['sources'])}")