import streamlit as st

from frontend.services.api_client import ask_document
from frontend.components.sources import render_sources


def render_chat():
    st.markdown("## 💬 Conversation")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.get("document_id"):
        st.info("Upload a PDF from the sidebar to start asking questions.")

    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"

        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

            if message["role"] == "assistant" and message.get("sources"):
                render_sources(message["sources"])

    prompt = st.chat_input("Ask anything about your uploaded document...")

    if not prompt:
        return

    if not st.session_state.get("document_id"):
        st.warning("Please upload a PDF first.")
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.spinner("AIOS is retrieving context and generating an answer..."):
        response = ask_document(
            session_id=st.session_state.session_id,
            document_id=st.session_state.document_id,
            question=prompt,
            top_k=3,
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
            render_sources(result.get("sources", []))
    else:
        st.error("Backend error")
        st.write(response.status_code)
        st.write(response.text)