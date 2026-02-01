from anthropic import Anthropic

from app.config import settings

client = Anthropic(api_key=settings.anthropic_api_key)


def chat_with_claude(messages: list[dict]) -> str:
    """
    messages: [{"role": "user"|"assistant", "content": "..."}]
    """
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=messages
    )
    return response.content[0].text
