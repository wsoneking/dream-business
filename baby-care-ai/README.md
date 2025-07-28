# 🍼 BabyCareAI 育儿顾问系统

基于 Ollama 本地大模型和 LangChain 构建的智能育儿助手，为新手父母提供专业、温暖的育儿指导。

## ✨ 系统特色

- 🤖 **智能问答**：基于 RAG 技术，结合本地知识库提供专业育儿建议
- 👶 **个性化服务**：支持宝宝信息记录，提供针对性建议
- 🔒 **隐私保护**：本地部署，数据安全可控
- 📖 **知识丰富**：涵盖新生儿护理、喂养、睡眠、健康等各个方面
- 🌟 **温暖贴心**：专业的育儿顾问语调，给予父母信心和支持

## 🛠️ 技术栈

- **Python 3.8+**
- **LangChain** - LLM 应用开发框架
- **Ollama** - 本地大模型部署
- **FastAPI** - 高性能 Web 框架
- **ChromaDB** - 向量数据库
- **Sentence Transformers** - 文本嵌入模型

## 📋 系统要求

### 必需组件
1. **Ollama** - 本地大模型运行环境
2. **Python 3.8+**
3. **至少 8GB RAM**（推荐 16GB）
4. **至少 10GB 磁盘空间**

### 推荐模型
- `qwen3:8b` (推荐，支持中英文)
- `llama3`
- `mistral`

## 🚀 快速开始

### 1. 安装 Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# 下载并安装 https://ollama.ai/download
```

### 2. 拉取模型

```bash
# 拉取 Qwen3 模型（推荐）
ollama pull qwen3:8b

# 或者拉取其他模型
ollama pull llama3
ollama pull mistral
```

### 3. 启动 Ollama 服务

```bash
ollama serve
```

### 4. 克隆项目并安装依赖

```bash
git clone <repository-url>
cd baby-care-ai

# 方法1: 使用安装脚本（推荐）
python install_dependencies.py

# 方法2: 手动安装
pip install -r requirements.txt
```

### 5. 启动系统

```bash
# 推荐方式：使用启动脚本
python start.py

# 或者直接运行
python app/main.py
```

系统将在 `http://localhost:8000` 启动

**注意：请确保在项目根目录（baby-care-ai/）下运行命令，不要在子目录中运行。**

## 📁 项目结构

```
baby-care-ai/
├── app/                          # 应用核心代码
│   ├── main.py                   # FastAPI 主应用
│   ├── chain.py                  # LangChain 链管理
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
│   ├── ollama_config.yaml        # Ollama 配置
│   └── custom_prompt.txt         # 自定义提示词
├── requirements.txt              # Python 依赖
└── README.md                     # 项目说明
```

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

- [ ] 支持用户创建宝宝档案
- [ ] 对接微信小程序/网页聊天窗口
- [ ] 加入语音输入/输出
- [ ] 多 Agent 协同支持
- [ ] 支持图片识别（宝宝症状图片）
- [ ] 成长记录和里程碑提醒
- [ ] 社区问答功能

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