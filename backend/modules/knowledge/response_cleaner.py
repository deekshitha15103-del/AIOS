FALLBACK_ANSWER = "I don't know based on the uploaded documents."


def clean_answer(answer: str) -> str:
    cleaned = answer.strip()

    if FALLBACK_ANSWER in cleaned:
        answer_without_fallback = cleaned.replace(FALLBACK_ANSWER, "").strip()

        if len(answer_without_fallback) > 20:
            return answer_without_fallback

    return cleaned