import requests
import streamlit as st


API = "http://127.0.0.1:8000/api/v1"


st.set_page_config(
    page_title="AIOS",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AIOS")
st.caption("Enterprise AI Operating System")

if "session_id" not in st.session_state:
    st.session_state.session_id = "streamlit-session"

if "document_id" not in st.session_state:
    st.session_state.document_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


uploaded = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded:
    with st.spinner("Uploading and processing document..."):
        files = {
            "file": (
                uploaded.name,
                uploaded.getvalue(),
                "application/pdf",
            )
        }

        response = requests.post(
            f"{API}/knowledge/documents/upload",
            files=files,
            timeout=600,
        )

    if response.status_code == 200:
        data = response.json()["data"]
        st.session_state.document_id = data["document_id"]

        st.success("Document uploaded successfully!")
        st.write("Document ID:", st.session_state.document_id)
        st.write("Status:", data.get("status"))
    else:
        st.error("Upload failed.")
        st.write(response.status_code)
        st.write(response.text)


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


prompt = st.chat_input("Ask your document...")

if prompt:
    if not st.session_state.document_id:
        st.warning("Please upload a PDF first.")
    else:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        body = {
            "session_id": st.session_state.session_id,
            "document_id": st.session_state.document_id,
            "question": prompt,
            "top_k": 3,
        }

        with st.spinner("AIOS is thinking..."):
            response = requests.post(
                f"{API}/knowledge/ask",
                json=body,
                timeout=600,
            )

        if response.status_code == 200:
            result = response.json()
            answer = result["data"]["answer"]

            with st.chat_message("assistant"):
                st.markdown(answer)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

            with st.expander("Sources"):
                for source in result["data"].get("sources", []):
                    st.markdown(f"**Source {source['source_number']}**")
                    st.write("Score:", source["score"])
                    st.write("Chunk:", source["chunk_index"])
                    st.write(source["preview"])
        else:
            st.error("Backend returned an error.")
            st.write("Status Code:", response.status_code)
            st.write("Response:", response.text)