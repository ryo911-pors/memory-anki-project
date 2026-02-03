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


async def get_model_names() -> list[str]:
    """
    Get list of all model (note type) names
    """
    return await invoke("modelNames")


async def find_basic_model() -> str:
    """
    Find a basic model that works for simple Front/Back cards.
    Checks for common names in different languages.
    """
    models = await get_model_names()

    # Common names for basic model in different languages
    basic_names = ["Basic", "基本", "Basic (and reversed card)", "基本（様式カードとその逆）"]

    for name in basic_names:
        if name in models:
            return name

    # Fallback: return first model that exists
    if models:
        return models[0]

    raise Exception("No models found in Anki")


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
    # Find appropriate model name (handles Japanese Anki)
    model_name = await find_basic_model()

    # Determine field names based on model
    # Japanese Anki uses "表面" and "裏面" instead of "Front" and "Back"
    if model_name == "基本":
        fields = {"表面": front, "裏面": back}
    else:
        fields = {"Front": front, "Back": back}

    note = {
        "deckName": deck_name,
        "modelName": model_name,
        "fields": fields,
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
    # Find appropriate model name (handles Japanese Anki)
    model_name = await find_basic_model()

    anki_notes = []
    for note in notes:
        # Determine field names based on model
        if model_name == "基本":
            fields = {"表面": note["front"], "裏面": note["back"]}
        else:
            fields = {"Front": note["front"], "Back": note["back"]}

        anki_notes.append({
            "deckName": note.get("deck_name", "Default"),
            "modelName": model_name,
            "fields": fields,
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
