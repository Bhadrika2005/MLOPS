import streamlit as st
import os
import shutil
import warnings
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


st.set_page_config(
    page_title="BakeGPT – Your AI Baking Assistant",
    page_icon="🍰",
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Nunito:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background: #FFF8F2; }
#MainMenu, header, footer { visibility: hidden; }
.block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; max-width: 820px !important; }

.bg-icons { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.bg-icon  { position: absolute; font-size: 2.2rem; opacity: 0.08; animation: float 8s ease-in-out infinite; }
.bg-icon:nth-child(1){top:8%;left:4%;animation-delay:0s;font-size:2.8rem;}
.bg-icon:nth-child(2){top:18%;left:88%;animation-delay:1.2s;font-size:2rem;}
.bg-icon:nth-child(3){top:45%;left:6%;animation-delay:2.4s;font-size:2.5rem;}
.bg-icon:nth-child(4){top:65%;left:90%;animation-delay:0.8s;font-size:3rem;}
.bg-icon:nth-child(5){top:80%;left:12%;animation-delay:3.1s;font-size:2.2rem;}
.bg-icon:nth-child(6){top:30%;left:50%;animation-delay:1.7s;font-size:1.8rem;}
.bg-icon:nth-child(7){top:88%;left:70%;animation-delay:2s;font-size:2.6rem;}
.bg-icon:nth-child(8){top:55%;left:78%;animation-delay:0.5s;font-size:2rem;}
@keyframes float{0%,100%{transform:translateY(0px) rotate(-3deg);}50%{transform:translateY(-14px) rotate(3deg);}}

.hero-wrap{text-align:center;padding:2.5rem 1rem 1.5rem;position:relative;z-index:1;}
.hero-cake{font-size:4rem;display:block;margin-bottom:0.2rem;}
.hero-title{font-family:'Playfair Display',serif;font-size:3.2rem;font-weight:900;letter-spacing:-1px;line-height:1;margin:0;padding:0;}
.hero-title .bake{color:#2B1A0F;}.hero-title .gpt{color:#E8651A;}
.hero-heart{color:#E8651A;font-size:1rem;display:block;margin:0.3rem 0;}
.hero-sub{color:#7A6255;font-size:1.05rem;font-weight:600;letter-spacing:0.5px;margin-top:0.2rem;}
.hero-sub span{color:#E8651A;font-weight:700;}

.msg-row{display:flex;margin-bottom:1.1rem;align-items:flex-end;gap:0.6rem;position:relative;z-index:1;}
.msg-row.user{flex-direction:row-reverse;}
.msg-row.bot{flex-direction:row;}
.avatar{width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0;}
.avatar.bot{background:linear-gradient(135deg,#E8651A,#F5A05A);}
.avatar.user{background:linear-gradient(135deg,#2B1A0F,#5C3D2E);color:#fff;font-size:0.72rem;font-weight:700;}
.bubble{padding:0.8rem 1.15rem;border-radius:18px;max-width:80%;font-size:0.95rem;line-height:1.65;box-shadow:0 2px 12px rgba(0,0,0,0.07);}
.bubble.bot{background:#FFFFFF;border-bottom-left-radius:4px;color:#2B1A0F;}
.bubble.user{background:linear-gradient(135deg,#E8651A,#F5863A);border-bottom-right-radius:4px;color:#fff;}

.stTextInput>div>div>input{
    background:#1C1410 !important;color:#F5E6D8 !important;
    border:2px solid #3A2618 !important;border-radius:50px !important;
    padding:0.85rem 1.5rem !important;font-size:1rem !important;
    font-family:'Nunito',sans-serif !important;
    box-shadow:0 4px 24px rgba(232,101,26,0.18) !important;
    caret-color:#E8651A;}
.stTextInput>div>div>input::placeholder{color:#8A7060 !important;}
.stTextInput>div>div>input:focus{border-color:#E8651A !important;box-shadow:0 4px 28px rgba(232,101,26,0.35) !important;outline:none !important;}

.stButton>button{
    background:linear-gradient(135deg,#E8651A,#F5863A) !important;
    color:white !important;border:none !important;border-radius:50% !important;
    width:48px !important;height:48px !important;font-size:1.3rem !important;
    cursor:pointer !important;box-shadow:0 4px 16px rgba(232,101,26,0.4) !important;
    padding:0 !important;margin-top:0.1rem !important;}
.stButton>button:hover{transform:scale(1.08) !important;box-shadow:0 6px 20px rgba(232,101,26,0.55) !important;}

hr{border:none;border-top:1px solid #F0DDD0;margin:0.5rem 0;}

.thinking{display:flex;align-items:center;gap:6px;color:#B07050;font-size:0.88rem;
          font-style:italic;padding:0.4rem 0.8rem;position:relative;z-index:1;}
.dot{width:7px;height:7px;border-radius:50%;background:#E8651A;display:inline-block;
     animation:bounce 1.2s ease-in-out infinite;}
.dot:nth-child(2){animation-delay:0.2s;}.dot:nth-child(3){animation-delay:0.4s;}
@keyframes bounce{0%,80%,100%{transform:scale(0.7);opacity:0.5}40%{transform:scale(1.1);opacity:1}}

.model-badge{text-align:center;color:#B07050;font-size:0.78rem;margin-bottom:0.8rem;position:relative;z-index:1;}
.model-badge span{background:#FFF0E6;border:1px solid #F5C9A0;border-radius:20px;padding:3px 14px;}
</style>

<div class="bg-icons">
  <span class="bg-icon">🥄</span><span class="bg-icon">🎂</span>
  <span class="bg-icon">🍪</span><span class="bg-icon">🥐</span>
  <span class="bg-icon">🍞</span><span class="bg-icon">🧁</span>
  <span class="bg-icon">🎂</span><span class="bg-icon">🍫</span>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero-wrap">
  <span class="hero-cake">🍰</span>
  <h1 class="hero-title"><span class="bake">Bake</span><span class="gpt">GPT</span></h1>
  <span class="hero-heart">♥</span>
  <p class="hero-sub">Your <span>AI Baking</span> Assistant</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="model-badge"><span>✨ Powered by Google Gemini</span></div>', unsafe_allow_html=True)


if not GEMINI_API_KEY:
    st.error(
        "❌ **GEMINI_API_KEY not found.**\n\n"
        "Add this line to your `.env` file:\n"
        "```\nGEMINI_API_KEY=your_key_here\n```\n"
        "Get a free key at: https://aistudio.google.com/app/apikey"
    )
    st.stop()


genai.configure(api_key=GEMINI_API_KEY)

@st.cache_resource(show_spinner=False)
def get_gemini_model():
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=genai.GenerationConfig(
            temperature=0.4,
            max_output_tokens=8192,
        )
    )

model = get_gemini_model()


@st.cache_resource(show_spinner=False)
def load_vector_store():
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        import tempfile

        base      = os.path.dirname(os.path.abspath(__file__))
        faiss_src = os.path.join(base, "index.faiss")
        pkl_src   = os.path.join(base, "index.pkl")

        if not (os.path.exists(faiss_src) and os.path.exists(pkl_src)):
            print(f"FAISS files not found at: {base}")
            return None

        # Use platform-safe temp directory (works on Windows too)
        tmp_dir = os.path.join(tempfile.gettempdir(), "faiss_store")
        os.makedirs(tmp_dir, exist_ok=True)
        shutil.copy(faiss_src, os.path.join(tmp_dir, "index.faiss"))
        shutil.copy(pkl_src,   os.path.join(tmp_dir, "index.pkl"))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vs = FAISS.load_local(
                tmp_dir, embeddings,
                allow_dangerous_deserialization=True
            )
            print("Vector store loaded successfully!")
            return vs
    except Exception as e:
        print(f"Vector store error: {e}")
        return None

vs = load_vector_store()

def retrieve_context(query: str, k: int = 4) -> str:
    if vs is None:
        return ""
    try:
        docs = vs.similarity_search(query, k=k)
        return "\n\n".join(d.page_content for d in docs)
    except Exception:
        return ""


SYSTEM_PROMPT = """You are BakeGPT, a warm and expert AI Baking Assistant.

MOST IMPORTANT RULE — TOPIC RESTRICTION:
You ONLY answer questions about baking. If the user asks ANYTHING not related to baking (coding, weather, sports, general knowledge, etc.), reply EXACTLY this:
"Sorry, I am BakeGPT and I specialize only in baking topics — cakes, pastries, breads, cookies, brownies, cupcakes, muffins, and baking techniques. Ask me anything about baking! 🍰"

BAKING TOPICS YOU COVER:
Cakes, Brownies, Cookies, Bread, Pastries, Cupcakes, Muffins, Macarons, Croissants,
Baking temperatures & times, Ingredient substitutions, Troubleshooting, Recipe scaling, Techniques

═══════════════════════════════════════
RECIPE FORMAT (always follow this exactly):
═══════════════════════════════════════
🍰 [Recipe Name]

📋 Ingredients:
• [ingredient] — [quantity]
• ...

👨‍🍳 Instructions:
1. [Clear step]
2. [Clear step]
...

🌡️ Baking Temperature: [°C / °F]
⏰ Baking Time: [minutes]
🍽️ Servings: [number]

💡 Pro Tip: [one genuinely useful tip]

═══════════════════════════════════════
WHEN USER GIVES INGREDIENTS:
═══════════════════════════════════════
Suggest the best possible recipe, then:
✅ Ingredients you have: [list]
❌ Ingredients you need: [list]
Then give full recipe with temperature and time.

═══════════════════════════════════════
TROUBLESHOOTING FORMAT:
═══════════════════════════════════════
🔍 Possible Causes:
• ...

🛠️ How to Fix It:
• ...

✅ Prevention Tips:
• ...

═══════════════════════════════════════
SUBSTITUTION FORMAT:
═══════════════════════════════════════
🔄 Substitutes for [ingredient]:
• [Option 1] — [ratio and usage note]
• [Option 2] — [ratio and usage note]

═══════════════════════════════════════
GREETING (hi / hello / hey / good morning / good evening):
═══════════════════════════════════════
👋 Hello! Welcome to BakeGPT.
I'm your AI Baking Assistant.

I can help you with:
🎂 Cake Recipes  🍫 Brownies  🍪 Cookies  🍞 Bread Making
🌡️ Baking Temperatures  🧈 Ingredient Substitutions  🔧 Troubleshooting

How can I help you today?

RULES:
- Never invent ingredients or quantities
- Never guess temperatures or times — write "Not Specified" if unknown
- Never mention: FAISS, vector database, context, PDF, knowledge base, or Gemini
- Always be warm, friendly, and easy to understand
- Use emojis and formatting to make answers visually clear and readable
- Keep answers concise but complete"""

# ── Gemini chat function ───────────────────────────────────────────────────────
def chat_with_gemini(history: list, user_query: str, context: str) -> str:
    """Send full conversation to Gemini and return reply."""
    try:
        # Build full prompt with system + context + history
        full_system = SYSTEM_PROMPT
        if context:
            full_system += f"\n\n[Relevant baking reference material:\n{context}\n]"

        # Convert history to Gemini format (exclude last user msg — sent separately)
        gemini_history = []
        for msg in history[:-1]:  # all except the last user message
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        # Start chat with history
        chat = model.start_chat(history=gemini_history)

        # Inject system prompt into the first message if no history
        if not gemini_history:
            prompt = f"{full_system}\n\nUser: {user_query}"
        else:
            prompt = user_query

        response = chat.send_message(prompt)
        return response.text

    except Exception as e:
        return f"⚠️ Gemini error: {e}"


if "messages"   not in st.session_state:
    st.session_state.messages   = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "last_input" not in st.session_state:
    st.session_state.last_input = ""


if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;color:#B07050;font-size:0.92rem;
                padding:3rem 1rem 2rem;position:relative;z-index:1;">
      👇 Ask me anything about baking!<br><br>
      <em>"Give me a chocolate fudge brownie recipe"</em><br>
      <em>"Why did my bread not rise?"</em><br>
      <em>"What can I substitute for eggs?"</em>
    </div>""", unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        import re
        raw = msg["content"]
        # Convert markdown to HTML
        raw = re.sub(r"###\s*(.+)", r"<h4 style='margin:0.6rem 0 0.2rem;font-size:1rem;'>\g<1></h4>", raw)
        raw = re.sub(r"\*\*(.+?)\*\*", r"<strong>\g<1></strong>", raw)
        raw = re.sub(r"\*(.+?)\*", r"<em>\g<1></em>", raw)
        raw = re.sub(r"^[-\*]\s+(.+)", r"• \g<1>", raw, flags=re.MULTILINE)
        text = raw.replace("\n", "<br>")
        if msg["role"] == "assistant":
            st.markdown(
                f'<div class="msg-row bot">'
                f'<div class="avatar bot">🍰</div>'
                f'<div class="bubble bot">{text}</div></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="msg-row user">'
                f'<div class="bubble user">{text}</div>'
                f'<div class="avatar user">You</div></div>',
                unsafe_allow_html=True
            )

    if st.session_state.processing:
        st.markdown("""
        <div class="thinking">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          &nbsp;BakeGPT is thinking…
        </div>""", unsafe_allow_html=True)

# Spacer
st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)


col1, col2 = st.columns([10, 1])
with col1:
    user_input = st.text_input(
        label="", placeholder="Ask any baking question...",
        key="user_input", label_visibility="collapsed",
    )
with col2:
    send = st.button("↑", key="send_btn")


if (send or bool(user_input)) and user_input.strip() and not st.session_state.processing:
    query = user_input.strip()
    if query != st.session_state.last_input:
        st.session_state.last_input = query
        st.session_state.messages.append({"role": "user", "content": query})
        st.session_state.processing = True
        st.rerun()

if st.session_state.processing:
    msgs = st.session_state.messages
    if msgs and msgs[-1]["role"] == "user":
        query   = msgs[-1]["content"]
        context = retrieve_context(query)
        answer  = chat_with_gemini(msgs, query, context)
        st.session_state.messages.append({"role": "assistant", "content": answer})

    st.session_state.processing = False
    st.rerun()