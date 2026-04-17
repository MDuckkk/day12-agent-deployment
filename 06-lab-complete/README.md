# 06-lab-complete MVP

This folder now supports two deployment styles:
- `Streamlit` for local run, Docker, Railway, and Render
- `Flask on Vercel` for serverless deployment on Vercel

The AI analysis logic is shared in `analyzer.py`. The Vercel version uses a Flask entrypoint at `api/index.py` because Vercel does not run `streamlit run app.py` as a long-lived app server.

## Environment variables

Create `.env.local` for local development:

```powershell
cd 06-lab-complete
Copy-Item .env.example .env.local
```

Set values:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
APP_NAME=DevCoach MVP
MAX_UPLOAD_SIZE_MB=5
```

## Local run with Streamlit

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Local run with Vercel-compatible Flask app

If you want to test the Vercel version before deploying:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:FLASK_APP="api.index"
flask run
```

Or with Vercel CLI:

```powershell
vercel dev
```

## Deploy to Vercel

### Option 1: Deploy from the Vercel dashboard

1. Push this repository to GitHub.
2. In Vercel, click `Add New -> Project`.
3. Import your repository.
4. Set the project root to `06-lab-complete`.
5. Add these environment variables in Project Settings:
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL`
   - `APP_NAME`
   - `MAX_UPLOAD_SIZE_MB`
6. Deploy.

### Option 2: Deploy with Vercel CLI

Run from inside `06-lab-complete`:

```powershell
npm i -g vercel
vercel
```

When asked:
- link to an existing scope or create a new project
- confirm the current directory is the project to deploy
- keep `06-lab-complete` as the root for this deployment

Then add env vars:

```powershell
vercel env add OPENAI_API_KEY
vercel env add OPENAI_MODEL
vercel env add APP_NAME
vercel env add MAX_UPLOAD_SIZE_MB
vercel --prod
```

## Files added for Vercel

- `api/index.py`: Flask app Vercel can execute as a Python function
- `vercel.json`: rewrites `/` to the Flask entrypoint and trims the deployment bundle

## Docker / Railway / Render

The original Streamlit app remains available:

```powershell
docker compose up --build
```

Railway and Render can still use the existing `Dockerfile`, `railway.toml`, and `render.yaml`.
