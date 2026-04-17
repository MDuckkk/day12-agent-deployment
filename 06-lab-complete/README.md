# 06-lab-complete MVP

This version is intentionally minimal:
- Streamlit UI only
- one OpenAI model call
- no CrewAI
- no FastAPI backend

## Local run

```powershell
cd 06-lab-complete
Copy-Item .env.example .env.local
```

Fill `.env.local`:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
APP_NAME=DevCoach MVP
MAX_UPLOAD_SIZE_MB=5
```

Run locally:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Or with Docker:

```powershell
docker compose up --build
```

## Railway

Set these variables in Railway:
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `APP_NAME`
- `MAX_UPLOAD_SIZE_MB`

Deploy this folder with the included `Dockerfile` and `railway.toml`.
