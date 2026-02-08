"""
Pulse Ecosystem - Web Interface
Built with Streamlit.
"""

import streamlit as st
import time
import threading
from pulse.config import get_default_config
from pulse.core.brain import Brain

# Configure page settings
print("DEBUG: Setting page config...")
st.set_page_config(
    page_title="Pulse AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
print("DEBUG: Page config set.")

# Custom CSS for modern look
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #f0f2f6;
    }
    .user-avatar {
        background-color: #4CAF50;
    }
    .assistant-avatar {
        background-color: #2196F3;
    }
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #1E1E1E;
    }
    .stButton button {
        border-radius: 20px;
    }
    /* ScaleDown badge */
    .sd-badge {
        background-color: #E0F2F1;
        color: #00695C;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_brain():
    """Initialize Brain singleton."""
    config = get_default_config()
    return Brain(config)



# Voice Integration
@st.cache_resource
class VoiceManager:
    def __init__(self):
        self._thread = None
        self._loop = None
        self._stop_event = threading.Event()
        
    def start(self, brain):
        if self._thread and self._thread.is_alive():
            return
            
        from pulse.voice.voice_loop import VoiceLoop
        # We need to ensure we don't block the UI
        # VoiceLoop normally runs in its own thread, but here we manage the high level
        
        self._loop = VoiceLoop(brain, brain.config)
        self._thread = threading.Thread(target=self._loop.start, daemon=True)
        self._thread.start()
        
    def stop(self):
        if self._loop:
            self._loop.stop()
            self._loop = None
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None
            
    def is_running(self):
         return bool(self._loop and self._loop.running)

@st.cache_resource
def get_voice_manager():
    return VoiceManager()

def main():
    print("DEBUG: Entering main()...")
    brain = get_brain()
    print("DEBUG: Brain initialized.")
    voice_manager = get_voice_manager()
    print("DEBUG: VoiceManager initialized.")

    # Sidebar Settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Voice Controls
        st.subheader("🎤 Voice Control")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Start Voice", type="primary", disabled=voice_manager.is_running()):
                voice_manager.start(brain)
                st.rerun()
                
        with col2:
            if st.button("Stop Voice", type="secondary", disabled=not voice_manager.is_running()):
                voice_manager.stop()
                st.rerun()
                
        if voice_manager.is_running():
            st.success("Voice Active (Listening...)")
            st.caption(f"Wake words: {', '.join(brain.config.wake_words)}")
        else:
            st.info("Voice Inactive")

        st.divider()
        
        if brain.config.openrouter_api_key:
             model_options = [
                "arcee-ai/trinity-large-preview:free",
                "google/gemini-2.0-flash-exp:free",
                "mistralai/mistral-7b-instruct:free",
            ]

        selected_model = st.selectbox(
            "Select Model",
            options=model_options,
            index=0,
            help="Choose the OpenRouter model"
        )
        
        # Update config if model changes
        if selected_model != brain.config.default_model:
            brain.config.default_model = selected_model
            brain.llm.default_model = selected_model
        
        st.divider()
        
        # Context Optimization Settings
        st.subheader("🧠 ScaleDown")
        context_opt = st.toggle("Enable Context Optimization", value=True)
        brain.config.enable_context_optimization = context_opt
        
        if context_opt:
            st.code(f"Strategy: Haste + Compress\nRate: {brain.config.compression_rate}", language="text")
            st.success("Context optimization active")
        else:
            st.warning("Sending raw full history")
            
        st.divider()
        
        # Memory actions
        if st.button("Clear Conversation History", type="primary"):
            brain.clear_memory()
            st.session_state.messages = []
            st.rerun()

    # Main Chat Interface
    st.title("🧠 Pulse AI")
    st.caption("High-performance assistant powered by ScaleDown & OpenRouter")

    # --- DB-DRIVEN UI SYNC ---
    # Always fetch latest history from Brain Memory to ensure voice chats show up
    # We use a larger limit to show context
    db_history = brain.memory.get_history(limit=50)
    
    # st.session_state.messages is now just a cache/buffer for the UI render
    # We rebuild it from DB every time to catch external changes (Voice)
    st.session_state.messages = [{"role": msg.role, "content": msg.content} for msg in db_history]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("How can I help you today?"):
        # Add user message to UI immediately (optimistic update)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Show "thinking" indicator if optimization is ON
            if brain.config.enable_context_optimization and len(st.session_state.messages) > 4:
                with st.status("Optimizing context with ScaleDown...", expanded=False) as status:
                    pass
            
            try:
                # Stream response
                # Note: stream_thought handles adding to memory internally
                for chunk in brain.stream_thought(prompt):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                
    # --- AUTO-REFRESH FOR VOICE ---
    # If voice is running, checking for new messages in DB
    if voice_manager.is_running():
        time.sleep(2) # Refresh every 2 seconds
        st.rerun()

if __name__ == "__main__":
    main()
