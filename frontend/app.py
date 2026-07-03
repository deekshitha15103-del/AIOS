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


st.title("🤖 AIOS")
st.caption("Enterprise AI Knowledge Assistant")

if "session_id" not in st.session_state:
    st.session_state.session_id = "streamlit-session"

if "document_id" not in st.session_state:
    st.session_state.document_id = None

if "current_filename" not in st.session_state:
    st.session_state.current_filename = None

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.header("📄 Documents")

    uploaded = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded:
        with st.spinner("Processing document..."):
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

            st.success("Uploaded & indexed")
            st.markdown(f"**Filename:** {data['filename']}")
            st.markdown(f"**Status:** `{data.get('status')}`")
            st.markdown(f"**Chunks:** `{data.get('chunk_count')}`")
            st.markdown(f"**Vectors:** `{data.get('vector_count')}`")
        else:
            st.error("Upload failed")
            st.write(response.text)

    st.divider()

    st.subheader("Active Document")

    if st.session_state.document_id:
        st.markdown(f"**File:** {st.session_state.current_filename}")
        st.caption(st.session_state.document_id)
    else:
        st.info("No document uploaded yet.")

    st.divider()

    st.subheader("Current Session")
    st.code(st.session_state.session_id)

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()


st.markdown("### 💬 Chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask anything about your uploaded document...")

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
            result = response.json()["data"]
            answer = result["answer"]

            with st.chat_message("assistant"):
                st.markdown(answer)

                with st.expander("📚 Sources & Citations"):
                    for source in result.get("sources", []):
                        score = source.get("score")
                        semantic_score = source.get("semantic_score")
                        keyword_score = source.get("keyword_score")
                        page_number = source.get("page_number")

                        st.markdown("---")
                        st.markdown(f"### 📌 Source {source['source_number']}")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                "Relevance",
                                f"{relevance_percent(score)}%",
                            )

                        with col2:
                            st.metric(
                                "Chunk",
                                source.get("chunk_index"),
                            )

                        with col3:
                            st.metric(
                                "Page",
                                page_number if page_number else "N/A",
                            )

                        if semantic_score is not None or keyword_score is not None:
                            st.caption(
                                f"Semantic: {round(semantic_score or 0, 3)} | "
                                f"Keyword: {round(keyword_score or 0, 3)}"
                            )

                        st.markdown("**Preview**")
                        st.info(source.get("preview", ""))

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )
        else:
            st.error("Backend error")
            st.write(response.status_code)
            st.write(response.text)