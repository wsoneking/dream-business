# 🚀 AI Agent Project Template Usage Guide

This guide shows you how to use the [`ai_agent_project_template.roo`](ai_agent_project_template.roo) to quickly create new AI agent projects.

## 📋 Template Overview

The template is based on the successful **BabyCareAI** project and includes:
- ✅ Complete tech stack with proven compatibility
- ✅ Production-ready project structure
- ✅ Comprehensive configuration templates
- ✅ Best practices and implementation guidelines
- ✅ Testing and deployment scripts
- ✅ Multilingual support framework

## 🎯 Quick Start Examples

### Example 1: Legal Assistant AI
```yaml
project_name: LegalAdvisorAI
description: |
  An AI legal assistant that helps users understand legal documents, 
  provides basic legal guidance, and answers common legal questions.
  
custom_prompt_template: |
  You are a knowledgeable legal assistant who helps users understand legal concepts and documents.
  
  CRITICAL: Always respond in the SAME LANGUAGE as the user's question.
  
  Your characteristics:
  - Professional and precise in legal terminology
  - Clear in explaining complex legal concepts
  - Careful to distinguish between information and legal advice
  
  Response guidelines:
  1. Use a professional and helpful tone
  2. Provide step-by-step explanations when possible
  3. If questions relate to specific jurisdictions, ask for location details
  4. Always include disclaimers about not replacing professional legal counsel
  5. For complex legal matters, recommend consulting a qualified attorney
  6. End with "Remember, this is general information only. Consult a lawyer for specific legal advice."
```

### Example 2: Fitness Coach AI
```yaml
project_name: FitnessCoachAI
description: |
  A personal fitness AI coach that provides workout plans, nutrition advice,
  and motivation for users at all fitness levels.

custom_prompt_template: |
  You are an experienced and motivating fitness coach who helps people achieve their health goals.
  
  CRITICAL: Always respond in the SAME LANGUAGE as the user's question.
  
  Your characteristics:
  - Energetic and motivational
  - Knowledgeable about exercise science and nutrition
  - Supportive and encouraging
  
  Response guidelines:
  1. Use an enthusiastic and encouraging tone
  2. Provide detailed workout instructions and form tips
  3. If questions relate to fitness level, ask about current activity and goals
  4. Always emphasize safety and proper form
  5. For medical conditions, recommend consulting healthcare providers
  6. End with motivational phrases like "You've got this! Keep pushing forward!"
```

### Example 3: Cooking Assistant AI
```yaml
project_name: CulinaryMasterAI
description: |
  A culinary AI assistant that helps with recipes, cooking techniques,
  meal planning, and dietary accommodations.

custom_prompt_template: |
  You are a skilled culinary expert who loves helping people create delicious meals.
  
  CRITICAL: Always respond in the SAME LANGUAGE as the user's question.
  
  Your characteristics:
  - Passionate about food and cooking
  - Knowledgeable about various cuisines and techniques
  - Creative with ingredient substitutions
  
  Response guidelines:
  1. Use a warm and enthusiastic tone about food
  2. Provide detailed cooking instructions and tips
  3. If questions relate to dietary restrictions, ask for specific requirements
  4. Include ingredient alternatives and substitutions
  5. For food safety concerns, emphasize proper handling and storage
  6. End with encouraging phrases like "Happy cooking! Enjoy your delicious creation!"
```

## 🛠️ Customization Steps

### 1. Project Initialization
```bash
# Create your project directory
mkdir your-project-name
cd your-project-name

# Copy the template
cp /path/to/ai_agent_project_template.roo ./project_spec.roo
```

### 2. Template Customization
Edit `project_spec.roo` and replace:
- `[YOUR_PROJECT_NAME]` → Your actual project name
- `[ROLE_DESCRIPTION]` → AI's role (e.g., "legal assistant", "fitness coach")
- `[DOMAIN_EXPERTISE]` → Specific expertise area
- `[PERSONALITY_TRAIT_X]` → Specific personality characteristics
- `[TONE]` and `[STYLE]` → Desired communication style
- `[ENCOURAGING_PHRASE]` → Domain-appropriate encouragement

### 3. Knowledge Base Preparation
```bash
# Create knowledge directories
mkdir -p data/knowledge data/faq

# Add your domain-specific content
# data/knowledge/ - Structured articles and guides
# data/faq/ - Common questions and answers
```

### 4. Configuration Setup
```bash
# Create config directory
mkdir config

# Copy configuration templates from the template
# Customize ollama_config.yaml and custom_prompt.txt
```

## 📁 File Generation Checklist

Based on the template, create these files:

### Core Application Files
- [ ] `app/__init__.py`
- [ ] `app/main.py` (FastAPI application)
- [ ] `app/chain.py` (LangChain integration)
- [ ] `app/rag_engine.py` (RAG implementation)
- [ ] `app/prompt_templates/specialized_prompts.py`

### API Layer
- [ ] `api/__init__.py`
- [ ] `api/routes.py` (API endpoints)

### Configuration
- [ ] `config/ollama_config.yaml`
- [ ] `config/custom_prompt.txt`

### Utilities
- [ ] `requirements.txt`
- [ ] `start.py`
- [ ] `test_system.py`
- [ ] `example_usage.py`
- [ ] `rebuild_vectordb.py`
- [ ] `install_dependencies.py`

### Documentation
- [ ] `README.md`
- [ ] Usage examples
- [ ] API documentation

## 🎯 Domain-Specific Adaptations

### For Technical Domains (Legal, Medical, Financial)
- Add disclaimer templates
- Include regulatory compliance notes
- Emphasize limitations and professional consultation
- Add specialized validation for domain-specific terms

### For Creative Domains (Art, Writing, Music)
- Include inspiration and creativity prompts
- Add style and technique guidance
- Provide examples and references
- Encourage experimentation

### For Educational Domains (Tutoring, Training)
- Include learning progression tracking
- Add assessment and quiz capabilities
- Provide multiple explanation approaches
- Include progress encouragement

## 🔧 Advanced Customizations

### Multi-Agent Systems
```python
# Add to prompt_templates/specialized_prompts.py
SPECIALIST_PROMPTS = {
    "research": "You are a research specialist...",
    "analysis": "You are an analysis expert...",
    "recommendation": "You are a recommendation engine..."
}
```

### Custom API Endpoints
```python
# Add to api/routes.py
@router.post("/domain-specific-endpoint")
async def domain_specific_function(request: CustomRequest):
    # Your domain-specific logic
    pass
```

### Specialized Knowledge Processing
```python
# Add to rag_engine.py
def process_domain_documents(self, documents):
    # Domain-specific document processing
    # E.g., legal document parsing, medical terminology extraction
    pass
```

## 📊 Success Metrics by Domain

### Customer Service AI
- Response accuracy rate
- Customer satisfaction scores
- Resolution time
- Escalation rate

### Educational AI
- Learning outcome improvement
- Student engagement metrics
- Knowledge retention rates
- Completion rates

### Healthcare AI
- Information accuracy
- User safety compliance
- Professional referral rate
- User trust metrics

## 🚀 Deployment Considerations

### Local Development
```bash
# Start Ollama
ollama serve

# Pull your chosen model
ollama pull qwen3:8b

# Start your application
python start.py
```

### Production Deployment
- Use environment variables for configuration
- Implement proper logging and monitoring
- Set up health checks and alerts
- Consider load balancing for high traffic
- Implement backup strategies for vector databases

## 🤝 Community Template Sharing

Consider creating domain-specific template variations:
- `legal_ai_template.roo`
- `healthcare_ai_template.roo`
- `education_ai_template.roo`
- `ecommerce_ai_template.roo`

Each with pre-configured:
- Domain-specific prompts
- Relevant knowledge base structures
- Specialized API endpoints
- Compliance considerations

## 📚 Next Steps

1. **Choose your domain** and customize the template
2. **Gather domain knowledge** for your knowledge base
3. **Test with real users** to refine prompts and responses
4. **Iterate and improve** based on feedback
5. **Scale and deploy** when ready for production

The template provides a solid foundation - your domain expertise and user feedback will make it exceptional! 🎯