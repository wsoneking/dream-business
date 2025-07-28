"""
BabyCareAI - Streamlit UI
Interactive web interface for baby care assistance using AI
"""

import streamlit as st
import asyncio
import yaml
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from streamlit_option_menu import option_menu
import os

# Import our baby care components
from app.chain import BabyCareChain
from app.rag_engine import RAGEngine

# Page configuration
st.set_page_config(
    page_title="BabyCareAI 育儿顾问",
    page_icon="🍼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ff6b6b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .baby-card {
        background-color: #fff5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .ai-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_config():
    """Load configuration with cloud compatibility"""
    try:
        config_path = Path(__file__).parent / "config" / "ollama_config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Override with Streamlit secrets if available
        if hasattr(st, 'secrets') and 'llm' in st.secrets:
            # Set environment variables from secrets for compatibility
            os.environ['OPENROUTER_API_KEY'] = st.secrets['llm'].get('OPENROUTER_API_KEY', '')
            os.environ['LLM_PROVIDER'] = st.secrets['llm'].get('LLM_PROVIDER', 'openrouter')
            os.environ['OPENROUTER_MODEL'] = st.secrets['llm'].get('OPENROUTER_MODEL', 'qwen/qwen3-14b:free')
        
        return config
    except Exception as e:
        st.error(f"❌ Failed to load configuration: {e}")
        # Return a minimal default config for cloud deployment
        return {
            "ollama": {
                "base_url": "http://localhost:11434",
                "model": "qwen3:8b",
                "temperature": 0.7,
                "max_tokens": 2048,
                "timeout": 60
            },
            "vector_db": {
                "type": "chromadb",
                "persist_directory": "./data/vectordb",
                "collection_name": "baby_care_knowledge"
            },
            "embedding": {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "chunk_size": 1000,
                "chunk_overlap": 200
            }
        }

@st.cache_resource
def initialize_components():
    """Initialize baby care components"""
    config = load_config()
    
    # Initialize Baby Care Chain
    baby_care_chain = BabyCareChain()
    
    return config, baby_care_chain

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🍼 BabyCareAI 育儿顾问</h1>', unsafe_allow_html=True)
    st.markdown("**专业、温暖的AI育儿助手 • Professional & Caring AI Parenting Assistant**")
    
    # Initialize components
    try:
        config, baby_care_chain = initialize_components()
        
        # Initialize RAG system if not already done
        if 'rag_initialized' not in st.session_state:
            with st.spinner("初始化AI组件... Initializing AI components..."):
                data_dirs = ["data/knowledge", "data/faq"]
                success = baby_care_chain.setup_rag_chain(data_dirs, force_rebuild=False)
                if success:
                    st.session_state.rag_initialized = True
                    st.success("✅ AI组件初始化成功！ AI components initialized successfully!")
                else:
                    st.error("❌ AI组件初始化失败 Failed to initialize AI components")
                    st.stop()
        
    except Exception as e:
        st.error(f"❌ Failed to initialize components: {e}")
        st.stop()
    
    # Sidebar navigation
    with st.sidebar:
        # Create a simple text-based logo
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #ff6b6b, #ffa726); border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0; font-weight: bold;">🍼 BabyCareAI</h2>
            <p style="color: white; margin: 5px 0 0 0; font-size: 14px;">育儿顾问系统</p>
        </div>
        """, unsafe_allow_html=True)
        
        selected = option_menu(
            menu_title="导航 Navigation",
            options=[
                "💬 智能问答 Chat",
                "👶 宝宝档案 Baby Profile",
                "📚 知识库 Knowledge",
                "📊 使用统计 Stats"
            ],
            icons=["chat", "person", "book", "graph-up"],
            menu_icon="cast",
            default_index=0,
        )
    
    # Main content based on selection
    if selected == "💬 智能问答 Chat":
        show_chat_page(baby_care_chain)
    elif selected == "👶 宝宝档案 Baby Profile":
        show_baby_profile_page()
    elif selected == "📚 知识库 Knowledge":
        show_knowledge_page(baby_care_chain)
    elif selected == "📊 使用统计 Stats":
        show_stats_page()

def show_chat_page(baby_care_chain):
    """Chat interface page"""
    
    st.markdown("## 💬 智能育儿问答 Smart Parenting Q&A")
    st.markdown("请输入您的育儿问题，我会为您提供专业、温暖的建议。")
    st.markdown("Please enter your parenting question, and I'll provide professional and caring advice.")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Baby info input
    with st.expander("👶 宝宝信息 Baby Information (可选 Optional)", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            baby_age = st.text_input("年龄 Age", placeholder="如 2个月 / e.g., 2 months")
            baby_weight = st.text_input("体重 Weight", placeholder="如 5.5kg / e.g., 5.5kg")
        
        with col2:
            baby_gender = st.selectbox("性别 Gender", ["", "男 Male", "女 Female", "其他 Other"])
            special_conditions = st.text_input("特殊情况 Special Conditions", placeholder="如早产儿 / e.g., premature")
        
        # Store baby info in session state
        if any([baby_age, baby_weight, baby_gender, special_conditions]):
            st.session_state.baby_info = {
                "age": baby_age,
                "weight": baby_weight,
                "gender": baby_gender,
                "special_conditions": special_conditions
            }
        else:
            st.session_state.baby_info = None
    
    # Chat interface
    st.markdown("### 💭 对话 Conversation")
    
    # Display chat history
    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 您 You:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message ai-message">
                <strong>🤖 BabyCareAI:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Show sources if available
            if "sources" in message and message["sources"]:
                with st.expander(f"📚 参考来源 Sources ({len(message['sources'])} 个)"):
                    for j, source in enumerate(message["sources"], 1):
                        st.markdown(f"**来源 {j}:** {source['content']}")
    
    # Example questions
    st.markdown("### 💡 示例问题 Example Questions")
    example_questions = [
        "新生儿一天要喂几次奶？",
        "宝宝晚上哭闹不止怎么办？",
        "如何建立宝宝的睡眠规律？",
        "什么时候开始添加辅食？",
        "How often should I feed my newborn?",
        "What should I do if my baby cries at night?",
        "How to establish a sleep routine for baby?",
        "When to start introducing solid foods?"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(example_questions):
        with cols[i % 2]:
            if st.button(question, key=f"example_{i}"):
                # Directly process the question instead of just setting it
                process_question(baby_care_chain, question)
                return  # Return early to avoid duplicate processing
    
    # Question input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_question = st.text_input(
            "请输入您的问题 Enter your question:",
            placeholder="例如：新生儿一天要喂几次奶？/ e.g., How often should I feed my newborn?",
            key="question_input"
        )
    
    with col2:
        ask_button = st.button("🚀 提问 Ask", type="primary")
    
    # Process question
    if ask_button and user_question:
        process_question(baby_care_chain, user_question)
    
    # Clear chat button
    if st.button("🗑️ 清除对话 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

def process_question(baby_care_chain, question):
    """Process user question and get AI response"""
    
    if not question or not question.strip():
        st.warning("请输入问题 Please enter a question")
        return
    
    # Add user message to chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })
    
    with st.spinner("🤔 AI正在思考... AI is thinking..."):
        try:
            # Get baby info from session state
            baby_info = st.session_state.get('baby_info')
            
            # Ask question
            result = baby_care_chain.ask_question(question, baby_info)
            
            # Check if result is valid
            if result and "answer" in result:
                # Add AI response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result.get("sources", [])
                })
            else:
                # Handle invalid result
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "抱歉，我无法处理您的问题。请稍后再试。Sorry, I couldn't process your question. Please try again later."
                })
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 处理问题时出错 Error processing question: {e}")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "抱歉，处理您的问题时遇到了技术问题。请稍后再试。Sorry, I encountered a technical issue. Please try again later."
            })
            st.rerun()

def show_baby_profile_page():
    """Baby profile management page"""
    
    st.markdown("## 👶 宝宝档案管理 Baby Profile Management")
    st.markdown("创建和管理宝宝的基本信息，获得更个性化的建议。")
    
    # Initialize baby profiles
    if "baby_profiles" not in st.session_state:
        st.session_state.baby_profiles = []
    
    # Add new baby profile
    with st.expander("➕ 添加新宝宝 Add New Baby", expanded=len(st.session_state.baby_profiles) == 0):
        with st.form("add_baby_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                baby_name = st.text_input("宝宝姓名 Baby Name")
                birth_date = st.date_input("出生日期 Birth Date")
                gender = st.selectbox("性别 Gender", ["男 Male", "女 Female", "其他 Other"])
            
            with col2:
                birth_weight = st.number_input("出生体重 Birth Weight (kg)", min_value=0.5, max_value=10.0, step=0.1)
                current_weight = st.number_input("当前体重 Current Weight (kg)", min_value=0.5, max_value=50.0, step=0.1)
                special_notes = st.text_area("特殊情况 Special Notes")
            
            if st.form_submit_button("💾 保存宝宝信息 Save Baby Info"):
                if baby_name:
                    new_baby = {
                        "name": baby_name,
                        "birth_date": birth_date.strftime("%Y-%m-%d"),
                        "gender": gender,
                        "birth_weight": birth_weight,
                        "current_weight": current_weight,
                        "special_notes": special_notes,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.baby_profiles.append(new_baby)
                    st.success(f"✅ 已保存 {baby_name} 的信息！")
                    st.rerun()
                else:
                    st.error("请输入宝宝姓名 Please enter baby's name")
    
    # Display existing profiles
    if st.session_state.baby_profiles:
        st.markdown("### 👶 现有宝宝档案 Existing Baby Profiles")
        
        for i, baby in enumerate(st.session_state.baby_profiles):
            with st.expander(f"👶 {baby['name']} - {baby['birth_date']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("姓名 Name", baby['name'])
                    st.metric("性别 Gender", baby['gender'])
                
                with col2:
                    # Calculate age
                    from datetime import datetime
                    birth_date = datetime.strptime(baby['birth_date'], "%Y-%m-%d")
                    age_days = (datetime.now() - birth_date).days
                    age_months = age_days // 30
                    age_str = f"{age_months}个月 {age_days % 30}天" if age_months > 0 else f"{age_days}天"
                    
                    st.metric("年龄 Age", age_str)
                    st.metric("出生体重 Birth Weight", f"{baby['birth_weight']} kg")
                
                with col3:
                    st.metric("当前体重 Current Weight", f"{baby['current_weight']} kg")
                    if baby['special_notes']:
                        st.text_area("特殊情况 Special Notes", baby['special_notes'], disabled=True)
                
                if st.button(f"🗑️ 删除 Delete {baby['name']}", key=f"delete_{i}"):
                    st.session_state.baby_profiles.pop(i)
                    st.rerun()
    else:
        st.info("还没有宝宝档案，请添加一个。No baby profiles yet, please add one.")

def show_knowledge_page(baby_care_chain):
    """Knowledge base search page"""
    
    st.markdown("## 📚 育儿知识库 Parenting Knowledge Base")
    st.markdown("搜索和浏览育儿相关知识。Search and browse parenting knowledge.")
    
    # Search interface
    search_query = st.text_input(
        "🔍 搜索知识库 Search Knowledge Base",
        placeholder="例如：新生儿护理 / e.g., newborn care",
        help="输入中文或英文问题 Enter your question in Chinese or English"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        search_button = st.button("🔍 搜索 Search", type="primary")
        num_results = st.slider("结果数量 Number of Results", 1, 10, 3)
    
    with col2:
        if search_button and search_query:
            with st.spinner("🔍 搜索知识库中... Searching knowledge base..."):
                try:
                    # Use RAG engine to search
                    if hasattr(baby_care_chain, 'rag_engine') and baby_care_chain.rag_engine:
                        results = baby_care_chain.rag_engine.retrieve_documents(search_query)
                        
                        if results:
                            st.markdown("### 📋 搜索结果 Search Results")
                            
                            for i, result in enumerate(results[:num_results], 1):
                                with st.expander(f"结果 Result {i}: {result.page_content[:100]}..."):
                                    st.markdown(result.page_content)
                                    if hasattr(result, 'metadata') and result.metadata:
                                        st.caption(f"来源 Source: {result.metadata.get('source', '未知')}")
                        else:
                            st.info("没有找到相关结果，请尝试其他关键词。No results found. Try different keywords.")
                    else:
                        st.error("知识库未初始化 Knowledge base not initialized")
                        
                except Exception as e:
                    st.error(f"搜索失败 Search failed: {e}")
    
    # Knowledge categories
    st.markdown("### 📂 知识分类 Knowledge Categories")
    
    categories = {
        "🍼 新生儿护理 Newborn Care": "0-3个月宝宝护理知识",
        "🥛 喂养指导 Feeding Guide": "母乳喂养、配方奶、辅食添加",
        "😴 睡眠训练 Sleep Training": "建立睡眠规律、解决睡眠问题",
        "🏥 健康护理 Health Care": "常见疾病、疫苗接种、发育监测",
        "🤱 产前准备 Prenatal Preparation": "孕期保健、分娩准备、产后恢复"
    }
    
    selected_category = st.selectbox("选择分类 Select Category:", list(categories.keys()))
    
    if selected_category:
        st.info(f"**{selected_category}**: {categories[selected_category]}")
        
        if st.button(f"🔍 浏览 {selected_category}"):
            # Extract category keyword for search
            category_keywords = {
                "🍼 新生儿护理 Newborn Care": "新生儿护理",
                "🥛 喂养指导 Feeding Guide": "喂养",
                "😴 睡眠训练 Sleep Training": "睡眠",
                "🏥 健康护理 Health Care": "健康",
                "🤱 产前准备 Prenatal Preparation": "产前准备"
            }
            
            keyword = category_keywords.get(selected_category, "育儿")
            
            with st.spinner(f"加载 {selected_category} 内容..."):
                try:
                    if hasattr(baby_care_chain, 'rag_engine') and baby_care_chain.rag_engine:
                        results = baby_care_chain.rag_engine.retrieve_documents(keyword)
                        
                        if results:
                            for i, result in enumerate(results[:5], 1):
                                with st.expander(f"{selected_category} - 内容 Content {i}"):
                                    st.markdown(result.page_content)
                        else:
                            st.info(f"没有找到 {selected_category} 相关内容")
                    else:
                        st.error("知识库未初始化")
                        
                except Exception as e:
                    st.error(f"加载分类内容失败: {e}")

def show_stats_page():
    """Usage statistics page"""
    
    st.markdown("## 📊 使用统计 Usage Statistics")
    st.markdown("查看系统使用情况和统计信息。View system usage and statistics.")
    
    # Mock statistics (in a real app, these would come from a database)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 总问题数 Total Questions", len(st.session_state.get('chat_history', [])) // 2)
    with col2:
        st.metric("👶 宝宝档案 Baby Profiles", len(st.session_state.get('baby_profiles', [])))
    with col3:
        st.metric("📚 知识库文档 Knowledge Docs", "50+", "育儿指南")
    with col4:
        st.metric("🌐 支持语言 Languages", "2", "中文/English")
    
    # Chat history analysis
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.markdown("### 💬 对话历史分析 Chat History Analysis")
        
        # Create a simple chart of questions over time
        user_messages = [msg for msg in st.session_state.chat_history if msg['role'] == 'user']
        
        if user_messages:
            st.markdown(f"**总提问数 Total Questions:** {len(user_messages)}")
            
            # Show recent questions
            st.markdown("#### 最近问题 Recent Questions")
            for i, msg in enumerate(user_messages[-5:], 1):
                st.markdown(f"{i}. {msg['content'][:100]}...")
    
    # System information
    st.markdown("### ⚙️ 系统信息 System Information")
    
    try:
        config = load_config()
        provider_info = "OpenRouter" if os.getenv("LLM_PROVIDER", "openrouter") == "openrouter" else "Ollama"
        
        info_data = {
            "LLM提供商 LLM Provider": provider_info,
            "模型 Model": os.getenv("OPENROUTER_MODEL", config["ollama"]["model"]),
            "向量数据库 Vector DB": config["vector_db"]["type"],
            "嵌入模型 Embedding Model": config["embedding"]["model"]
        }
        
        for key, value in info_data.items():
            st.markdown(f"**{key}:** {value}")
            
    except Exception as e:
        st.error(f"获取系统信息失败: {e}")

if __name__ == "__main__":
    main()