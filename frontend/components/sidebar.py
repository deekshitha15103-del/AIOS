import streamlit as st

from frontend.services.api_client import upload_document


def render_sidebar():
    st.sidebar.title("🤖 AIOS")

    st.sidebar.caption("Enterprise Knowledge Assistant")

    st.sidebar.divider()

    uploaded = st.sidebar.file_uploader(
        "Upload PDF",
        type=["pdf"],
    )

    if uploaded:
        with st.spinner("Indexing document..."):
            response = upload_document(uploaded)

        if response.status_code == 200:
            data = response.json()["data"]

            st.session_state.document_id = data["document_id"]
            st.session_state.current_filename = data["filename"]

            st.sidebar.success("Document indexed successfully")

            st.sidebar.markdown("---")

            st.sidebar.markdown("### 📄 Current Document")

            st.sidebar.write(data["filename"])

            st.sidebar.write(f"Chunks: {data['chunk_count']}")

            st.sidebar.write(f"Vectors: {data['vector_count']}")

        else:
            st.sidebar.error("Upload failed")
            st.sidebar.write(response.text)

    st.sidebar.divider()

    st.sidebar.markdown("### ⚙️ System")

    st.sidebar.write("Model: Llama 3.2")

    st.sidebar.write("Retriever: Hybrid")

    st.sidebar.write("Embedding: MiniLM")

    st.sidebar.divider()

    if st.sidebar.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()