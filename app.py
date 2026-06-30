"""
app.py — NovaPay Technologies AI Assistant
==========================================
"""

import asyncio
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from agents import Agent, Runner
from pypdf import PdfReader

load_dotenv()  # loads .env when running locally

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — AGENT LOGIC
# ══════════════════════════════════════════════════════════════════════════════

# Wire OpenRouter to the openai-agents SDK via standard env vars.
# The SDK reads OPENAI_API_KEY and OPENAI_BASE_URL automatically.
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"
os.environ["OPENAI_API_KEY"] = os.getenv("API_TOKEN", "")
os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

if not os.environ["OPENAI_API_KEY"]:
    raise EnvironmentError(
        "API_TOKEN is not set. "
        "Add it to your .env file (local) or HF Space Secrets (deployment)."
    )

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
    novapay_agent = Agent(
        name="NovaPay Assistant",
        instructions=_build_system_prompt(company_context),
        model=MODEL,
    )

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
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  :root {
    --bg:        #060D1F;
    --surface:   #0B1A30;
    --card:      #0F2340;
    --border:    #163354;
    --teal:      #0ABFA3;
    --teal-dim:  rgba(10, 191, 163, 0.10);
    --teal-glow: rgba(10, 191, 163, 0.22);
    --blue:      #1A6FD4;
    --text:      #DDE8F5;
    --muted:     #4D6E8A;
  }

  .stApp { background-color: var(--bg); color: var(--text); }
  .block-container { padding: 1.5rem 1.5rem 1rem; max-width: 720px; }

  /* ── top bar ── */
  .topbar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
  }
  .topbar-icon {
    width: 40px; height: 40px; border-radius: 10px;
    background: linear-gradient(135deg, var(--teal), var(--blue));
    display: flex; align-items: center; justify-content: center;
    font-size: 1.05rem; color: #fff; font-weight: 700; flex-shrink: 0;
  }
  .topbar-name { font-size: 0.95rem; font-weight: 600; color: var(--text); }
  .topbar-sub  { font-size: 0.68rem; color: var(--muted); margin-top: 1px; }
  .topbar-pill {
    margin-left: auto; font-size: 0.68rem; color: var(--teal);
    border: 1px solid rgba(10, 191, 163, 0.35); border-radius: 20px;
    padding: 3px 10px; display: flex; align-items: center; gap: 5px;
  }
  .pill-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: var(--teal); animation: blink 2s infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

  /* ── welcome greeting (shown on empty chat) ── */
  .greeting { text-align: center; padding: 1.8rem 1rem 1rem; }
  .greeting h2 {
    font-size: 1.3rem; font-weight: 700; color: var(--text);
    margin: 0 0 0.4rem;
  }
  .greeting p {
    font-size: 0.82rem; color: var(--muted);
    margin: 0 0 1.4rem; line-height: 1.7;
  }

  /* ── suggestion chips ── */
  .chips-label {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.07em;
    text-transform: uppercase; color: var(--muted); margin-bottom: 0.5rem;
  }
  div[data-testid="stButton"] > button {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    color: var(--muted) !important;
    font-size: 0.78rem !important;
    font-weight: 400 !important;
    padding: 6px 14px !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    line-height: 1.35 !important;
    transition: border-color 0.15s, color 0.15s, background 0.15s !important;
  }
  div[data-testid="stButton"] > button:hover {
    border-color: var(--teal) !important;
    color: var(--teal) !important;
    background: var(--teal-dim) !important;
  }

  /* ── chat messages ── */
  [data-testid="stChatMessage"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 0.85rem 1rem !important;
    margin-bottom: 0.5rem !important;
  }

  /* ── chat input — bold and visible ── */
  [data-testid="stChatInputContainer"] {
    background: var(--card) !important;
    border: 2px solid var(--teal) !important;
    border-radius: 14px !important;
    box-shadow: 0 0 18px var(--teal-glow) !important;
  }
  [data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
  }
  [data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; }

  #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Top bar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="topbar-icon">N</div>
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
      <h2>👋 Hi, how can I help you?</h2>
      <p>I'm the NovaPay AI Assistant. Ask me anything about our<br>
      products, services, pricing, or integrations.</p>
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

    for i in range(0, len(suggestions), 2):
        row = suggestions[i:i + 2]
        cols = st.columns(2)
        for col, suggestion in zip(cols, row):
            with col:
                if st.button(suggestion, key=f"chip_{suggestions.index(suggestion)}", use_container_width=True):
                    st.session_state.pending_prompt = suggestion
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

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