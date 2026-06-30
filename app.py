"""
app.py — NovaPay Technologies AI Assistant
==========================================
Single-file app: agent logic (PDF loader, OpenRouter setup, openai-agents
runner) + Streamlit UI all live here.

Local dev:
    streamlit run app.py

Env vars needed:
    OPENROUTER_API_KEY   — your OpenRouter key
    OPENROUTER_MODEL     — e.g. "openai/gpt-4o-mini" (default)
"""

import asyncio
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from agents import Agent, Runner
from pypdf import PdfReader

load_dotenv()  # loads .env when running locally; no-op on HF Spaces

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — AGENT LOGIC
# ══════════════════════════════════════════════════════════════════════════════

# Wire OpenRouter to the openai-agents SDK via standard env vars.
# The SDK reads OPENAI_API_KEY and OPENAI_BASE_URL automatically —
# no custom client or wrapper needed.
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"
os.environ["OPENAI_API_KEY"] = os.getenv("API_TOKEN", "")
os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

if not os.environ["OPENAI_API_KEY"]:
    raise EnvironmentError(
        "OPENROUTER_API_KEY is not set. "
        "Add it to your .env file (local) or HF Space Secrets (deployment)."
    )

# Model to use — swap via env var without touching code.
# See https://openrouter.ai/models for available strings.
MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")


def load_company_context(pdf_path: str) -> str:
    """
    Extracts all text from the NovaPay company profile PDF.
    Returns a single string injected into the agent's system prompt.
    Falls back to a minimal placeholder if the PDF is missing or unreadable.
    """
    try:
        reader = PdfReader(pdf_path)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text.strip())
        full_text = "\n\n".join(pages_text)
        print(f"[novapay] Loaded PDF: {len(full_text)} chars, {len(reader.pages)} pages.")
        return full_text
    except Exception as e:
        print(f"[novapay] Warning — could not read PDF at '{pdf_path}': {e}")
        return "NovaPay Technologies is a fintech company providing payment solutions."


def _build_system_prompt(company_context: str) -> str:
    return f"""You are the official AI assistant for NovaPay Technologies — friendly, \
knowledgeable, and professional.

Your responsibilities:
- Answer questions accurately based solely on the NovaPay company profile below.
- Help users understand NovaPay's products, services, pricing, integrations, and support.
- Maintain a warm, concise, and professional tone at all times.
- If a question goes beyond what's in the profile, don't say the information is missing \
or that the profile doesn't cover it. Instead, smoothly guide the user to NovaPay support \
for that specific detail, as if it's simply the next best step — not a fallback.
- Never fabricate facts, pricing, or features not present in the profile.
- Use bullet points or short paragraphs for readability where helpful.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOVAPAY COMPANY PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{company_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


async def run_agent(
    user_message: str,
    history: list[dict],
    company_context: str,
) -> str:
    """
    Runs one turn of the NovaPay agent.

    Args:
        user_message:    The latest user input.
        history:         Previous chat turns as [{"role": ..., "content": ...}, ...].
        company_context: Full text from the company PDF (injected via system prompt).

    Returns:
        The assistant's reply as a plain string.
    """
    # Build the agent — plain model string, SDK uses set_default_openai_client above
    novapay_agent = Agent(
        name="NovaPay Assistant",
        instructions=_build_system_prompt(company_context),
        model=MODEL,
    )

    # Reconstruct full conversation: history turns + new user message
    input_messages: list[dict] = []
    for msg in history:
        if msg["role"] in ("user", "assistant"):
            input_messages.append({"role": msg["role"], "content": msg["content"]})
    input_messages.append({"role": "user", "content": user_message})

    try:
        result = await Runner.run(novapay_agent, input=input_messages)
        return result.final_output or "I'm sorry, I couldn't generate a response. Please try again."
    except Exception as e:
        print(f"[novapay] Runner error: {e}")
        return (
            "I'm having trouble connecting right now. "
            "Please check back in a moment or contact NovaPay support directly."
        )


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="NovaPay Assistant",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  :root {
    --bg:         #F3F5F8;
    --surface:    #FFFFFF;
    --card:       #FFFFFF;
    --border:     #E2E7EF;
    --ink:        #10151D;
    --muted:      #6B7686;
    --faint:      #98A2B3;
    --blue:       #2451FF;
    --blue-dim:   rgba(36,81,255,0.08);
    --blue-ring:  rgba(36,81,255,0.18);
    --mint:       #00C2A8;
    --user-bg:    #10151D;
    --user-text:  #F3F5F8;
  }

  .stApp { background-color: var(--bg); color: var(--ink); }
  .block-container { padding: 1.4rem 1.2rem 1rem; max-width: 700px; }

  /* ── top bar ── */
  .topbar {
    display: flex; align-items: center; gap: 12px;
    padding: 0.9rem 1.1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    margin-bottom: 1.4rem;
  }
  .topbar-icon {
    width: 38px; height: 38px; border-radius: 10px;
    background: var(--ink);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .topbar-icon svg { width: 18px; height: 18px; }
  .topbar-name { font-family: 'Sora', sans-serif; font-size: 0.95rem; font-weight: 700; color: var(--ink); line-height: 1.2; }
  .topbar-sub  { font-size: 0.72rem; color: var(--muted); margin-top: 2px; }
  .topbar-pill {
    margin-left: auto; font-size: 0.7rem; font-weight: 600; color: var(--mint);
    background: rgba(0,194,168,0.08);
    border: 1px solid rgba(0,194,168,0.25); border-radius: 20px;
    padding: 4px 10px 4px 8px; display: flex; align-items: center; gap: 6px;
    white-space: nowrap;
  }
  .pill-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--mint); animation: blink 2s infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.35} }

  /* ── welcome greeting (shown on empty chat) ── */
  .greeting { padding: 1.6rem 0.4rem 1.2rem; }
  .greeting h2 {
    font-family: 'Sora', sans-serif;
    font-size: 1.5rem; font-weight: 700; color: var(--ink);
    margin: 0 0 0.5rem; letter-spacing: -0.01em;
  }
  .greeting p {
    font-size: 0.86rem; color: var(--muted);
    margin: 0 0 1.3rem; line-height: 1.6; max-width: 480px;
  }

  /* ── suggestion chips ── */
  .chips-label {
    font-size: 0.66rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--faint); margin-bottom: 0.6rem;
  }
  div[data-testid="stButton"] > button {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--ink) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 10px 14px !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    line-height: 1.35 !important;
    min-height: 44px !important;
    height: auto !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: border-color 0.15s ease, background 0.15s ease, transform 0.1s ease !important;
  }
  div[data-testid="stButton"] > button:hover {
    border-color: var(--blue) !important;
    background: var(--blue-dim) !important;
    color: var(--blue) !important;
    transform: translateY(-1px);
  }
  div[data-testid="stButton"] > button:active { transform: translateY(0); }

  /* ── chat messages ── */
  [data-testid="stChatMessage"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 0.9rem 1.1rem !important;
    margin-bottom: 0.6rem !important;
    box-shadow: 0 1px 2px rgba(16,21,29,0.03);
  }
  [data-testid="stChatMessage"] p { color: var(--ink) !important; font-size: 0.9rem; line-height: 1.6; }

  /* user bubble — darker, aligned visually distinct via avatar background */
  [data-testid="stChatMessageAvatarUser"] {
    background: var(--ink) !important;
  }
  [data-testid="stChatMessageAvatarAssistant"] {
    background: linear-gradient(135deg, var(--blue), var(--mint)) !important;
  }

  /* ── chat input ── */
  [data-testid="stChatInputContainer"] {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 10px rgba(16,21,29,0.04) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }
  [data-testid="stChatInputContainer"]:focus-within {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 4px var(--blue-ring) !important;
  }
  [data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    color: var(--ink) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
  }
  [data-testid="stChatInput"] textarea::placeholder { color: var(--faint) !important; }

  #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Top bar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="topbar-icon">
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 8.5C3 6 5 4 7.5 4H16.5C19 4 21 6 21 8.5V15.5C21 18 19 20 16.5 20H7.5C5 20 3 18 3 15.5V8.5Z" stroke="#F3F5F8" stroke-width="1.6"/>
      <path d="M3 9.5H21" stroke="#F3F5F8" stroke-width="1.6"/>
      <path d="M7 14.5H11" stroke="#00C2A8" stroke-width="1.6" stroke-linecap="round"/>
    </svg>
  </div>
  <div>
    <div class="topbar-name">NovaPay Assistant</div>
    <div class="topbar-sub">Powered by NovaPay Technologies</div>
  </div>
  <div class="topbar-pill">
    <div class="pill-dot"></div> Online
  </div>
</div>
""", unsafe_allow_html=True)

# ── Load company context once (cached across sessions) ─────────────────────────
@st.cache_resource(show_spinner=False)
def get_company_context() -> str:
    pdf_path = Path("resources/NovaPay_Profile.pdf")
    if pdf_path.exists():
        return load_company_context(str(pdf_path))
    return "NovaPay Technologies is a leading fintech payment solutions company."

company_context = get_company_context()

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ── Welcome greeting + suggestion chips (empty chat only) ─────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="greeting">
      <h2>Hi, how can I help you today?</h2>
      <p>I'm the NovaPay AI Assistant. Ask me anything about our products, services,
      pricing, or integrations — I'll answer straight from the NovaPay company profile.</p>
    </div>
    <div class="chips-label">Try asking</div>
    """, unsafe_allow_html=True)

    suggestions = [
        "What services does NovaPay offer?",
        "How do I integrate the payment API?",
        "What are your transaction fees?",
        "Tell me about security features",
        "How do I contact support?",
        "What industries do you serve?",
    ]

    # Two chips per row — fixed-width columns can't fit longer questions on one
    # line, so each row only ever holds two suggestions and text wraps cleanly.
    for i in range(0, len(suggestions), 2):
        row = suggestions[i:i + 2]
        cols = st.columns(2)
        for col, suggestion in zip(cols, row):
            with col:
                if st.button(suggestion, key=f"chip_{suggestions.index(suggestion)}", use_container_width=True):
                    st.session_state.pending_prompt = suggestion
                    st.rerun()

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

# ── Render chat history ────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Handle chip click ──────────────────────────────────────────────────────────
if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = asyncio.run(
                run_agent(prompt, st.session_state.messages[:-1], company_context)
            )
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# ── Chat input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me anything about NovaPay..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = asyncio.run(
                run_agent(prompt, st.session_state.messages[:-1], company_context)
            )
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})