from collections import deque
from threading import Lock


MAX_HISTORY = 20


_conversations: dict[str, deque] = {}

_lock = Lock()


def add_message(session_id: str, role: str, content: str) -> None:
    """
    Add a message to a conversation.
    Keeps only the latest MAX_HISTORY messages.
    """

    with _lock:
        if session_id not in _conversations:
            _conversations[session_id] = deque(maxlen=MAX_HISTORY)

        _conversations[session_id].append(
            {
                "role": role,
                "content": content.strip(),
            }
        )


def get_history(session_id: str, limit: int = 8) -> list[dict]:
    """
    Returns the latest conversation history.
    """

    with _lock:
        history = _conversations.get(session_id)

        if history is None:
            return []

        return list(history)[-limit:]


def clear_history(session_id: str) -> None:
    """
    Delete a conversation.
    """

    with _lock:
        _conversations.pop(session_id, None)


def get_all_sessions() -> list[str]:
    """
    Returns all active session IDs.
    """

    with _lock:
        return list(_conversations.keys())


def conversation_length(session_id: str) -> int:
    """
    Returns the number of stored messages.
    """

    with _lock:
        history = _conversations.get(session_id)

        if history is None:
            return 0

        return len(history)