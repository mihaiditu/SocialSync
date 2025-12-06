import streamlit as st
from dotenv import load_dotenv
from core_logic import clasifica_personalitate, agent_router_response

load_dotenv()

st.set_page_config(page_title="SocialSync AI", page_icon="🤝")

st.title("🤝 SocialSync AI")
st.markdown("### Your Personal Social Assistant")
st.markdown("---")

# --- STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Hi! I'm SocialSync AI. To help you find the best events, I need to get to know you a little bit.\n\n**Tell me, what kind of activities energize you? Do you prefer large, loud groups or smaller, intimate gatherings?**"
    }]
if "personalitate" not in st.session_state:
    st.session_state["personalitate"] = None
if "mod_recomandare" not in st.session_state:
    st.session_state["mod_recomandare"] = False

# --- INFO SIDEBAR ---
with st.sidebar:
    st.header("Profile Status")
    if st.session_state["personalitate"]:
        st.success(f"Personality Type: **{st.session_state['personalitate']}**")
        st.info("You can now ask for recommendations (e.g., 'something under 50 RON' or 'a quiet book club').")
    else:
        st.warning("Assessment in progress... Please answer the chat questions.")
    
    st.markdown("---")
    st.markdown("**How it works:**\n1. You answer a few questions.\n2. The AI determines your social style.\n3. A smart 'Router' decides whether to query the SQL database (for price/dates) or the RAG system (for interests/vibes).")

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- MAIN CHAT LOGIC ---
if prompt := st.chat_input("Type your message here..."):
    # 1. Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Personality Assessment Flow (first 2 exchanges)
    if not st.session_state["mod_recomandare"]:
        user_messages_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        
        if user_messages_count < 2:
            # Follow-up question
            response = "Got it. And what are your main hobbies? What do you usually like to do on weekends?"
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
        
        else:
            # Classification
            with st.chat_message("assistant"):
                with st.spinner("Analyzing your answers to understand your style..."):
                    istoric_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                    tip_personalitate = clasifica_personalitate(istoric_text)
                    
                    st.session_state["personalitate"] = tip_personalitate
                    st.session_state["mod_recomandare"] = True 
                    
                    response = f"All set! Based on what you said, I think you fit best as an: **{tip_personalitate}**.\n\nFrom now on, you can ask for specific recommendations. You can ask about budget (e.g., 'anything free this weekend') or atmosphere (e.g., 'I want a place to meet new people')."
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()

    # 3. Recommendation Flow (Agent Router)
    else:
        with st.chat_message("assistant"):
            status_msg, final_response = agent_router_response(prompt, st.session_state["personalitate"])
            
            st.caption(status_msg) 
            st.markdown(final_response)
            st.session_state.messages.append({"role": "assistant", "content": final_response})