"""
AnkiConnect API wrapper
AnkiConnect runs on localhost:8765 when Anki is open
"""
import httpx
from typing import Optional


ANKI_CONNECT_URL = "http://localhost:8765"


async def invoke(action: str, **params) -> dict:
    """
    Invoke AnkiConnect API
    """
    request_body = {
        "action": action,
        "version": 6,
        "params": params
    }

    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(ANKI_CONNECT_URL, json=request_body)
        result = response.json()

        if result.get("error"):
            raise Exception(result["error"])

        return result.get("result")


async def check_connection() -> bool:
    """
    Check if Anki is running and AnkiConnect is available
    """
    try:
        result = await invoke("version")
        return result is not None
    except Exception:
        return False


async def get_deck_names() -> list[str]:
    """
    Get list of all deck names
    """
    return await invoke("deckNames")


async def create_deck(deck_name: str) -> int:
    """
    Create a new deck (returns deck ID)
    """
    return await invoke("createDeck", deck=deck_name)


async def add_note(
    deck_name: str,
    front: str,
    back: str,
    tags: Optional[list[str]] = None
) -> int:
    """
    Add a note (card) to Anki
    Returns the note ID
    """
    note = {
        "deckName": deck_name,
        "modelName": "Basic",
        "fields": {
            "Front": front,
            "Back": back
        },
        "options": {
            "allowDuplicate": False,
            "duplicateScope": "deck"
        },
        "tags": tags or ["anki-saas"]
    }

    return await invoke("addNote", note=note)


async def add_notes(notes: list[dict]) -> list[int]:
    """
    Add multiple notes at once
    Returns list of note IDs (None for failed notes)
    """
    anki_notes = []
    for note in notes:
        anki_notes.append({
            "deckName": note.get("deck_name", "Default"),
            "modelName": "Basic",
            "fields": {
                "Front": note["front"],
                "Back": note["back"]
            },
            "options": {
                "allowDuplicate": False,
                "duplicateScope": "deck"
            },
            "tags": note.get("tags", ["anki-saas"])
        })

    return await invoke("addNotes", notes=anki_notes)


async def sync() -> None:
    """
    Trigger Anki sync
    """
    await invoke("sync")
