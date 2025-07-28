"""
DREAM Business Analysis AI - Streamlit UI
Interactive web interface for business analysis using the DREAM framework
"""

import streamlit as st
import asyncio
import yaml
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from streamlit_option_menu import option_menu
import io
import re
import os

# Import our business analysis components
from app.business_analyzer import DreamBusinessAnalyzer
from app.rag_engine import RAGEngine

# Page configuration
st.set_page_config(
    page_title="DREAM Business Analysis AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
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
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
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
                "temperature": 0.3,
                "max_tokens": 4096,
                "timeout": 120
            },
            "vector_db": {
                "type": "chromadb",
                "persist_directory": "./data/vectordb",
                "collection_name": "dream_business_knowledge"
            },
            "embedding": {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "chunk_size": 1500,
                "chunk_overlap": 300
            }
        }

@st.cache_resource
def initialize_components():
    """Initialize business analysis components"""
    config = load_config()
    
    # Initialize RAG Engine
    rag_engine = RAGEngine(config)
    
    # Initialize Business Analyzer
    business_analyzer = DreamBusinessAnalyzer(config, rag_engine)
    
    return config, rag_engine, business_analyzer

def process_think_tags(text):
    """Process <think> tags to make them collapsible using Streamlit expander"""
    import re
    
    # Find all <think>...</think> blocks
    think_pattern = r'<think>(.*?)</think>'
    
    # Store think blocks to be processed separately
    think_blocks = []
    
    def extract_think(match):
        think_content = match.group(1).strip()
        think_blocks.append(think_content)
        # Replace with a placeholder that we'll handle in display
        return f"__THINK_BLOCK_{len(think_blocks)-1}__"
    
    # Extract think blocks and replace with placeholders
    processed_text = re.sub(think_pattern, extract_think, text, flags=re.DOTALL)
    
    return processed_text, think_blocks

def display_content_with_think_blocks(content, think_blocks=None):
    """Display content with think blocks as Streamlit expanders"""
    if think_blocks is None:
        think_blocks = []
    
    # Split content by think block placeholders
    parts = content.split('__THINK_BLOCK_')
    
    # Display first part
    if parts[0].strip():
        st.markdown(parts[0].strip())
    
    # Display remaining parts with think blocks
    for i in range(1, len(parts)):
        part = parts[i]
        
        # Extract think block index from the beginning of the part
        if part.startswith('0__') or any(part.startswith(f'{j}__') for j in range(len(think_blocks))):
            # Find the think block index
            think_index = int(part.split('__')[0])
            remaining_content = '__'.join(part.split('__')[1:])
            
            # Display think block as expander
            if think_index < len(think_blocks):
                with st.expander("🤔 AI Thinking Process (Click to expand)", expanded=False):
                    st.markdown(think_blocks[think_index], unsafe_allow_html=True)
            
            # Display remaining content
            if remaining_content.strip():
                st.markdown(remaining_content.strip())
        else:
            # No think block, just display content
            if part.strip():
                st.markdown(part.strip())

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎯 DREAM Business Analysis AI</h1>', unsafe_allow_html=True)
    st.markdown("**D**emand • **R**esolution • **E**arning • **A**cquisition • **M**oat")
    
    # Initialize components
    try:
        config, rag_engine, business_analyzer = initialize_components()
        
        # Initialize components asynchronously
        if 'initialized' not in st.session_state:
            with st.spinner("Initializing AI components..."):
                # Run async initialization
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(rag_engine.initialize())
                # Note: business_analyzer initializes synchronously in __init__
                st.session_state.initialized = True
                st.success("✅ AI components initialized successfully!")
        
    except Exception as e:
        st.error(f"❌ Failed to initialize components: {e}")
        st.stop()
    
    # Sidebar navigation
    with st.sidebar:
        # Create a simple text-based logo
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #1f77b4, #2ca02c); border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0; font-weight: bold;">🎯 DREAM</h2>
            <p style="color: white; margin: 5px 0 0 0; font-size: 14px;">Business Analysis AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        selected = option_menu(
            menu_title="Navigation",
            options=[
                "🔍 DREAM Analysis",
                "📚 Knowledge Base",
                "📋 Case Studies"
            ],
            icons=["search", "book", "folder"],
            menu_icon="cast",
            default_index=0,
        )
    
    # Main content based on selection
    if selected == "🔍 DREAM Analysis":
        show_dream_analysis_page(business_analyzer)
    elif selected == "📚 Knowledge Base":
        show_knowledge_base_page(rag_engine)
    elif selected == "📋 Case Studies":
        show_case_studies_page()

def show_dream_analysis_page(business_analyzer):
    """DREAM Framework analysis page"""
    
    st.markdown("## 🔍 DREAM Framework Analysis")
    st.markdown("Comprehensive business analysis using the 5-step DREAM methodology")
    
    # Business case input
    with st.expander("📝 Business Case Input", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            business_name = st.text_input(
                "Business Name",
                value=st.session_state.get('example_business_name', ''),
                placeholder="e.g., 智能健身教练APP"
            )
            
            # Get the default business type from session state if available
            default_business_type = st.session_state.get('example_business_type', "SaaS平台")
            business_type_options = [
                "SaaS平台", "移动应用", "电商平台", "O2O服务",
                "硬件产品", "内容平台", "金融科技", "教育科技", "其他"
            ]
            try:
                default_index = business_type_options.index(default_business_type)
            except ValueError:
                default_index = 0
            
            business_type = st.selectbox(
                "Business Type",
                business_type_options,
                index=default_index
            )
        
        with col2:
            # Get the default target market from session state if available
            default_target_market = st.session_state.get('example_target_market', "中国大陆")
            target_market_options = [
                "中国大陆", "港澳台", "东南亚", "全球市场"
            ]
            try:
                default_market_index = target_market_options.index(default_target_market)
            except ValueError:
                default_market_index = 0
                
            target_market = st.selectbox(
                "Target Market",
                target_market_options,
                index=default_market_index
            )
            analysis_depth = st.selectbox("Analysis Depth", [
                "快速分析 (5分钟)", "标准分析 (15分钟)", "深度分析 (30分钟)"
            ])
    
    # Business description
    business_description = st.text_area(
        "Business Description",
        value=st.session_state.get('example_loaded', ''),
        placeholder="""请详细描述您的商业想法，包括：
- 产品/服务描述
- 目标用户群体
- 核心功能特性
- 预期商业模式
- 市场机会等""",
        height=150
    )
    
    # Analysis controls
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🚀 Start DREAM Analysis", type="primary", disabled=not business_description.strip()):
            perform_dream_analysis(business_analyzer, business_name, business_description, business_type)
    
    with col2:
        if st.button("📋 加载示例案例"):
            load_example_business_case()
            st.rerun()
    
    with col3:
        if st.button("🗑️ 清除数据"):
            clear_example_data()
            st.rerun()
    
    # Results display
    if 'dream_results' in st.session_state:
        display_dream_results(st.session_state.dream_results, business_analyzer)

def perform_dream_analysis(business_analyzer, business_name, business_description, business_type):
    """Perform DREAM framework analysis"""
    
    with st.spinner("🧠 AI is analyzing your business case..."):
        try:
            # Prepare analysis request
            analysis_request = f"""
            商业案例：{business_name}
            业务类型：{business_type}
            
            详细描述：
            {business_description}
            
            请按照DREAM框架进行全面分析。
            """
            
            # Run async analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Perform each DREAM component analysis
            results = {}
            
            # Demand Analysis
            with st.status("📊 Analyzing Demand (需求分析)..."):
                demand_result = loop.run_until_complete(
                    business_analyzer.analyze_demand(analysis_request)
                )
                results['demand'] = demand_result
                st.write("✅ Demand analysis completed")
            
            # Resolution Analysis  
            with st.status("💡 Analyzing Resolution (解决方案)..."):
                resolution_result = loop.run_until_complete(
                    business_analyzer.analyze_resolution(analysis_request)
                )
                results['resolution'] = resolution_result
                st.write("✅ Resolution analysis completed")
            
            # Earning Analysis
            with st.status("💰 Analyzing Earning (商业模式)..."):
                earning_result = loop.run_until_complete(
                    business_analyzer.analyze_earning(analysis_request)
                )
                results['earning'] = earning_result
                st.write("✅ Earning analysis completed")
            
            # Acquisition Analysis
            with st.status("📈 Analyzing Acquisition (增长策略)..."):
                acquisition_result = loop.run_until_complete(
                    business_analyzer.analyze_acquisition(analysis_request)
                )
                results['acquisition'] = acquisition_result
                st.write("✅ Acquisition analysis completed")
            
            # Moat Analysis
            with st.status("🏰 Analyzing Moat (竞争壁垒)..."):
                moat_result = loop.run_until_complete(
                    business_analyzer.analyze_moat(analysis_request)
                )
                results['moat'] = moat_result
                st.write("✅ Moat analysis completed")
            
            # Store results
            st.session_state.dream_results = {
                'business_name': business_name,
                'business_type': business_type,
                'analysis_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'results': results
            }
            
            st.success("🎉 DREAM Analysis completed successfully!")
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")

def display_dream_results(dream_results, business_analyzer):
    """Display DREAM analysis results"""
    
    st.markdown("## 📊 Analysis Results")
    
    # Header info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Business", dream_results['business_name'])
    with col2:
        st.metric("Type", dream_results['business_type'])
    with col3:
        st.metric("Analyzed", dream_results['analysis_time'])
    
    # DREAM components tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Demand", "💡 Resolution", "💰 Earning", "📈 Acquisition", "🏰 Moat"
    ])
    
    with tab1:
        st.markdown("### 📊 Demand Analysis (需求分析)")
        if 'demand' in dream_results['results']:
            result = dream_results['results']['demand']
            # Extract just the analysis content if it's a dict
            if isinstance(result, dict) and 'analysis' in result:
                processed_content, think_blocks = process_think_tags(result['analysis'])
                display_content_with_think_blocks(processed_content, think_blocks)
            elif isinstance(result, str):
                processed_content, think_blocks = process_think_tags(result)
                display_content_with_think_blocks(processed_content, think_blocks)
            else:
                st.write(result)
        else:
            st.info("Demand analysis not available")
    
    with tab2:
        st.markdown("### 💡 Resolution Analysis (解决方案)")
        if 'resolution' in dream_results['results']:
            result = dream_results['results']['resolution']
            if isinstance(result, dict) and 'analysis' in result:
                processed_content, think_blocks = process_think_tags(result['analysis'])
                display_content_with_think_blocks(processed_content, think_blocks)
            elif isinstance(result, str):
                processed_content, think_blocks = process_think_tags(result)
                display_content_with_think_blocks(processed_content, think_blocks)
            else:
                st.write(result)
        else:
            st.info("Resolution analysis not available")
    
    with tab3:
        st.markdown("### 💰 Earning Analysis (商业模式)")
        if 'earning' in dream_results['results']:
            result = dream_results['results']['earning']
            if isinstance(result, dict) and 'analysis' in result:
                processed_content, think_blocks = process_think_tags(result['analysis'])
                display_content_with_think_blocks(processed_content, think_blocks)
            elif isinstance(result, str):
                processed_content, think_blocks = process_think_tags(result)
                display_content_with_think_blocks(processed_content, think_blocks)
            else:
                st.write(result)
        else:
            st.info("Earning analysis not available")
    
    with tab4:
        st.markdown("### 📈 Acquisition Analysis (增长策略)")
        if 'acquisition' in dream_results['results']:
            result = dream_results['results']['acquisition']
            if isinstance(result, dict) and 'analysis' in result:
                processed_content, think_blocks = process_think_tags(result['analysis'])
                display_content_with_think_blocks(processed_content, think_blocks)
            elif isinstance(result, str):
                processed_content, think_blocks = process_think_tags(result)
                display_content_with_think_blocks(processed_content, think_blocks)
            else:
                st.write(result)
        else:
            st.info("Acquisition analysis not available")
    
    with tab5:
        st.markdown("### 🏰 Moat Analysis (竞争壁垒)")
        if 'moat' in dream_results['results']:
            result = dream_results['results']['moat']
            if isinstance(result, dict) and 'analysis' in result:
                processed_content, think_blocks = process_think_tags(result['analysis'])
                display_content_with_think_blocks(processed_content, think_blocks)
            elif isinstance(result, str):
                processed_content, think_blocks = process_think_tags(result)
                display_content_with_think_blocks(processed_content, think_blocks)
            else:
                st.write(result)
        else:
            st.info("Moat analysis not available")
    
    # Export options
    st.markdown("### 📤 Export Results")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Export as Markdown", type="primary"):
            with st.spinner("🔄 Generating Markdown report..."):
                md_data = generate_markdown_report(dream_results)
                if md_data:
                    st.download_button(
                        label="📥 Download Markdown Report",
                        data=md_data,
                        file_name=f"DREAM_Analysis_{dream_results['business_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        key="md_download"
                    )
                    st.success("✅ Markdown report generated successfully!")
    
    with col2:
        json_data = json.dumps(dream_results, ensure_ascii=False, indent=2)
        st.download_button(
            label="💾 Download JSON",
            data=json_data,
            file_name=f"dream_analysis_{dream_results['business_name']}.json",
            mime="application/json"
        )

def load_example_business_case():
    """Load example business case with pre-prepared DREAM analysis"""
    import json
    from pathlib import Path
    
    try:
        # Load the pre-prepared example data
        example_file = Path(__file__).parent / "data" / "case_studies" / "dream_analysis_社区旅游.json"
        
        with open(example_file, 'r', encoding='utf-8') as f:
            example_data = json.load(f)
        
        # Set the business description in session state
        st.session_state.example_loaded = example_data['business_description']
        
        # Set the business name and other fields
        st.session_state.example_business_name = example_data['business_name']
        st.session_state.example_business_type = example_data['business_type']
        st.session_state.example_target_market = example_data['target_market']
        
        # Load the pre-prepared DREAM analysis results
        st.session_state.dream_results = {
            'business_name': example_data['business_name'],
            'business_type': example_data['business_type'],
            'analysis_time': example_data['analysis_time'],
            'results': example_data['dream_analysis']
        }
        
        st.success("✅ 示例案例已加载：智能健身教练APP")
        
    except Exception as e:
        st.error(f"❌ 加载示例案例失败: {e}")
        # Fallback to original example if file loading fails
        example_case = """一款基于AI的个人健身教练应用，为用户提供个性化的健身计划、实时动作指导、进度跟踪和营养建议。

产品特色：
- AI动作识别和纠正技术
- 个性化训练计划生成
- 实时健身数据分析
- 社区互动和挑战功能
- 智能营养建议系统

目标用户：
- 25-40岁城市白领
- 有健身需求但缺乏专业指导
- 愿意为健康投资的中高收入人群

商业模式：
- 基础功能免费，高级功能订阅制
- 月费99元，年费999元
- 企业团体健身服务
- 健身器材和营养品推荐分成"""
        
        st.session_state.example_loaded = example_case
        st.session_state.example_business_name = "智能健身教练APP"

def clear_example_data():
    """Clear example data from session state"""
    keys_to_clear = [
        'example_loaded',
        'example_business_name',
        'example_business_type',
        'example_target_market',
        'dream_results'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("✅ 数据已清除")


def generate_markdown_report(dream_results):
    """Generate Markdown report from DREAM analysis results"""
    try:
        # Build markdown content
        md_content = []
        
        # Title and header
        md_content.append("# DREAM Business Analysis Report")
        md_content.append("")
        md_content.append("## Business Information")
        md_content.append("")
        md_content.append(f"- **Business Name**: {dream_results['business_name']}")
        md_content.append(f"- **Business Type**: {dream_results['business_type']}")
        md_content.append(f"- **Analysis Date**: {dream_results['analysis_time']}")
        md_content.append("")
        
        # DREAM components
        dream_components = [
            ("📊 Demand Analysis (需求分析)", "demand"),
            ("💡 Resolution Analysis (解决方案)", "resolution"),
            ("💰 Earning Analysis (商业模式)", "earning"),
            ("📈 Acquisition Analysis (增长策略)", "acquisition"),
            ("🏰 Moat Analysis (竞争壁垒)", "moat")
        ]
        
        for title, key in dream_components:
            md_content.append(f"## {title}")
            md_content.append("")
            
            if key in dream_results['results']:
                result = dream_results['results'][key]
                
                # Extract content
                if isinstance(result, dict) and 'analysis' in result:
                    content = result['analysis']
                elif isinstance(result, str):
                    content = result
                else:
                    content = str(result)
                
                # Clean content for markdown
                content = clean_content_for_markdown(content)
                md_content.append(content)
            else:
                md_content.append("*Analysis not available*")
            
            md_content.append("")
            md_content.append("---")
            md_content.append("")
        
        # Footer
        md_content.append("## Report Information")
        md_content.append("")
        md_content.append("This report was generated by the DREAM Business Analysis AI system.")
        md_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(md_content)
        
    except Exception as e:
        st.error(f"Markdown generation failed: {e}")
        return None

def clean_content_for_markdown(content):
    """Clean content for Markdown generation"""
    if not content:
        return ""
    
    # Ensure content is a string
    if isinstance(content, bytes):
        content = content.decode('utf-8', errors='ignore')
    
    # Remove think tags but preserve their content in a collapsible format
    import re
    def replace_think_for_md(match):
        think_content = match.group(1).strip()
        return f"\n<details>\n<summary>🤔 AI Thinking Process</summary>\n\n{think_content}\n\n</details>\n"
    
    content = re.sub(r'<think>(.*?)</think>', replace_think_for_md, content, flags=re.DOTALL)
    
    # Clean up excessive whitespace but preserve structure
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    return content.strip()

def clean_content_for_html(content):
    """Clean content for HTML generation while preserving Chinese characters"""
    if not content:
        return ""
    
    # Ensure content is a string
    if isinstance(content, bytes):
        content = content.decode('utf-8', errors='ignore')
    
    # Remove think tags
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    
    # Convert markdown to HTML
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)  # Bold
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)              # Italic
    
    # Convert headings to HTML
    content = re.sub(r'^### (.*?)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    
    # Convert bullet points to HTML lists
    lines = content.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            item_text = line.strip()[2:].strip()
            result_lines.append(f'<li>{item_text}</li>')
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            if line.strip():
                result_lines.append(f'<p>{line.strip()}</p>')
            else:
                result_lines.append('')
    
    if in_list:
        result_lines.append('</ul>')
    
    content = '\n'.join(result_lines)
    
    # Clean up excessive whitespace
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    # Escape HTML special characters but preserve our tags
    content = content.replace('&', '&amp;')
    content = content.replace('<', '&lt;').replace('>', '&gt;')
    # Restore our HTML tags
    content = re.sub(r'&lt;(/?(?:strong|em|h[2-4]|ul|li|p))&gt;', r'<\1>', content)
    
    return content.strip()


def show_knowledge_base_page(rag_engine):
    """Knowledge base search page"""
    
    st.markdown("## 📚 Knowledge Base")
    st.markdown("Search and explore the DREAM framework knowledge base")
    
    # Search interface
    search_query = st.text_input(
        "🔍 Search Knowledge Base",
        placeholder="e.g., 如何进行用户需求分析？",
        help="Enter your question in Chinese or English"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        search_button = st.button("🔍 Search", type="primary")
        num_results = st.slider("Number of Results", 1, 10, 3)
    
    with col2:
        if search_button and search_query:
            with st.spinner("🔍 Searching knowledge base..."):
                try:
                    # Perform search
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    results = loop.run_until_complete(
                        rag_engine.search_knowledge(search_query, num_results)
                    )
                    
                    if results:
                        st.markdown("### 📋 Search Results")
                        
                        for i, result in enumerate(results, 1):
                            with st.expander(f"Result {i}: {result['content'][:100]}..."):
                                st.markdown(result['content'])
                                if 'metadata' in result:
                                    st.caption(f"Source: {result['metadata']}")
                    else:
                        st.info("No results found. Try different keywords.")
                        
                except Exception as e:
                    st.error(f"Search failed: {e}")
    
    # Knowledge base statistics
    st.markdown("### 📊 Knowledge Base Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Documents", "15", "Framework guides")
    with col2:
        st.metric("🧩 Chunks", "150+", "Text segments")
    with col3:
        st.metric("🏷️ Categories", "5", "DREAM components")
    with col4:
        st.metric("🌐 Language", "中文", "Chinese focused")
    
    # Browse categories
    st.markdown("### 📂 Browse by Category")
    
    categories = {
        "📊 Demand (需求)": "User analysis, market research, demand validation",
        "💡 Resolution (解决方案)": "Value proposition, product-market fit, solution design",
        "💰 Earning (商业模式)": "Revenue models, pricing, unit economics",
        "📈 Acquisition (增长)": "Customer acquisition, growth strategies, marketing",
        "🏰 Moat (壁垒)": "Competitive advantages, defensibility, moats"
    }
    
    selected_category = st.selectbox("Select Category:", list(categories.keys()))
    
    if selected_category:
        st.info(f"**{selected_category}**: {categories[selected_category]}")
        
        if st.button(f"🔍 Explore {selected_category}"):
            # Search for category-specific content
            category_query = selected_category.split("(")[1].split(")")[0]  # Extract Chinese term
            
            with st.spinner(f"Loading {selected_category} content..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    results = loop.run_until_complete(
                        rag_engine.search_knowledge(category_query, 5)
                    )
                    
                    if results:
                        for i, result in enumerate(results, 1):
                            with st.expander(f"{selected_category} - Content {i}"):
                                st.markdown(result['content'])
                    else:
                        st.info(f"No content found for {selected_category}")
                        
                except Exception as e:
                    st.error(f"Failed to load category content: {e}")

def show_case_studies_page():
   """Case studies showcase page"""
   
   st.markdown("## 📋 Case Studies")
   st.markdown("Explore real business analysis examples using the DREAM framework")
   
   # Load case studies from the data directory
   case_studies_dir = Path(__file__).parent / "data" / "case_studies"
   
   try:
       # Get all JSON files in the case studies directory
       case_study_files = list(case_studies_dir.glob("*.json"))
       
       if not case_study_files:
           st.warning("No case studies found in the data directory.")
           return
       
       # Create tabs for different views
       tab1, tab2 = st.tabs(["📊 Case Study Gallery", "🔍 Detailed View"])
       
       with tab1:
           st.markdown("### Available Case Studies")
           
           # Display case studies in a grid
           cols = st.columns(2)
           
           for i, case_file in enumerate(case_study_files):
               try:
                   with open(case_file, 'r', encoding='utf-8') as f:
                       case_data = json.load(f)
                   
                   with cols[i % 2]:
                       # Create a card for each case study
                       with st.container():
                           st.markdown(f"""
                           <div class="metric-card">
                               <h3>🎯 {case_data.get('business_name', case_file.stem)}</h3>
                               <p><strong>Type:</strong> {case_data.get('business_type', 'N/A')}</p>
                               <p><strong>Market:</strong> {case_data.get('target_market', 'N/A')}</p>
                               <p><strong>Analysis Date:</strong> {case_data.get('analysis_time', 'N/A')}</p>
                           </div>
                           """, unsafe_allow_html=True)
                           
                           # Show business description if available
                           if 'business_description' in case_data:
                               with st.expander("📝 Business Description"):
                                   st.markdown(case_data['business_description'][:300] + "..." if len(case_data['business_description']) > 300 else case_data['business_description'])
                           
                           # Load case study button
                           if st.button(f"📖 Load Case Study", key=f"load_{case_file.stem}"):
                               load_case_study_data(case_data)
                               st.success(f"✅ Loaded case study: {case_data.get('business_name', case_file.stem)}")
                               st.info("💡 Navigate to DREAM Analysis page to view the loaded analysis results.")
               
               except Exception as e:
                   st.error(f"Error loading case study {case_file.name}: {e}")
       
       with tab2:
           st.markdown("### Detailed Case Study Analysis")
           
           # Dropdown to select case study
           case_study_options = {}
           for case_file in case_study_files:
               try:
                   with open(case_file, 'r', encoding='utf-8') as f:
                       case_data = json.load(f)
                   case_study_options[case_data.get('business_name', case_file.stem)] = case_data
               except:
                   continue
           
           if case_study_options:
               selected_case = st.selectbox(
                   "Select a case study to view:",
                   options=list(case_study_options.keys())
               )
               
               if selected_case:
                   case_data = case_study_options[selected_case]
                   display_case_study_details(case_data)
   
   except Exception as e:
       st.error(f"Error loading case studies: {e}")

def load_case_study_data(case_data):
   """Load case study data into session state"""
   try:
       # Set basic information
       st.session_state.example_business_name = case_data.get('business_name', '')
       st.session_state.example_business_type = case_data.get('business_type', 'SaaS平台')
       st.session_state.example_target_market = case_data.get('target_market', '中国大陆')
       st.session_state.example_loaded = case_data.get('business_description', '')
       
       # Load DREAM analysis results if available
       if 'dream_analysis' in case_data:
           st.session_state.dream_results = {
               'business_name': case_data.get('business_name', ''),
               'business_type': case_data.get('business_type', ''),
               'analysis_time': case_data.get('analysis_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
               'results': case_data['dream_analysis']
           }
       elif 'results' in case_data:
           # Handle different JSON structure
           st.session_state.dream_results = {
               'business_name': case_data.get('business_name', ''),
               'business_type': case_data.get('business_type', ''),
               'analysis_time': case_data.get('analysis_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
               'results': case_data['results']
           }
   except Exception as e:
       st.error(f"Error loading case study data: {e}")

def display_case_study_details(case_data):
   """Display detailed view of a case study"""
   
   # Basic information
   col1, col2, col3 = st.columns(3)
   with col1:
       st.metric("Business Name", case_data.get('business_name', 'N/A'))
   with col2:
       st.metric("Business Type", case_data.get('business_type', 'N/A'))
   with col3:
       st.metric("Target Market", case_data.get('target_market', 'N/A'))
   
   # Business description
   if 'business_description' in case_data:
       st.markdown("### 📝 Business Description")
       st.markdown(case_data['business_description'])
   
   # DREAM Analysis Results
   dream_data = case_data.get('dream_analysis') or case_data.get('results')
   if dream_data:
       st.markdown("### 🎯 DREAM Analysis Results")
       
       # Create tabs for each DREAM component
       dream_tabs = st.tabs([
           "📊 Demand", "💡 Resolution", "💰 Earning", "📈 Acquisition", "🏰 Moat"
       ])
       
       components = ['demand', 'resolution', 'earning', 'acquisition', 'moat']
       component_names = ['Demand (需求分析)', 'Resolution (解决方案)', 'Earning (商业模式)', 'Acquisition (增长策略)', 'Moat (竞争壁垒)']
       
       for i, (tab, component, name) in enumerate(zip(dream_tabs, components, component_names)):
           with tab:
               st.markdown(f"#### {name}")
               
               if component in dream_data:
                   result = dream_data[component]
                   
                   # Handle different data structures
                   if isinstance(result, dict):
                       if 'analysis' in result:
                           content = result['analysis']
                       else:
                           content = str(result)
                   else:
                       content = str(result)
                   
                   # Process and display content
                   if content:
                       processed_content, think_blocks = process_think_tags(content)
                       display_content_with_think_blocks(processed_content, think_blocks)
                   else:
                       st.info(f"{name} analysis not available")
               else:
                   st.info(f"{name} analysis not available")
   
   # Load button
   st.markdown("---")
   if st.button("📖 Load This Case Study", type="primary"):
       load_case_study_data(case_data)
       st.success(f"✅ Loaded case study: {case_data.get('business_name', 'Unknown')}")
       st.info("💡 Navigate to DREAM Analysis page to view the loaded analysis results.")

if __name__ == "__main__":
   main()
