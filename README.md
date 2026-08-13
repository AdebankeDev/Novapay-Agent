---

title: NovaPay Assistant
emoji: 💳
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
------------

# 💳 NovaPay AI Assistant

🚀 **[Live Demo](https://adebankedev-novapay-agent.hf.space)**

An AI-powered customer support assistant built for **NovaPay Technologies**, a fictional fintech company created for an educational bootcamp project.

NovaPay AI Assistant uses an **agentic architecture** to provide context-grounded answers about the company's products, services, pricing, and integrations.

## 🎓 About the Project

This project was developed as part of a **bootcamp focused on AI agents and agentic systems**.

The goal was to build a practical AI application that demonstrates how an LLM-powered agent can interact with company-specific information and provide useful, context-aware responses through a conversational interface.

> **Disclaimer:** NovaPay Technologies is a fictional company created solely for this educational project. It does not represent a real financial institution or service.

## ✨ Features

* 🤖 **Agentic AI Assistant** — powered by the OpenAI Agents SDK
* 📚 **Context-Grounded Responses** — answers are based on the NovaPay company profile
* 💬 **Conversational Interface** — interactive chat experience built with Streamlit
* 🧠 **Conversation History** — maintains context throughout the user's session
* ⚡ **Quick-Start Suggestions** — suggestion chips for common customer questions
* 🔄 **Flexible LLM Backend** — uses OpenRouter, allowing the underlying model to be changed without modifying the application architecture
* 🐳 **Dockerized Application** — packaged for consistent development and deployment
* ☁️ **Cloud Deployment** — deployed and hosted using Hugging Face Spaces

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │      User            │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Streamlit UI     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   OpenAI Agents SDK  │
                    │     AI Agent         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Company Context   │
                    │  NovaPay Profile    │
                    │       PDF            │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      LLM via         │
                    │     OpenRouter       │
                    └──────────────────────┘
```

## 🛠️ Technology Stack

| Technology              | Purpose                                         |
| ----------------------- | ----------------------------------------------- |
| **Python**              | Application development                         |
| **OpenAI Agents SDK**   | Agent creation and conversation management      |
| **OpenRouter**          | LLM API and model access                        |
| **Streamlit**           | User interface                                  |
| **pypdf**               | Extracting content from the company profile PDF |
| **Docker**              | Application containerization                    |
| **Hugging Face Spaces** | Cloud deployment and hosting                    |

## 🔄 How It Works

1. The user sends a question through the Streamlit chat interface.
2. The request is passed to the AI agent built with the OpenAI Agents SDK.
3. The agent uses the NovaPay company profile as its source of context.
4. The request is processed using an LLM accessed through OpenRouter.
5. The agent generates a response grounded in the available company information.
6. The response is returned to the user through the Streamlit interface.
7. Conversation history is maintained throughout the session.

## 📄 Knowledge Source

The assistant is grounded using a **NovaPay company profile PDF** containing information about the fictional company's:

* Products
* Services
* Pricing
* Integrations
* Company information

This allows the assistant to answer questions based on the application's provided context rather than relying entirely on the model's general knowledge.

## 🚀 Deployment

The application is containerized using **Docker** and deployed to **Hugging Face Spaces**.

### Live Application

**https://adebankedev-novapay-agent.hf.space**

The Hugging Face Space is configured to run the Docker application on port `7860`.

## 🔐 Environment Variables

The application requires the following environment variables:

| Variable             | Description                       |
| -------------------- | --------------------------------- |
| `OPENROUTER_API_KEY` | API key used to access OpenRouter |
| `OPENROUTER_MODEL`   | LLM model used by the application |

If `OPENROUTER_MODEL` is not specified, the application uses:

```text
openai/gpt-4o-mini
```

For deployment, these values should be configured as **Hugging Face Space Secrets/Variables** rather than hard-coded into the application.

## 💻 Local Development

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/novapay-agent
cd novapay-agent
```

### 2. Create a virtual environment

Using `uv`:

```bash
uv venv
```

Activate the environment:

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

### 5. Add the company profile

Place the NovaPay company profile PDF in:

```text
data/company_profile.pdf
```

### 6. Run the application

```bash
streamlit run app.py
```

The application will then be available locally through the Streamlit development server.

## 🐳 Running with Docker

Build the Docker image:

```bash
docker build -t novapay-agent .
```

Run the container:

```bash
docker run -p 7860:7860 \
  -e OPENROUTER_API_KEY=your_api_key_here \
  -e OPENROUTER_MODEL=openai/gpt-4o-mini \
  novapay-agent
```

## 🎯 What This Project Demonstrates

This project demonstrates practical experience with:

* Building **LLM-powered applications**
* Developing **AI agents**
* Working with the **OpenAI Agents SDK**
* Integrating third-party LLM APIs
* Grounding AI responses with external knowledge
* Building conversational interfaces
* Managing session-based conversation history
* Containerizing applications with Docker
* Deploying AI applications to the cloud

## 📌 Project Status

**Status: Completed**

The application is currently deployed and available for demonstration.

👉 **[Try NovaPay AI Assistant](https://adebankedev-novapay-agent.hf.space)**

---

### 👩🏽‍💻 Author

Built by **Adebanke Peke** as part of an AI/Agentic Systems bootcamp project.
