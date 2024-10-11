import streamlit as st
import requests
import uuid
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("URL_PROD", None) # prod url or os.getenv("URL_TEST") for test url
supabase_url = os.getenv("SUPABASE_URL", None)
supabase_api_secret = os.getenv("SUPABASE_API_SECRET", None)

supabase: Client = create_client(supabase_url, supabase_api_secret)

def generate_session_id():
    return str(uuid.uuid4())
    
def send_message_to_n8n_chain(session_id, user_input, rag_mode, tune_mode, token):
    print(token)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "sessionId": session_id,
        "chatInput": user_input,
        "ragMode": rag_mode,
        "tuneMode": tune_mode
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Response json: {response.json()}")
        if isinstance(response.json(), list):
            output_val = response.json()[-1].get("output", None)
            text_val = response.json()[-1].get("text", None)
            
        elif isinstance(response.json(), dict):
            output_val = response.json().get("output", None)
            text_val = response.json().get("text", None)
        
        else:
            return "Sorry, we are having a problem... Try back in a few moments."

        return max(output_val, text_val, key=len) if output_val and text_val else output_val or text_val
            # return "Our servers are unstable at the moment. Please contact the administrator."
    else:
        return f"Error: {response.status_code} - {response.text}"

def login_user(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            return res, None
        return None, "Invalid credentials. Please check your email and password"
    except Exception as e:
        return None, str(e)
    
def signup_user(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            return res, None
        return None, "Sign up failed. Please try again."
    except Exception as e:
        return None, str(e)

def main():
    st.set_page_config(layout="wide", page_title="FinBot", page_icon="💵")

    if "user" not in st.session_state:
        st.session_state.user = None

    if "session_id" not in st.session_state:
        st.session_state.session_id = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.sidebar.title("User Info")
    if st.session_state.user:
        st.sidebar.success(f"Logged in as: {st.session_state.user.user.email}")
        st.sidebar.info(f"Session ID {st.session_state.session_id}")

        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.session_state.messages = []
            st.rerun()
    else:
        st.sidebar.info("Plase log in or sign up")

    if not st.session_state.user:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            st.header("Login", divider="red")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", use_container_width=True):
                if not email or not password:
                    st.error("Please provide both email and password")
                else:
                    with st.spinner("Logging in..."):
                        user_auth, error = login_user(email, password)
                        if user_auth:
                            st.session_state.user = user_auth
                            st.session_state.session_id = generate_session_id()
                            st.success("Logged in successfully!")
                            st.rerun()
                        else:
                            st.error(error)

        with tab2:
            st.header("Sign Up", divider="red")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            if st.button("Sign Up", use_container_width=True):
                if not email or not password:
                    st.error("Please provide both email and password")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    with st.spinner("Signing up..."):
                        user_auth, error = signup_user(email, password)
                        if user_auth:
                            st.session_state.user = user_auth
                            st.session_state.session_id = generate_session_id()
                            st.success("Signed up successfully!")
                            st.rerun()
                        else:
                            st.error(error)

    else:
        
        st.header("FinBot 💵", divider="green")
        col1, col2, col3, col4, col5 = st.columns(5)

        rag_mode = col1.toggle("RAG mode", help="Enable rag for augmented knowledge.")
        tune_mode = col2.toggle("Fine-tune mode", help="Enable fine-tuning for another kind of knowledge source.")
        print(f"rag: {rag_mode}")
        print(f"fine-tune: {tune_mode}")

        # if "messages" in st.session_state:
        for message in st.session_state.messages:
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.markdown(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.markdown(message['content'])

        if user_input := st.chat_input("Escreva sua mensagem aqui..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.spinner("Pensando..."):
                llm_response = send_message_to_n8n_chain(st.session_state.session_id, user_input, rag_mode, tune_mode, st.session_state.user.session.access_token)
        
                st.session_state.messages.append({"role": "assistant", "content": llm_response})
                with st.chat_message("assistant"):
                    st.markdown(llm_response)

        if st.sidebar.button("Apagar histórico de mensagens"):
            st.session_state.messages = []
            st.session_state.session_id = generate_session_id()
            st.rerun()

if __name__ == "__main__":
    main()
