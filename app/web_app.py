import streamlit as st
import requests
import os

# API endpoints for OpenAI (FastAPI) and Mistral (ngrok)
LOCAL_BACKEND_URL = "http://127.0.0.1:8000/api"
MISTRAL_BACKEND_URL = "https://b502-34-125-11-8.ngrok-free.app"

st.set_page_config(page_title="CV Analysis AI", layout="wide")

# Sidebar - Model Selection
st.sidebar.title("AI Model Selection")
model_choice = st.sidebar.radio(
    "Select Processing Model:",
    ["OpenAI (Azure OCR + GPT-4)", "Mistral (PyTesseract + Mistral)"],
    index=0
)

# Map model choice to API parameter
model_api_param = "openai" if "OpenAI" in model_choice else "mistral"

st.title("📄 AI-Powered CV Analyzer")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# File Upload Section
st.subheader("Upload CVs (PDF format)")
uploaded_files = st.file_uploader(
    "Upload one or multiple CVs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files and st.button("Process CVs"):
    st.info("Processing CVs... Please wait.")

    # Select API URL based on the model choice
    process_url = f"{LOCAL_BACKEND_URL}/process_cv" if model_api_param == "openai" else f"{MISTRAL_BACKEND_URL}/process_cv"

    try:
        if model_api_param == "openai":
            files_payload = [("files", (f.name, f, "application/pdf")) for f in uploaded_files]
            response = requests.post(f"{process_url}?model_choice={model_api_param}", files=files_payload)
        else:
            response = requests.post(
                f"{MISTRAL_BACKEND_URL}/process_cv",
                files={"file": uploaded_files[0].getvalue()}  # Send first file as bytes
            )

        if response.status_code == 200:
            st.success("✅ CVs Processed Successfully!")
            results = response.json()["results"]

            for res in results:
                st.subheader(f"📌 {res['filename']}")
                st.text_area("Extracted & Structured CV Data", res["data"], height=250)
        else:
            st.error(f"❌ Error: {response.text}")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")

# Query Section
st.subheader("🔍 Query Processed CVs")
query_text = st.text_input("Enter a query (e.g., 'Who has AI experience?')")

if query_text and st.button("🔎 Search"):
    # Select query API URL based on the model choice
    query_url = f"{LOCAL_BACKEND_URL}/query_cv" if model_api_param == "openai" else f"{MISTRAL_BACKEND_URL}/query_cv"

    try:
        if model_api_param == "openai":
            # Use GET for OpenAI
            response = requests.get(query_url, params={"query": query_text, "model_choice": model_api_param})
        else:
            # Use POST for Mistral
            response = requests.post(query_url, json={"query": query_text})

        if response.status_code == 200:
            ai_response = response.json()["response"]

            # Append query and response to chat history
            st.session_state.chat_history.append(("You", query_text))
            st.session_state.chat_history.append(("AI", ai_response))

            st.success("🎯 Response added to chat!")
        else:
            st.error(f"❌ Query failed: {response.text}")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")

# Display Chat History
st.subheader("💬 Chat History")
for role, message in st.session_state.chat_history:
    if role == "You":
        st.markdown(f" **You:** {message}")
    else:
        st.markdown(f" **AI:** {message}")
