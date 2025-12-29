import streamlit as st
import requests

BACKEND = "http://127.0.0.1:8000"

st.title("📄 Multi-PDF Chatbot")

files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
user_id = st.text_input("User ID", "default")

if st.button("Index PDFs"):
    if files:
        requests.post(f"{BACKEND}/upload", files=[("files", f) for f in files], params={"user_id": user_id})
        st.success("Indexed!")

query = st.text_input("Ask a question")

if st.button("Ask"):
    r = requests.post(f"{BACKEND}/ask", params={"q": query, "user_id": user_id})
    st.write(r.json()["answer"])

