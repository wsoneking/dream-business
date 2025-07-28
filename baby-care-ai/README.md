# 🍼 BabyCareAI 育儿顾问系统

基于 OpenRouter/Ollama 和 LangChain 构建的智能育儿助手，为新手父母提供专业、温暖的育儿指导。支持云端部署和本地运行。

## ✨ 系统特色

- 🤖 **智能问答**：基于 RAG 技术，结合本地知识库提供专业育儿建议
- 👶 **个性化服务**：支持宝宝信息记录，提供针对性建议
- 🔒 **隐私保护**：本地部署，数据安全可控
- 📖 **知识丰富**：涵盖新生儿护理、喂养、睡眠、健康等各个方面
- 🌟 **温暖贴心**：专业的育儿顾问语调，给予父母信心和支持

## 🛠️ 技术栈

- **Python 3.8+**
- **LangChain** - LLM 应用开发框架
- **OpenRouter/Ollama** - 云端/本地大模型支持
- **Streamlit** - 现代化 Web 界面
- **FastAPI** - 高性能 API 框架
- **ChromaDB** - 向量数据库
- **Sentence Transformers** - 文本嵌入模型

## 📋 部署选项

### 🌐 云端部署 (推荐)
- **OpenRouter API** - 无需本地GPU，即开即用
- **Streamlit Community Cloud** - 免费托管
- **Python 3.8+**
- **OpenRouter API Key** (免费额度可用)

### 🏠 本地部署
- **Ollama** - 本地大模型运行环境
- **Python 3.8+**
- **至少 8GB RAM**（推荐 16GB）
- **至少 10GB 磁盘空间**

### 推荐模型
**云端 (OpenRouter):**
- `qwen/qwen3-14b:free` (免费)
- `anthropic/claude-3-haiku` (付费)
- `openai/gpt-3.5-turbo` (付费)

**本地 (Ollama):**
- `qwen3:8b` (推荐，支持中英文)
- `llama3`
- `mistral`

## 🚀 快速开始

### 🌐 方式一：Streamlit Web 应用 (推荐)

#### 云端部署到 Streamlit Community Cloud
1. **获取 OpenRouter API Key**
   - 访问 https://openrouter.ai/
   - 注册并获取免费 API Key

2. **部署到 Streamlit Cloud**
   - Fork 本项目到你的 GitHub
   - 访问 https://share.streamlit.io/
   - 连接 GitHub 仓库，选择 `streamlit_app.py`
   - 在 Secrets 中配置：
   ```toml
   [llm]
   LLM_PROVIDER = "openrouter"
   OPENROUTER_API_KEY = "your_api_key_here"
   OPENROUTER_MODEL = "qwen/qwen3-14b:free"
   ```

#### 本地运行 Streamlit
```bash
# 1. 克隆项目
git clone <repository-url>
cd baby-care-ai

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境变量 (OpenRouter)
export LLM_PROVIDER=openrouter
export OPENROUTER_API_KEY=your_api_key_here

# 4. 启动 Streamlit 应用
streamlit run streamlit_app.py
# 或使用启动脚本
python start_streamlit.py
```

应用将在 `http://localhost:8501` 启动

### 🏠 方式二：本地 Ollama + FastAPI

#### 1. 安装 Ollama
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows - 下载安装包
# https://ollama.ai/download
```

#### 2. 拉取模型
```bash
# 拉取 Qwen3 模型（推荐）
ollama pull qwen3:8b

# 启动 Ollama 服务
ollama serve
```

#### 3. 启动 FastAPI 系统
```bash
# 设置本地模式
export LLM_PROVIDER=ollama

# 启动系统
python start.py
```

系统将在 `http://localhost:8000` 启动

## 📁 项目结构

```
baby-care-ai/
├── streamlit_app.py              # 🆕 Streamlit Web 应用 (主要界面)
├── start_streamlit.py            # 🆕 Streamlit 启动脚本
├── DEPLOYMENT.md                 # 🆕 部署指南
├── .streamlit/
│   └── secrets.toml              # 🆕 Streamlit 密钥配置
├── app/                          # 应用核心代码
│   ├── main.py                   # FastAPI 主应用
│   ├── llm_provider.py           # 🆕 统一 LLM 提供商 (OpenRouter/Ollama)
│   ├── chain.py                  # LangChain 链管理 (已更新)
│   ├── rag_engine.py             # RAG 引擎
│   └── prompt_templates/         # 提示词模板
│       └── baby_care_prompts.py
├── api/                          # API 路由
│   └── routes.py
├── data/                         # 数据目录
│   ├── knowledge/                # 知识库文档
│   │   ├── newborn_care.md
│   │   └── pregnancy_preparation.md
│   ├── faq/                      # 常见问题
│   │   └── common_questions.txt
│   └── vectordb/                 # 向量数据库（自动生成）
├── config/                       # 配置文件
│   ├── ollama_config.yaml        # 配置文件 (支持 OpenRouter)
│   └── custom_prompt.txt         # 自定义提示词
├── requirements.txt              # Python 依赖 (已更新)
└── README.md                     # 项目说明
```

## 🌟 新功能特性

### 🖥️ Streamlit Web 界面
- **💬 智能问答**: 现代化聊天界面，支持中英文对话
- **👶 宝宝档案**: 创建和管理多个宝宝的信息档案
- **📚 知识库搜索**: 浏览和搜索育儿知识库
- **📊 使用统计**: 查看使用情况和对话历史
- **🌐 双语支持**: 完整的中英文界面支持

### 🔄 LLM 提供商支持
- **☁️ OpenRouter**: 云端 API，支持多种先进模型
- **🏠 Ollama**: 本地部署，数据完全私有
- **🔄 自动切换**: 根据环境自动选择最佳提供商

## 🔧 配置说明

### Ollama 配置 (`config/ollama_config.yaml`)

```yaml
ollama:
  base_url: "http://localhost:11434"  # Ollama 服务地址
  model: "llama3"                     # 使用的模型
  temperature: 0.7                    # 生成温度
  max_tokens: 2048                    # 最大生成长度

vector_db:
  type: "chromadb"                    # 向量数据库类型
  persist_directory: "./data/vectordb" # 数据库存储路径
  collection_name: "baby_care_knowledge"

embedding:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  chunk_size: 1000                    # 文档分块大小
  chunk_overlap: 200                  # 分块重叠长度
```

## 📚 API 接口

### 主要端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 系统主页 |
| `/docs` | GET | Swagger API 文档 |
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/ask` | POST | 智能问答（RAG） |
| `/api/v1/ask-simple` | POST | 简单问答 |
| `/api/v1/example-questions` | GET | 示例问题 |
| `/api/v1/knowledge-stats` | GET | 知识库统计 |

### 问答接口示例

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "新生儿一天要喂几次奶？",
    "baby_info": {
      "age": "2个月",
      "weight": "5.5kg",
      "gender": "男"
    }
  }'
```

## 📖 使用示例

### 1. 基础问答

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={
        "question": "宝宝哭闹不止怎么办？"
    }
)

result = response.json()
print(result["answer"])
```

### 2. 个性化问答

```python
response = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={
        "question": "我的宝宝睡眠不规律，怎么办？",
        "baby_info": {
            "age": "3个月",
            "weight": "6kg",
            "gender": "女",
            "special_conditions": "早产儿"
        }
    }
)
```

## 🔄 知识库管理

### 添加新知识

1. 在 `data/knowledge/` 目录下添加 Markdown 文件
2. 在 `data/faq/` 目录下添加 TXT 文件
3. 调用重建接口：

```bash
curl -X POST "http://localhost:8000/api/v1/rebuild-knowledge" \
  -H "Content-Type: application/json" \
  -d '{"force_rebuild": true}'
```

### 知识库格式

**Markdown 文件示例：**
```markdown
# 新生儿护理

## 喂养指导
- 母乳喂养每2-3小时一次
- 观察宝宝饥饿信号
...
```

**FAQ 文件示例：**
```
Q: 新生儿一天要喂几次奶？
A: 新生儿通常每2-3小时需要喂一次奶，一天大约8-12次。

Q: 宝宝哭闹不止怎么办？
A: 首先检查是否饿了、尿湿了、太热或太冷...
```

## 🎯 问题分类

系统自动识别问题类型并使用相应的专业提示词：

- **新生儿护理** - 0-3个月宝宝相关问题
- **喂养问题** - 母乳、奶粉、辅食相关
- **睡眠问题** - 睡眠习惯、夜醒等
- **健康问题** - 发烧、咳嗽等症状
- **产前准备** - 孕期、分娩准备
- **情感支持** - 育儿焦虑、心理支持

## 🔍 故障排除

### 常见问题

## 🚀 部署选项

### 🌐 Streamlit Community Cloud (推荐)
- **免费托管**: 无需服务器，直接部署到云端
- **自动更新**: GitHub 推送后自动重新部署
- **HTTPS 支持**: 自动提供安全连接
- **详细指南**: 查看 [DEPLOYMENT.md](DEPLOYMENT.md)

### 🏠 本地部署
- **完全私有**: 数据不离开本地环境
- **自定义配置**: 可调整所有参数
- **离线运行**: 使用 Ollama 本地模型

### 🔧 混合部署
- **本地界面 + 云端模型**: Streamlit 本地运行，使用 OpenRouter API
- **最佳体验**: 结合本地控制和云端性能


1. **Ollama 连接失败**
   ```bash
   # 检查 Ollama 是否运行
   ollama list
   
   # 重启 Ollama 服务
   ollama serve
   ```

2. **模型加载失败**
   ```bash
   # 确认模型已下载
   ollama list
   
   # 重新拉取模型
   ollama pull llama3
   ```

3. **向量数据库错误**
   ```bash
   # 删除并重建向量数据库
   rm -rf data/vectordb
   # 重启应用，系统会自动重建
   ```

4. **内存不足**
   - 使用较小的模型（如 `mistral`）
   - 减少 `chunk_size` 和 `max_tokens`
   - 增加系统内存

## 🚀 部署建议

### 开发环境
```bash
python app/main.py
```

### 生产环境
```bash
# 使用 Gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# 使用 Docker（可选）
docker build -t baby-care-ai .
docker run -p 8000:8000 baby-care-ai
```

## 🔮 未来扩展

- [x] ✅ 支持用户创建宝宝档案 (已完成)
- [x] ✅ 现代化 Web 界面 (Streamlit)
- [x] ✅ 云端部署支持 (OpenRouter)
- [ ] 🔄 语音输入/输出功能
- [ ] 📱 移动端适配优化
- [ ] 🤖 多 Agent 协同支持
- [ ] 📷 图片识别（宝宝症状图片）
- [ ] 📈 成长记录和里程碑提醒
- [ ] 👥 社区问答功能
- [ ] 🔔 智能提醒系统
- [ ] 📊 数据分析和报告

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 💝 致谢

感谢所有为新手父母提供帮助的育儿专家和开发者们。

---

**💝 用心呵护每一个宝宝的成长 💝**

如有问题或建议，请提交 Issue 或联系开发团队。