---
title: NovaPay Assistant
emoji: 💳
colorFrom: teal
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# NovaPay AI Assistant

An intelligent customer-facing chatbot for **NovaPay Technologies**, built with:

- 🤖 **openai-agents SDK** — agentic reasoning and conversation management  
- 🖥️ **Streamlit** — clean, responsive chat UI  
- 🔀 **OpenRouter** — flexible LLM backend (swap models without code changes)  
- 📄 **pypdf** — loads the NovaPay company profile PDF at startup  
- 🐳 **Docker** — consistent environment from dev to HF Spaces  

## Features

- Answers questions about NovaPay's products, services, pricing, and integrations  
- Context-grounded responses — all answers are based on the official company profile  
- Conversation history maintained within the session  
- Quick-start suggestion chips for common questions  

## Environment Variables (HF Spaces Secrets)

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `OPENROUTER_MODEL` | Model to use (default: `openai/gpt-4o-mini`) |

## Local Development

```bash
# 1. Clone
git clone https://github.com/<your-username>/novapay-agent
cd novapay-agent

# 2. Create virtual environment with uv
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
uv pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# Edit .env and paste your OPENROUTER_API_KEY

# 5. Add the PDF
# Copy your NovaPay company profile PDF to:  data/company_profile.pdf

# 6. Run
streamlit run app.py
```