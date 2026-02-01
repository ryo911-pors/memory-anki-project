# Anki SaaS MVP

AIチャットで学んだ内容を自動でフラッシュカード化し、SM-2アルゴリズムで復習管理するAPI

## セットアップ

### 1. PostgreSQL起動

```bash
docker-compose up -d
```

### 2. Python環境セットアップ

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 環境変数設定

```bash
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定
```

### 4. マイグレーション実行

```bash
cd backend
alembic upgrade head
```

### 5. テストユーザー作成

```bash
python scripts/create_user.py
# 出力されるAPI Keyをメモ
```

### 6. API起動

```bash
uvicorn app.main:app --reload
```

### 7. フロントエンド起動

```bash
cd frontend
python -m http.server 3000
```

http://localhost:3000 でアクセス

## 画面

| 画面 | URL | 説明 |
|------|-----|------|
| Chat | /index.html | AIチャット → カード生成 |
| Review | /review.html | 今日の復習 (SM-2) |
| Cards | /cards.html | カード一覧 |

## API使用例

### ヘルスチェック

```bash
curl http://localhost:8000/health
```

### チャット

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"message": "Pythonのデコレータについて教えて"}'
```

### カード生成

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"conversation_id": "CONVERSATION_ID"}'
```

### カード承認

```bash
curl -X POST http://localhost:8000/approve \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "conversation_id": "CONVERSATION_ID",
    "cards": [
      {"card_type": "vocab", "front": "デコレータ", "back": "関数を修飾する関数"}
    ]
  }'
```

## Swagger UI

http://localhost:8000/docs
