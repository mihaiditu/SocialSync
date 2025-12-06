import streamlit as st
import time
import streamlit.components.v1 as components
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from rag_logic import SocialSyncAgent

# --- PAGE CONFIG ---
st.set_page_config(page_title="SocialSync AI", page_icon="🤝", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .event-card {
        background-color: #f0f2f6;
        border-left: 5px solid #ff4b4b;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        color: #31333F;
    }
    .event-title {
        font-weight: bold;
        font-size: 1.1em;
        color: #000;
    }
    .stChatInput {
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/handshake.png", width=100)
    st.title("SocialSync")
    st.markdown("### The Anti-Loneliness Agent")
    if st.button("Reset Conversation"):
        st.session_state.agent = SocialSyncAgent()
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm SocialSync. I'm here to connect you with your tribe. Tell me, what's on your mind?"}
        ]
        st.session_state.mission_complete = False
        st.rerun()

# --- STATE ---
if "agent" not in st.session_state:
    st.session_state.agent = SocialSyncAgent()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm SocialSync. I'm here to connect you with your tribe. Tell me, what's on your mind?"}
    ]

if "mission_complete" not in st.session_state:
    st.session_state.mission_complete = False

# --- HELPER ---
def format_event_markdown(raw_text):
    lines = raw_text.split('\n')
    info = {}
    for line in lines:
        if ": " in line:
            key, val = line.split(": ", 1)
            info[key.strip()] = val.strip()

    title = info.get("Event", "Unknown Event")
    date = info.get("Date", "TBD")
    loc = info.get("Location", "Check URL")
    cost = info.get("Cost", "Free")
    url = info.get("Source", "#")
    desc = info.get("Description", "")

    return f"""
    <div class="event-card">
        <div class="event-title">🏆 {title}</div>
        <p>📅 <b>When:</b> {date} | 📍 <b>Where:</b> {loc}</p>
        <p>💰 <b>Cost:</b> {cost}</p>
        <p>📝 <i>{desc}</i></p>
        <a href="{url}" target="_blank">🔗 View Event Details</a>
    </div>
    """

# --- MAIN LOOP ---
st.title("🤝 SocialSync AI")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("is_html"):
            st.markdown(msg["content"], unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# SUCCESS STATE
if st.session_state.mission_complete:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.success("🎉 Mission Complete!")
        if st.button("🔄 Start New Search", use_container_width=True, type="primary"):
            st.session_state.agent = SocialSyncAgent()
            st.session_state.messages = [
                {"role": "assistant", "content": "Hi! I'm SocialSync. I'm here to connect you with your tribe. Tell me, what's on your mind?"}
            ]
            st.session_state.mission_complete = False
            st.rerun()

# CHAT INPUT
if prompt := st.chat_input("Type your answer...", disabled=st.session_state.mission_complete):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.agent.chat_history.append(HumanMessage(content=prompt))

    with st.chat_message("assistant"):
        with st.spinner("SocialSync is thinking..."):
            
            ai_response = st.session_state.agent.llm.invoke(st.session_state.agent.chat_history)
            ai_text = ai_response.content
            
            # --- IMPROVED COMMAND DETECTION ---
            # We convert to uppercase to catch "Search_Action" or "search_action"
            # We check if it exists, THEN parse it
            
            if "SEARCH_ACTION" in ai_text.upper():
                # Extract clean query regardless of casing
                try:
                    # Split case-insensitive by replacing header
                    clean_text = ai_text.replace("**SEARCH_ACTION:**", "SEARCH_ACTION:")
                    search_part = clean_text.split("SEARCH_ACTION:")[1].strip()
                    # Remove any leftover brackets
                    search_query = search_part.replace("[", "").replace("]", "")
                    
                    st.info(f"🔎 Searching database for: '{search_query}'...")
                    
                    events = st.session_state.agent.retrieve_events(search_query, k=2)
                    
                    if not events:
                        events = st.session_state.agent.retrieve_events(search_query, k=50)
                        if events: events = [events[0]]

                    if events:
                        for event in events:
                            card = format_event_markdown(event)
                            st.markdown(card, unsafe_allow_html=True)
                            st.session_state.messages.append({"role": "assistant", "content": card, "is_html": True})
                        
                        st.session_state.agent.chat_history.append(AIMessage(content="SEARCH_EXECUTED"))
                        st.session_state.agent.chat_history.append(SystemMessage(content="SYSTEM: Results shown. Ask if user is happy."))
                        
                        follow_up = st.session_state.agent.llm.invoke(st.session_state.agent.chat_history)
                        st.markdown(follow_up.content)
                        st.session_state.messages.append({"role": "assistant", "content": follow_up.content})
                        st.session_state.agent.chat_history.append(follow_up)
                    
                    else:
                        st.error("No matches found.")
                        st.session_state.agent.chat_history.append(SystemMessage(content="SYSTEM: No results. Ask user to refine."))
                        follow_up = st.session_state.agent.llm.invoke(st.session_state.agent.chat_history)
                        st.markdown(follow_up.content)
                        st.session_state.messages.append({"role": "assistant", "content": follow_up.content})
                
                except Exception as e:
                    # Fallback if parsing fails
                    st.error(f"Search Error: {e}")
                    st.markdown(ai_text)

            elif "MISSION_COMPLETE" in ai_text:
                st.balloons()
                final_msg = "Mission Complete! Have fun out there! 🎉"
                st.markdown(final_msg)
                st.session_state.messages.append({"role": "assistant", "content": final_msg})
                st.session_state.mission_complete = True
                st.rerun()

            else:
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
                st.session_state.agent.chat_history.append(ai_response)

# SCROLL SCRIPT
js = f"""
<script>
    function forceScroll() {{
        var body = window.parent.document.querySelector(".main");
        var html = window.parent.document.querySelector("html");
        if (body) body.scrollTop = body.scrollHeight;
        if (html) html.scrollTop = html.scrollHeight;
    }}
    setTimeout(forceScroll, 300);
</script>
"""
components.html(js, height=0, width=0)