import requests
import streamlit as st


API = "http://127.0.0.1:8000/api/v1"


st.set_page_config(
    page_title="AIOS",
    page_icon="🤖",
    layout="wide",
)


def relevance_percent(score):
    if score is None:
        return 0
    return max(0, min(100, int(score * 100)))


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
    }

    [data-testid="stSidebar"] {
        background-color: #0f172a;
    }

    .source-card {
        background-color: #0f172a;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #334155;
        margin-bottom: 16px;
    }

    .small-muted {
        color: #9ca3af;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if "session_id" not in st.session_state:
    st.session_state.session_id = "streamlit-session"

if "document_id" not in st.session_state:
    st.session_state.document_id = None

if "current_filename" not in st.session_state:
    st.session_state.current_filename = None

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.title("🤖 AIOS")
    st.caption("Enterprise Knowledge Assistant")

    st.divider()

    st.markdown("### 📄 Upload Document")

    uploaded = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if uploaded:
        with st.spinner("Indexing document..."):
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
            st.session_state.current_filename = data["filename"]

            st.success("Document indexed successfully")
            st.markdown(f"**File:** {data['filename']}")
            st.markdown(f"**Status:** `{data.get('status')}`")
            st.markdown(f"**Chunks:** `{data.get('chunk_count')}`")
            st.markdown(f"**Vectors:** `{data.get('vector_count')}`")
        else:
            st.error("Upload failed")
            st.write(response.text)

    st.divider()

    st.markdown("### ⚙️ System")
    st.markdown("**Model:** Llama 3.2")
    st.markdown("**Retriever:** FAISS + BM25")
    st.markdown("**Backend:** FastAPI")
    st.markdown("**Frontend:** Streamlit")

    st.divider()

    st.markdown("### 💬 Session")
    st.code(st.session_state.session_id)

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


st.title("🤖 AIOS Enterprise")
st.caption("Production-style AI Knowledge Assistant with Hybrid Retrieval + Source Grounding")


left, right = st.columns([0.72, 0.28])


with left:
    st.markdown("## 💬 Conversation")

    if not st.session_state.document_id:
        st.info("Upload a PDF from the sidebar to start asking questions.")

    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"

        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

            if message["role"] == "assistant" and message.get("sources"):
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        score = source.get("score")
                        semantic_score = source.get("semantic_score")
                        keyword_score = source.get("keyword_score")
                        page_number = source.get("page_number")

                        st.markdown(
                            f"""
                            <div class="source-card">
                            <h4>📌 Source {source["source_number"]}</h4>
                            <p><b>📖 Page:</b> {page_number if page_number else "N/A"}</p>
                            <p><b>🧩 Chunk:</b> {source.get("chunk_index")}</p>
                            <p><b>⭐ Relevance:</b> {relevance_percent(score)}%</p>
                            <p><b>Semantic:</b> {round(semantic_score or 0, 3)}
                            &nbsp;&nbsp; <b>Keyword:</b> {round(keyword_score or 0, 3)}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        st.info(source.get("preview", ""))

    prompt = st.chat_input("Ask anything about your uploaded document...")


with right:
    st.markdown("## 📌 Active Document")

    if st.session_state.document_id:
        st.markdown(f"**File:** {st.session_state.current_filename}")
        st.caption(st.session_state.document_id)
    else:
        st.warning("No document selected.")

    st.markdown("---")

    st.markdown("### 🧠 Capabilities")
    st.markdown("- PDF ingestion")
    st.markdown("- Hybrid retrieval")
    st.markdown("- Source citations")
    st.markdown("- Conversation memory")
    st.markdown("- Local LLM inference")

    st.markdown("---")

    st.markdown("### ⚙️ Stack")
    st.markdown("**Backend:** FastAPI")
    st.markdown("**Frontend:** Streamlit")
    st.markdown("**LLM:** Llama 3.2 via Ollama")
    st.markdown("**Search:** FAISS + BM25")


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

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        body = {
            "session_id": st.session_state.session_id,
            "document_id": st.session_state.document_id,
            "question": prompt,
            "top_k": 3,
        }

        with st.spinner("AIOS is retrieving context and generating an answer..."):
            response = requests.post(
                f"{API}/knowledge/ask",
                json=body,
                timeout=600,
            )

        if response.status_code == 200:
            result = response.json()["data"]

            assistant_message = {
                "role": "assistant",
                "content": result["answer"],
                "sources": result.get("sources", []),
            }

            st.session_state.messages.append(assistant_message)

            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(result["answer"])

                with st.expander("📚 Sources"):
                    for source in result.get("sources", []):
                        score = source.get("score")
                        semantic_score = source.get("semantic_score")
                        keyword_score = source.get("keyword_score")
                        page_number = source.get("page_number")

                        st.markdown(
                            f"""
                            <div class="source-card">
                            <h4>📌 Source {source["source_number"]}</h4>
                            <p><b>📖 Page:</b> {page_number if page_number else "N/A"}</p>
                            <p><b>🧩 Chunk:</b> {source.get("chunk_index")}</p>
                            <p><b>⭐ Relevance:</b> {relevance_percent(score)}%</p>
                            <p><b>Semantic:</b> {round(semantic_score or 0, 3)}
                            &nbsp;&nbsp; <b>Keyword:</b> {round(keyword_score or 0, 3)}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        st.info(source.get("preview", ""))
        else:
            st.error("Backend error")
            st.write(response.status_code)
            st.write(response.text)