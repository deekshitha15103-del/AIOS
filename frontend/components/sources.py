import streamlit as st


def confidence(score):
    if score is None:
        return 0

    return max(0, min(int(score * 100), 100))


def render_sources(sources):
    if not sources:
        return

    with st.expander("📚 Sources", expanded=False):

        for source in sources:

            st.markdown("---")

            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(
                    f"""
### 📄 Source {source["source_number"]}

**Chunk:** `{source["chunk_index"]}`
"""
                )

            with col2:
                st.metric(
                    "Confidence",
                    f"{confidence(source.get('score'))}%"
                )

            if source.get("page_number"):
                st.caption(f"📖 Page {source['page_number']}")

            if source.get("semantic_score") is not None:
                st.progress(
                    min(source["semantic_score"], 1.0),
                    text="Semantic Match"
                )

            if source.get("keyword_score") is not None:
                st.progress(
                    min(source["keyword_score"], 1.0),
                    text="Keyword Match"
                )

            st.info(source["preview"])