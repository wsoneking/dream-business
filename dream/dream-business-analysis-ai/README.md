# 🎯 DREAM Business Analysis AI

专为中国市场设计的智能商业分析AI助手，使用DREAM框架方法论进行全面的商业案例分析。

## 📋 项目概述

DREAM Business Analysis AI 是一个基于人工智能的商业分析系统，结合了结构化的DREAM框架方法论与RAG（检索增强生成）技术，为创业者、投资人和商业专业人士提供全面的、假设驱动的商业评估和战略建议。

### DREAM框架五步法

- **需求 (Demand)**: 目标用户分析、使用场景识别、真实市场需求验证
- **解决方案 (Resolution)**: 价值主张设计、产品内核定义、最小可行解决方案
- **商业模式 (Earning)**: 商业模式可行性、单位经济模型、可持续盈利能力
- **增长 (Acquisition)**: 增长策略、客户获取、规模化机制
- **壁垒 (Moat)**: 竞争优势、进入壁垒、可防御性分析

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Ollama (本地LLM服务)
- 8GB+ RAM (推荐)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd dream-business-analysis-ai
   ```

2. **安装依赖**
   ```bash
   python install_dependencies.py
   # 或手动安装
   pip install -r requirements.txt
   ```

3. **设置Ollama**
   ```bash
   # 安装Ollama: https://ollama.ai/
   ollama serve
   ollama pull qwen2.5:7b
   ```

## 📖 使用步骤

### 1. 更新知识库（如果课程笔记有更新）
```bash
python update_knowledge_base.py
```
此脚本会从 `../class_notes/` 目录读取最新的课程笔记，使用LLM分析生成知识库内容。

### 2. 重建向量数据库（如果data目录有变化）
```bash
python rebuild_vectordb_only.py
```
此脚本会重新构建向量数据库，确保所有知识库文件都被正确索引。

### 3. 启动应用
```bash
python start_streamlit.py
```

### 4. 访问应用
打开浏览器访问：http://localhost:8501

## 🏗️ 项目结构

```
dream-business-analysis-ai/
├── app/                          # 核心应用代码
├── api/                         # API路由和端点
├── config/                      # 配置文件
├── data/                        # 知识库和商业数据
│   ├── frameworks/              # 商业框架和方法论
│   ├── case_studies/            # 真实商业案例
│   ├── templates/               # 商业分析模板
│   └── benchmarks/              # 行业基准和数据
├── tools/                       # 商业分析工具
├── update_knowledge_base.py     # 知识库更新脚本
├── rebuild_vectordb_only.py     # 向量数据库重建脚本
├── start_streamlit.py           # Streamlit应用启动脚本
└── requirements.txt             # Python依赖
```

## 🔧 故障排除

### 常见问题

1. **Ollama连接失败**
   ```bash
   # 检查Ollama状态
   ollama list
   
   # 重启Ollama服务
   ollama serve
   ```

2. **向量数据库初始化失败**
   ```bash
   # 重建向量数据库
   python rebuild_vectordb_only.py
   ```

3. **依赖安装问题**
   ```bash
   # 使用虚拟环境
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   
   pip install -r requirements.txt
   ```

## 📞 支持和联系

- 📧 邮箱: support@dream-business-ai.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/dream-business-ai/issues)

---

**🎯 DREAM Business Analysis AI - 让商业分析更科学、更高效！**