import json
import re

from app.services.claude import chat_with_claude


LOOKUP_PROMPT = """あなたは英語学習アシスタントです。
以下の英単語/フレーズの意味を日本語で説明してください。

単語: {word}
{context_line}

以下のJSON形式で回答してください（JSONのみ、説明不要）:
```json
{{
  "word": "単語",
  "meaning": "日本語での意味（簡潔に）",
  "pronunciation": "発音記号（あれば）",
  "example": "例文（英語）"
}}
```
"""


def lookup_word(word: str, context: str = None) -> dict:
    """
    単語の意味を Claude API で取得
    """
    context_line = f"文脈: {context}" if context else ""
    prompt = LOOKUP_PROMPT.format(word=word, context_line=context_line)

    response = chat_with_claude([{"role": "user", "content": prompt}])

    # Extract JSON from response
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return {
                "word": data.get("word", word),
                "meaning": data.get("meaning", ""),
                "pronunciation": data.get("pronunciation"),
                "example": data.get("example")
            }
        except json.JSONDecodeError:
            pass

    # Fallback: return raw response as meaning
    return {
        "word": word,
        "meaning": response.strip(),
        "pronunciation": None,
        "example": None
    }
