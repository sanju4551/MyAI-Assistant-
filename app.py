
import re
import streamlit as st
import ollama
from ddgs import DDGS
from google import genai
from calculator import calculate
from profile import load_profile, save_profile

from database import (
    save_message,
    get_messages,
    clear_messages,
    create_conversation,
    get_conversations,
    update_conversation_title,
    delete_conversation
)


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MyAI Assistant",
    page_icon="🤖",
    layout="wide"
)

MODEL_NAME = "qwen3:1.7b"
GEMINI_MODEL = "gemini-3.8-flash"

MAX_INPUT_LENGTH = 5000
MAX_PDF_LENGTH = 12000


# ==========================================
# 2. AI PROVIDER CONFIGURATION
# ==========================================

try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "").strip()
except Exception:
    GEMINI_API_KEY = ""

USE_GEMINI = bool(GEMINI_API_KEY)


def check_ollama_connection():
    try:
        ollama.list()
        return True
    except Exception:
        return False


if USE_GEMINI:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        st.error("Could not initialize Gemini. Check your API key.")
        st.stop()
else:
    gemini_client = None

    if not check_ollama_connection():
        st.error(
            "Ollama is not running. Start Ollama and refresh MyAI, "
            "or configure GEMINI_API_KEY in Streamlit Cloud Secrets."
        )
        st.stop()


def generate_ai_response(messages):
    """
    Generate an answer using Gemini in the cloud
    or Ollama on the local computer.
    """

    if USE_GEMINI:

        conversation_text = ""

        for message in messages:
            role = message["role"]

            if role == "system":
                label = "SYSTEM INSTRUCTIONS"
            elif role == "assistant":
                label = "MYAI"
            else:
                label = "USER"

            conversation_text += (
                f"\n\n{label}:\n{message['content']}"
            )

        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=conversation_text
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        return response.text

    response = ollama.chat(
        model=MODEL_NAME,
        messages=messages
    )

    return response["message"]["content"]


# ==========================================
# 3. WEB SEARCH
# ==========================================

def search_web(query):
    try:
        results = DDGS().text(
            query,
            max_results=5
        )

        search_results = []

        for result in results:
            search_results.append(
                f"Title: {result.get('title', '')}\n"
                f"Link: {result.get('href', '')}\n"
                f"Description: {result.get('body', '')}"
            )

        if not search_results:
            return "No web search results were found."

        return "\n\n".join(search_results)

    except Exception:
        return (
            "Web search is temporarily unavailable. "
            "Please try again later."
        )


# ==========================================
# 4. CALCULATOR DETECTION
# ==========================================

def is_calculation_request(question):

    question = question.lower().strip()

    if re.search(
        r"\d+(?:\.\d+)?\s*%\s*of\s*\d+(?:\.\d+)?",
        question
    ):
        return True

    calculation_words = (
        "calculate",
        "compute",
        "what is",
        "solve",
        "please calculate"
    )

    has_calculation_word = any(
        question.startswith(word)
        for word in calculation_words
    )

    has_math_operator = bool(
        re.search(
            r"[\d)]\s*[\+\-*/%]|\b(sqrt|sin|cos|tan|log)\s*\(",
            question
        )
    )

    is_plain_expression = bool(
        re.fullmatch(
            r"[\d\s.+\-*/()%]+",
            question
        )
    )

    return (
        (has_calculation_word and has_math_operator)
        or is_plain_expression
    )


# ==========================================
# 5. SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """
You are MyAI, an intelligent personal AI assistant.

Your responsibilities:
- Answer questions clearly and accurately.
- Teach Python, SQL and Artificial Intelligence.
- Help users write and debug code.
- Explain difficult concepts simply.
- Be friendly, patient and professional.

Programming rules:
- Put Python code inside proper Markdown code blocks.
- Use correct language identifiers such as python or sql.
- Keep explanations outside code blocks.
- Explain code simply.
- Show expected program output separately.
- Use correct Python indentation.
- When fixing code, show complete corrected code.

When the user provides PDF content:
- Read the provided content carefully.
- Answer questions using that content.
- Do not claim you cannot access the PDF.
- If the answer is not present in the provided content,
  clearly say that it was not found.

When web search results are provided:
- Use the search results to answer the question.
- Prefer relevant and recent information.
- Do not invent facts or sources.
- Include useful source links in your answer.
- If the results do not answer the question, say so.
"""


# ==========================================
# 6. SESSION STATE
# ==========================================

if "profile" not in st.session_state:
    try:
        st.session_state.profile = load_profile()
    except Exception:
        st.session_state.profile = {
            "name": "",
            "learning_goals": [],
            "explanation_style": "Simple and beginner-friendly"
        }

if "conversation_id" not in st.session_state:

    try:
        conversations = get_conversations()

        if conversations:
            st.session_state.conversation_id = conversations[0][0]
        else:
            st.session_state.conversation_id = create_conversation()

        st.session_state.messages = get_messages(
            st.session_state.conversation_id
        )

    except Exception:
        st.error("Could not load chat history. Please check the database.")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""


# ==========================================
# 7. PERSONALIZED SYSTEM PROMPT
# ==========================================

def build_system_prompt():

    profile = st.session_state.profile

    name = profile.get("name", "")
    goals = profile.get("learning_goals", [])

    style = profile.get(
        "explanation_style",
        "Simple and beginner-friendly"
    )

    profile_instructions = f"""

PERSONAL USER PROFILE:

Preferred name: {name if name else "Not provided"}

Learning goals: {", ".join(goals) if goals else "Not provided"}

Preferred explanation style: {style}

PERSONALIZATION RULES:
- Use the preferred name naturally when appropriate.
- Adapt explanations to the user's preferred style.
- Give examples related to learning goals when relevant.
- Be patient and supportive.
- Do not repeatedly mention the profile.
"""

    return SYSTEM_PROMPT + profile_instructions


# ==========================================
# 8. CUSTOM STYLING
# ==========================================

st.markdown("""
<style>

.main-title {
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 0;
}

.subtitle {
    color: gray;
    font-size: 16px;
}

[data-testid="stChatMessage"] {
    border-radius: 15px;
    padding: 16px;
    margin-bottom: 15px;
    border: 1px solid rgba(128, 128, 128, 0.2);
}

[data-testid="stChatMessageContent"] {
    font-size: 16px;
    line-height: 1.7;
}

[data-testid="stChatMessage"] pre {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 9. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🤖 MyAI")
    st.caption("Your personal AI assistant")

    if USE_GEMINI:
        st.success("☁️ Online AI: Gemini")
    else:
        st.success("💻 Local AI: Ollama")

    st.divider()

    # New Chat
    if st.button("＋ New Chat", use_container_width=True):

        try:
            new_id = create_conversation()

            st.session_state.conversation_id = new_id
            st.session_state.messages = []

            st.rerun()

        except Exception:
            st.error("Could not create a new chat.")

    st.divider()

    # Web Search
    st.subheader("🌐 Web Search")

    enable_web_search = st.checkbox(
        "Enable internet search",
        value=False,
        help="When enabled, MyAI searches the internet."
    )

    if enable_web_search:
        st.info("Internet search is enabled.")
    else:
        st.caption("Internet search is currently disabled.")

    st.divider()

    # PDF Reader
    st.subheader("📄 PDF Reader")

    uploaded_pdf = st.file_uploader(
        "Upload a PDF document",
        type=["pdf"],
        key="pdf_uploader"
    )

    if uploaded_pdf is not None:

        try:
            from pypdf import PdfReader

            pdf_reader = PdfReader(uploaded_pdf)

            pdf_text = ""

            for page in pdf_reader.pages:
                pdf_text += (page.extract_text() or "") + "\n"

            st.session_state.pdf_text = pdf_text

            if pdf_text.strip():

                st.success("PDF uploaded successfully!")

                st.caption(
                    f"Extracted {len(pdf_text)} characters"
                )

                with st.expander("View PDF text preview"):
                    st.text(pdf_text[:1000])

            else:
                st.warning(
                    "No readable text found. "
                    "The PDF may be scanned."
                )

        except Exception:
            st.error(
                "Could not read this PDF. "
                "Please check that the file is valid."
            )

    if st.session_state.pdf_text:

        st.success("PDF is ready for questions.")

        if st.button(
            "Remove Uploaded PDF",
            use_container_width=True
        ):
            st.session_state.pdf_text = ""
            st.rerun()

    st.divider()

    # Personal Profile
    st.subheader("👤 My Personal Profile")

    profile = st.session_state.profile

    with st.form("myai_profile_form"):

        user_name = st.text_input(
            "Your preferred name",
            value=profile.get("name", ""),
            max_chars=50,
            placeholder="Enter your name"
        )

        learning_goals = st.text_input(
            "Your learning goals",
            value=", ".join(profile.get("learning_goals", [])),
            max_chars=300,
            placeholder="Python, SQL, AI"
        )

        explanation_options = [
            "Simple and beginner-friendly",
            "Detailed and technical",
            "Short and direct",
            "Step-by-step explanations"
        ]

        current_style = profile.get(
            "explanation_style",
            "Simple and beginner-friendly"
        )

        style_index = (
            explanation_options.index(current_style)
            if current_style in explanation_options
            else 0
        )

        explanation_style = st.selectbox(
            "Preferred explanation style",
            explanation_options,
            index=style_index
        )

        save_profile_button = st.form_submit_button(
            "💾 Save My Profile",
            use_container_width=True
        )

        if save_profile_button:

            updated_profile = {
                "name": user_name.strip(),
                "learning_goals": [
                    goal.strip()
                    for goal in learning_goals.split(",")
                    if goal.strip()
                ],
                "explanation_style": explanation_style
            }

            try:
                save_profile(updated_profile)

                st.session_state.profile = updated_profile

                st.success("Your profile has been saved!")

            except Exception:
                st.error("Could not save your profile.")

    st.divider()

    # Chat History
    st.subheader("💬 Chat History")

    try:
        conversations = get_conversations()

        for conversation_id, title in conversations:

            col1, col2 = st.columns([5, 1])

            with col1:

                if st.button(
                    str(title),
                    key=f"chat_{conversation_id}",
                    use_container_width=True
                ):

                    st.session_state.conversation_id = conversation_id

                    st.session_state.messages = get_messages(
                        conversation_id
                    )

                    st.rerun()

            with col2:

                if st.button(
                    "🗑️",
                    key=f"delete_{conversation_id}"
                ):

                    delete_conversation(conversation_id)

                    remaining = get_conversations()

                    if remaining:

                        st.session_state.conversation_id = remaining[0][0]

                        st.session_state.messages = get_messages(
                            remaining[0][0]
                        )

                    else:

                        new_id = create_conversation()

                        st.session_state.conversation_id = new_id
                        st.session_state.messages = []

                    st.rerun()

    except Exception:
        conversations = []
        st.error("Could not load chat history.")

    st.divider()

    # Rename Current Chat
    st.subheader("✏️ Rename Current Chat")

    current_title = next(
        (
            title
            for chat_id, title in conversations
            if chat_id == st.session_state.conversation_id
        ),
        "New Chat"
    )

    new_title = st.text_input(
        "Enter new chat name",
        value=current_title,
        max_chars=60,
        key=f"rename_chat_title_{st.session_state.conversation_id}"
    )

    if st.button(
        "Save New Name",
        use_container_width=True
    ):

        if new_title.strip():

            try:
                update_conversation_title(
                    st.session_state.conversation_id,
                    new_title.strip()
                )

                st.rerun()

            except Exception:
                st.error("Could not rename this chat.")

        else:
            st.warning("Please enter a chat name.")

    st.divider()

    # Settings
    st.subheader("⚙️ Settings")

    if USE_GEMINI:
        st.write("**AI Model:** Gemini 2.5 Flash")
        st.write("**AI Provider:** Google Gemini")
    else:
        st.write("**AI Model:** Qwen3 1.7B")
        st.write("**AI Provider:** Ollama")

    st.write("**Memory:** SQLite Database")
    st.write("**Web Search:** DuckDuckGo")
    st.write("**Calculator:** Python")

    st.divider()

    # About MyAI
    st.subheader("About MyAI")

    st.write(
        "MyAI helps you learn Python, SQL, "
        "Artificial Intelligence and coding."
    )

    # Clear Current Chat
    if st.button(
        "🗑️ Clear Current Chat",
        use_container_width=True
    ):

        try:
            clear_messages(st.session_state.conversation_id)

            st.session_state.messages = []

            st.rerun()

        except Exception:
            st.error("Could not clear this chat.")


# ==========================================
# 10. AI SMART TOOLS
# ==========================================

st.subheader("🧰 AI Smart Tools")

with st.expander("Open AI Text Tools"):

    tool_choice = st.selectbox(
        "Choose a tool",
        [
            "Text Summarizer",
            "Language Translator",
            "Email Writer",
            "Notes Assistant"
        ]
    )

    tool_input = st.text_area(
        "Enter your text or instructions",
        height=150,
        max_chars=MAX_INPUT_LENGTH,
        placeholder="Type or paste your text here..."
    )

    target_language = ""

    if tool_choice == "Language Translator":

        target_language = st.text_input(
            "Translate into which language?",
            max_chars=50,
            placeholder="Example: Telugu, Hindi, English"
        )

    if st.button("🚀 Run AI Tool"):

        if not tool_input.strip():

            st.warning("Please enter some text first.")

        elif (
            tool_choice == "Language Translator"
            and not target_language.strip()
        ):

            st.warning("Please enter the target language.")

        else:

            if tool_choice == "Text Summarizer":

                instruction = (
                    "Summarize the following text clearly. "
                    "Include the most important points:\n\n"
                    + tool_input
                )

            elif tool_choice == "Language Translator":

                instruction = (
                    f"Translate the following text into "
                    f"{target_language}. Preserve its meaning:\n\n"
                    + tool_input
                )

            elif tool_choice == "Email Writer":

                instruction = (
                    "Write a professional, well-structured email "
                    "based on these instructions:\n\n"
                    + tool_input
                )

            else:

                instruction = (
                    "Organize the following rough notes into clear, "
                    "well-structured notes. Include headings, important "
                    "points, and action items where appropriate:\n\n"
                    + tool_input
                )

            try:

                with st.spinner("MyAI is working..."):

                    response = generate_ai_response([
                        {
                            "role": "system",
                            "content": build_system_prompt()
                        },
                        {
                            "role": "user",
                            "content": instruction
                        }
                    ])

                    st.markdown("### ✨ Result")
                    st.markdown(response)

            except Exception as error:
                st.error(
                    f"AI tool failed: {error}"
                )


# ==========================================
# 11. WELCOME MESSAGE
# ==========================================

if not st.session_state.messages:

    st.markdown("### 👋 Welcome to MyAI!")

    st.write(
        "I'm ready to help you with Python, SQL, "
        "AI projects and everyday questions."
    )


# ==========================================
# 12. DISPLAY CONVERSATION
# ==========================================

for role, content in st.session_state.messages:

    avatar = "🧑‍💻" if role == "user" else "🤖"

    with st.chat_message(role, avatar=avatar):
        st.markdown(content)


# ==========================================
# 13. CHAT INPUT
# ==========================================

prompt = st.chat_input(
    "Ask MyAI anything...",
    max_chars=MAX_INPUT_LENGTH
)


# ==========================================
# 14. PROCESS USER MESSAGE
# ==========================================

if prompt:

    user_input = prompt.strip()

    if not user_input:
        st.warning("Please enter a message.")

    else:

        current_id = st.session_state.conversation_id

        try:

            # Automatically name the conversation
            if not st.session_state.messages:

                title = " ".join(user_input.split())

                if len(title) > 35:
                    title = title[:35].rsplit(" ", 1)[0] + "..."

                update_conversation_title(current_id, title)

            # Save user message
            save_message(
                "user",
                user_input,
                current_id
            )

            st.session_state.messages.append(
                ("user", user_input)
            )

            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(user_input)

            # Generate response
            with st.chat_message("assistant", avatar="🤖"):

                with st.spinner("MyAI is thinking..."):

                    answer = None

                    # Calculator
                    if (
                        is_calculation_request(user_input)
                        and not st.session_state.pdf_text.strip()
                        and not enable_web_search
                    ):

                        calculation_result = calculate(user_input)

                        if not calculation_result.startswith("Sorry"):

                            answer = (
                                f"### 🧮 Calculator Result\n\n"
                                f"**Question:** {user_input}\n\n"
                                f"**Answer:** {calculation_result}"
                            )

                    # Gemini or Ollama AI
                    if answer is None:

                        ai_messages = [
                            {
                                "role": "system",
                                "content": build_system_prompt()
                            }
                        ]

                        # Previous conversation history
                        for role, content in st.session_state.messages[:-1]:

                            ai_messages.append({
                                "role": role,
                                "content": content
                            })

                        # Current question
                        current_question = user_input

                        # PDF content
                        if st.session_state.pdf_text.strip():

                            current_question += f"""

The user has uploaded a PDF document.

Use the following PDF content to answer the question.

PDF CONTENT:
{st.session_state.pdf_text[:MAX_PDF_LENGTH]}

Answer using the PDF content. If the answer is not present,
say so clearly.
"""

                        # Web search
                        if enable_web_search:

                            with st.spinner("Searching the internet..."):

                                web_results = search_web(user_input)

                            current_question += f"""

INTERNET SEARCH RESULTS:

{web_results}

Use these results to answer the user's question.
Include useful source links in your answer.
"""

                        ai_messages.append({
                            "role": "user",
                            "content": current_question
                        })

                        answer = generate_ai_response(ai_messages)

                    # Display answer
                    st.markdown(answer)

            # Save assistant response
            save_message(
                "assistant",
                answer,
                current_id
            )

            st.session_state.messages.append(
                ("assistant", answer)
            )

            st.rerun()

        except Exception as error:
            st.error(
                f"Something went wrong: {error}"
            )
