_conversations = {}


def add_message(session_id: str, role: str, content: str):
    if session_id not in _conversations:
        _conversations[session_id] = []

    _conversations[session_id].append(
        {
            "role": role,
            "content": content,
        }
    )


def get_history(session_id: str, limit: int = 8):
    return _conversations.get(session_id, [])[-limit:]


def clear_history(session_id: str):
    if session_id in _conversations:
        del _conversations[session_id]