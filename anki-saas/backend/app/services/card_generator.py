import json
import re

from app.services.claude import chat_with_claude


GENERATE_PROMPT = """あなたは学習カード生成アシスタントです。
以下の会話内容から、復習用のフラッシュカードを生成してください。

カードの種類:
- vocab: 単語・フレーズ → 意味・例文
- cloze: 穴埋め問題（___で穴を表現）→ 正解
- rewrite: 原文 → 書き換え・言い換え

JSON形式で出力してください:
```json
[
  {"card_type": "vocab", "front": "単語", "back": "意味"},
  {"card_type": "cloze", "front": "これは___です", "back": "テスト"},
  {"card_type": "rewrite", "front": "原文", "back": "書き換え例"}
]
```

重要なポイントだけを3〜5枚程度のカードにしてください。
JSONのみを出力し、説明は不要です。

---
会話内容:
"""


def generate_cards_from_conversation(messages: list[dict]) -> list[dict]:
    conversation_text = "\n".join([
        f"{m['role']}: {m['content']}" for m in messages
    ])

    prompt = GENERATE_PROMPT + conversation_text

    response = chat_with_claude([{"role": "user", "content": prompt}])

    # Extract JSON from response
    json_match = re.search(r'\[.*\]', response, re.DOTALL)
    if json_match:
        cards = json.loads(json_match.group())
        return cards

    return []
