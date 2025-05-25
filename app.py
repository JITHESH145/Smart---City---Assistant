import streamlit as st
import requests
import json


st.set_page_config(
    page_title="Smart City Assistant 🏙️",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    :root {
        --primary-blue: #007bff;
        --secondary-blue: #0056b3;
        --light-blue-bg: #e6f2ff;
        --user-msg-bg: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        --user-msg-text: #ffffff;
        --assistant-msg-bg: #f1f3f5;
        --assistant-msg-text: #212529;
        --text-color-dark: #212529;
        --text-color-light: #495057;
        --container-bg-overlay: rgba(255, 255, 255, 0.7); 
        --sidebar-bg: rgba(25, 50, 100, 0.8);
        --border-radius-md: 10px;
        --border-radius-lg: 15px;
        --box-shadow-light: 0 4px 8px rgba(0, 0, 0, 0.1);
        --box-shadow-strong: 0 6px 15px rgba(0, 0, 0, 0.15);
        --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    /* Global Styles */
    body {
        font-family: var(--font-family);
        background-color: #e9ecef; 
    }
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1506784983877-45594efa4c88?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"); 
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: var(--sidebar-bg);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem 1rem;
    }
    [data-testid="stSidebar"] h3 {
        color: #ffffff;
        font-weight: 600;
        text-align: center;
        margin-bottom: 1.5rem;
        font-size: 1.4rem;
    }
    [data-testid="stSidebar"] .stButton>button {
        background-color: rgba(255, 255, 255, 0.1);
        color: #f8f9fa;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: var(--border-radius-md);
        margin-bottom: 0.75rem;
        width: 100%;
        text-align: left;
        padding: 0.75rem 1rem;
        font-weight: 500;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background-color: rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.4);
        transform: translateX(3px);
    }

    .main-panel-container {
        display: flex;
        flex-direction: column;
        height: calc(100vh - 4rem); 
        max-height: 95vh;
        margin: 2rem auto; 
        width: 90%;
        max-width: 800px; 
        
        /* Updated background for image and overlay */
        background-image: linear-gradient(var(--container-bg-overlay), var(--container-bg-overlay)), url("/static/266536.jpg");
        background-size: cover;
        background-position: center;
        
        backdrop-filter: blur(5px); /* Adjusted blur for potentially better text-on-image readability */
        -webkit-backdrop-filter: blur(5px);
        border-radius: var(--border-radius-lg);
        box-shadow: var(--box-shadow-strong);
        padding: 1.5rem; 
        overflow: hidden; 
    }

    .app-header {
        text-align: center;
        margin-bottom: 0.75rem;
        flex-shrink: 0; 
        /* Background will be the panel's new background image + gradient */
    }
    .app-header h1 {
        color: var(--primary-blue); /* Keep text colors vibrant */
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 0.25rem;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.1); /* Slight shadow for readability on image */
    }
    .app-header p {
        color: var(--text-color-light);
        font-size: 1.1rem;
        margin-bottom: 0;
        font-weight: 500; /* Slightly bolder for readability */
        text-shadow: 0px 1px 2px rgba(0,0,0,0.05);
    }

    .chat-input-wrapper {
        margin-bottom: 1rem; 
        flex-shrink: 0; 
        /* Background is now transparent to show panel image */
        background-color: transparent; 
    }
    .stChatInputContainer > div {
        background-color: rgba(255, 255, 255, 0.9); /* Make input slightly opaque for focus */
        border-radius: var(--border-radius-md);
        border: 1px solid rgba(0,0,0,0.1); /* Softer border */
        box-shadow: var(--box-shadow-light);
    }
    .stChatInputContainer button {
        background-color: var(--primary-blue) !important;
        color: white !important;
        border-radius: var(--border-radius-md) !important;
    }
     .stChatInputContainer button:hover {
        background-color: var(--secondary-blue) !important;
    }

    .chat-messages-scroll-area {
        flex-grow: 1; 
        overflow-y: auto;
        padding: 0.5rem;
        /* Make this slightly more opaque than transparent panel to differentiate */
        background: rgba(255, 255, 255, 0.8); 
        border-radius: var(--border-radius-md); 
    }

    /* Individual Chat Message Styling (mostly unchanged, ensure readability) */
    .stChatMessage {
        border-radius: var(--border-radius-md);
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.75rem;
        max-width: 75%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.07);
        border: none;
        word-wrap: break-word;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background: var(--user-msg-bg);
        color: var(--user-msg-text);
        margin-left: auto; 
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) .stMarkdown p {
        color: var(--user-msg-text);
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        background-color: var(--assistant-msg-bg); /* This should be opaque enough */
        color: var(--assistant-msg-text);
        margin-right: auto; 
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) .stMarkdown p {
        color: var(--assistant-msg-text);
    }
    
    .stExpander {
        border: 1px solid #dee2e6;
        border-radius: var(--border-radius-md);
        margin-top: 0.5rem;
        background-color: rgba(255,255,255,0.9); /* More opaque for readability */
    }
    .stExpander header {
        font-weight: 500;
        color: var(--primary-blue);
        padding: 0.6rem 1rem !important;
    }

    /* Responsive Adjustments */
    @media (max-width: 768px) {
        .main-panel-container {
            width: 100%; 
            margin: 0;
            height: 100vh; 
            max-height: 100vh;
            border-radius: 0; 
            padding: 1rem; 
            /* Background image settings from above will apply */
        }
        /* .panel-image-banner media query removed */
        
        .app-header h1 {
            font-size: 1.8rem;
        }
        .app-header p {
            font-size: 1rem;
        }
        .chat-messages-scroll-area {
            padding: 0.25rem;
            background: rgba(255, 255, 255, 0.85); /* Slightly more opaque on mobile */
        }
        .stChatMessage {
            max-width: 85%;
        }
    }
</style>
""", unsafe_allow_html=True)


BACKEND_API_URL = "http://localhost:8000/query"

def query_backend(question_text: str):
    """Sends a question to the FastAPI backend and returns the response."""
    try:
        response = requests.post(BACKEND_API_URL, json={"text": question_text})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None
    except json.JSONDecodeError:
        st.error("API Error: Could not decode response.")
        return None


scroll_script = """
<script>
    const chatScrollArea = window.parent.document.querySelector(".chat-messages-scroll-area");
    function scrollToBottom() {
        if (chatScrollArea) {
            chatScrollArea.scrollTop = chatScrollArea.scrollHeight;
        }
    }
    const observer = new MutationObserver((mutationsList) => {
        for(const mutation of mutationsList) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                scrollToBottom();
                break;
            }
        }
    });
    if (chatScrollArea) {
        observer.observe(chatScrollArea, { childList: true });
        setTimeout(scrollToBottom, 100); // Initial scroll attempt
    }
    window.addEventListener('message', event => {
        if (event.data.type === 'streamlit:rerun') {
            setTimeout(scrollToBottom, 100);
        }
    });
</script>
"""

def main():
    
    with st.sidebar:
        st.markdown("### Sample Questions 💡")
        example_questions = [
            "How do I apply for a building permit?", "What are the library hours?",
            "When is garbage pickup in Zone A?", "How much does a business license cost?",
            "Emergency contact numbers?", "How to report a pothole?",
            "Public transportation options?", "Pay water bill online?"
        ]
        for question in example_questions:
            if st.button(question, key=f"sample_{question}"):
                st.session_state.messages = [{"role": "user", "content": question}]
                st.session_state.processed_latest_user_message = False
                st.rerun()

    
    st.markdown('<div class="main-panel-container">', unsafe_allow_html=True)

    
    st.markdown("""
    <div class="app-header">
        <h1>Smart City Assistant 🏙️</h1>
        <p>Your one-stop for city services. Ask me anything!</p>
    </div>
    """, unsafe_allow_html=True)

    
    st.markdown('<div class="chat-input-wrapper">', unsafe_allow_html=True)
    prompt = st.chat_input("Ask your question here...", key="main_chat_input")
    st.markdown('</div>', unsafe_allow_html=True)

    
    st.markdown('<div class="chat-messages-scroll-area">', unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "sources" in message and message["sources"]:
                with st.expander("View Sources"):
                    for source in message["sources"]:
                        st.markdown(f"- {source['title']} ({source['category']})")
    st.markdown('</div>', unsafe_allow_html=True) 

    st.markdown('</div>', unsafe_allow_html=True) 
    if st.session_state.messages:
        st.components.v1.html(scroll_script, height=0)

    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.processed_latest_user_message = False
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and not st.session_state.get("processed_latest_user_message", False):
        with st.spinner("Fetching information..."):
            user_query = st.session_state.messages[-1]["content"]
            response_data = query_backend(user_query)
            if response_data and "answer" in response_data:
                st.session_state.messages.append({"role": "assistant", "content": response_data["answer"], "sources": response_data.get("sources", [])})
            elif response_data: # If no "answer" key but response_data exists, it might be an API error formatted differently
                 st.session_state.messages.append({"role": "assistant", "content": "Sorry, I received an unexpected response from the information service.", "sources": []})
            else: # response_data is None (e.g. connection error handled by query_backend)
                st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't connect to the information service. Please try again later.", "sources": []})
            st.session_state.processed_latest_user_message = True
            st.rerun()

if __name__ == "__main__":
    
    if 'processed_latest_user_message' not in st.session_state:
        st.session_state.processed_latest_user_message = False
    main() 