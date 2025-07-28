# BabyCareAI Deployment Guide

## 🚀 Streamlit Community Cloud Deployment

### Prerequisites
1. GitHub account
2. OpenRouter API key (get from https://openrouter.ai/)
3. Streamlit Community Cloud account (https://share.streamlit.io/)

### Step 1: Prepare Your Repository
1. Push your baby-care-ai project to GitHub
2. Ensure all files are committed, especially:
   - `streamlit_app.py`
   - `requirements.txt`
   - `app/` directory with all modules
   - `config/` directory
   - `data/` directory with knowledge base

### Step 2: Deploy to Streamlit Community Cloud
1. Go to https://share.streamlit.io/
2. Click "New app"
3. Connect your GitHub repository
4. Set the following:
   - **Repository**: your-username/baby-care-ai
   - **Branch**: main (or your default branch)
   - **Main file path**: streamlit_app.py
   - **App URL**: choose a custom URL (optional)

### Step 3: Configure Secrets
1. In your Streamlit app dashboard, go to "Settings" → "Secrets"
2. Add the following secrets:

```toml
[llm]
LLM_PROVIDER = "openrouter"
OPENROUTER_API_KEY = "your_actual_api_key_here"
OPENROUTER_MODEL = "qwen/qwen3-14b:free"
```

### Step 4: Deploy
1. Click "Deploy!"
2. Wait for the deployment to complete
3. Your app will be available at the provided URL

## 🏠 Local Development

### Option 1: Using OpenRouter (Recommended for Development)
1. Set environment variables:
```bash
export LLM_PROVIDER=openrouter
export OPENROUTER_API_KEY=your_api_key
export OPENROUTER_MODEL=qwen/qwen3-14b:free
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run Streamlit app:
```bash
streamlit run streamlit_app.py
```

### Option 2: Using Ollama (Local LLM)
1. Install and start Ollama:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull qwen3:8b

# Start Ollama service
ollama serve
```

2. Set environment variables:
```bash
export LLM_PROVIDER=ollama
```

3. Run the application:
```bash
streamlit run streamlit_app.py
```

## 📁 Project Structure for Deployment

```
baby-care-ai/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt          # Python dependencies
├── DEPLOYMENT.md            # This file
├── .streamlit/
│   └── secrets.toml         # Secrets template
├── app/
│   ├── __init__.py
│   ├── llm_provider.py      # LLM provider (OpenRouter/Ollama)
│   ├── chain.py             # Baby care chain logic
│   ├── rag_engine.py        # RAG engine for knowledge retrieval
│   └── prompt_templates/
│       └── baby_care_prompts.py
├── config/
│   ├── ollama_config.yaml   # Configuration file
│   └── custom_prompt.txt    # Custom prompts
├── data/
│   ├── knowledge/           # Knowledge base (Markdown files)
│   ├── faq/                # FAQ files
│   └── vectordb/           # Vector database (auto-generated)
└── api/                    # FastAPI routes (optional)
```

## 🔧 Configuration Options

### LLM Models
You can use different models by changing the `OPENROUTER_MODEL` setting:

**Free Models:**
- `qwen/qwen3-14b:free`
- `meta-llama/llama-3-8b-instruct:free`
- `microsoft/phi-3-mini-128k-instruct:free`

**Paid Models (better quality):**
- `anthropic/claude-3-haiku`
- `openai/gpt-3.5-turbo`
- `openai/gpt-4o-mini`

### Knowledge Base
- Add your own knowledge files to `data/knowledge/` (Markdown format)
- Add FAQ files to `data/faq/` (Text format)
- The system will automatically build the vector database

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure all dependencies are in `requirements.txt`
   - Check that all import paths are correct

2. **OpenRouter API errors**
   - Verify your API key is correct
   - Check your OpenRouter account has sufficient credits
   - Try a different model if the current one is unavailable

3. **ChromaDB SQLite compatibility issues**
   - **Fixed**: This project includes automatic SQLite compatibility fixes
   - The system uses `pysqlite3-binary` to provide compatible SQLite version
   - If ChromaDB fails, the system automatically falls back to simple mode
   - See `CHROMADB_FIX.md` for technical details

4. **Vector database issues**
   - Delete the `data/vectordb/` directory to force rebuild
   - Check that knowledge files exist in `data/knowledge/` and `data/faq/`
   - The system will work without vector database (simple mode)

5. **Streamlit deployment fails**
   - Check the logs in Streamlit Community Cloud
   - Ensure all files are committed to GitHub
   - Verify secrets are configured correctly

### Performance Optimization

1. **For faster responses:**
   - Use smaller models like `qwen/qwen3-14b:free`
   - Reduce the number of retrieved documents in RAG

2. **For better quality:**
   - Use paid models like `anthropic/claude-3-haiku`
   - Increase the chunk size in vector database

## 📞 Support

If you encounter issues:
1. Check the Streamlit Community Cloud logs
2. Verify your OpenRouter API key and credits
3. Ensure all required files are in your GitHub repository
4. Test locally first before deploying

## 🔄 Updates

To update your deployed app:
1. Make changes to your local code
2. Commit and push to GitHub
3. Streamlit Community Cloud will automatically redeploy

## 🌟 Features

The deployed BabyCareAI includes:
- 💬 **Smart Q&A**: AI-powered parenting advice
- 👶 **Baby Profiles**: Manage multiple baby profiles
- 📚 **Knowledge Base**: Search parenting knowledge
- 📊 **Usage Stats**: Track your usage
- 🌐 **Bilingual**: Supports Chinese and English
- 🔒 **Secure**: Uses OpenRouter API for privacy

Enjoy your BabyCareAI deployment! 🍼✨