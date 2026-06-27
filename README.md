# LangChain AI Agent

A full-stack starter project for a LangChain-powered AI assistant. It includes a FastAPI backend, a React/Vite frontend, OpenAI integration, simple local conversation memory, and helper tools for math, file operations, CSV analysis, API calls, web search, and Python execution.

## What This Project Includes

- FastAPI backend for chat requests
- LangChain + OpenAI response generation
- React + Vite frontend chat interface
- Persistent chat memory stored in `backend/data/memory.json`
- Environment-based configuration with `.env`
- Graceful fallback message when no OpenAI key is configured
- Tool routing for common tasks like math, CSV analysis, file reads/writes, API fetches, and code execution

## Project Structure

```text
Langchain_Ai_Agent/
  backend/
    app/
      __init__.py
      main.py          # FastAPI app, chat endpoint, OpenAI/LangChain logic
      tools.py         # Local helper tools
    requirements.txt   # Python dependencies
    data/              # Runtime memory/output data, ignored by git

  frontend/
    src/
      App.jsx          # Main React chat UI
      main.jsx         # React entry point
      styles.css       # App styling
    index.html
    package.json       # Frontend scripts and dependencies
    vite.config.js     # Vite dev server and API proxy

  .env.example         # Example environment variables
  .env                 # Local secrets, ignored by git
  README.md
```

## Requirements

Install these before starting:

- Python 3.11 or newer
- Node.js 18 or newer
- npm
- An OpenAI API key with available billing/quota

Check versions:

```powershell
python --version
node --version
npm --version
```

## Environment Variables

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4o-mini
APP_TITLE=LangChain AI Agent
```

Important:

- Do not paste a real API key into `.env.example`.
- `.env` is ignored by git and is the correct place for secrets.
- Restart the backend after changing `.env`.
- If OpenAI returns `insufficient_quota`, the key is valid but the account/project needs billing or credits.

## Setup

Run these commands from the project root:

```powershell
cd C:\Users\sdkkr\Langchain_Ai_Agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

For macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Install frontend dependencies:

```powershell
cd frontend
npm install
```

## Run The App

You need two terminals: one for the backend and one for the frontend.

### Terminal 1: Start Backend

```powershell
cd C:\Users\sdkkr\Langchain_Ai_Agent\backend
..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Expected output:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

Backend health check:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### Terminal 2: Start Frontend

```powershell
cd C:\Users\sdkkr\Langchain_Ai_Agent\frontend
npm run dev
```

Open the app:

```text
http://localhost:5173
```

The frontend sends `/api/chat` requests to the backend through the Vite proxy in `frontend/vite.config.js`.

## API Endpoints

### Health

```http
GET /health
```

Returns:

```json
{"status":"ok"}
```

### Chat

```http
POST /api/chat
Content-Type: application/json

{
  "message": "Explain this project"
}
```

Returns:

```json
{
  "reply": "..."
}
```

## Useful Test Commands

Test backend import:

```powershell
cd C:\Users\sdkkr\Langchain_Ai_Agent
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'backend'); import app.main; print('backend_import_ok')"
```

Check whether the API key loads without printing it:

```powershell
cd C:\Users\sdkkr\Langchain_Ai_Agent
.\.venv\Scripts\python.exe -c "from pathlib import Path; from dotenv import load_dotenv; import os; load_dotenv(Path('.env')); k=os.getenv('OPENAI_API_KEY','').strip(); print('loaded=', bool(k)); print('prefix=', k[:7]); print('length=', len(k))"
```

Check if port `8000` is already in use:

```powershell
netstat -ano
```

Look for:

```text
127.0.0.1:8000 ... LISTENING ... PID
```

## Troubleshooting

### `OpenAI is not configured yet`

The backend did not find a usable `OPENAI_API_KEY`.

Fix:

1. Confirm `.env` exists in the project root, not inside `backend` or `frontend`.
2. Confirm it contains `OPENAI_API_KEY=...`.
3. Restart the backend.

### `The agent hit an error: Connection error.`

The backend reached the chat logic, but the OpenAI request failed.

Common causes:

- No internet connection
- Firewall/proxy blocking OpenAI
- Invalid OpenAI account/project configuration
- OpenAI quota or billing issue

If a direct OpenAI test returns `insufficient_quota`, add billing/credits or use a key from a project with available quota.

### `Error code: 429` or `insufficient_quota`

The API key is recognized, but the OpenAI account/project has no available quota.

Fix:

1. Open the OpenAI platform billing page.
2. Add billing or credits.
3. Check project usage limits.
4. Restart the backend.

### `[WinError 10013] An attempt was made to access a socket...`

Usually the selected port is blocked or already in use.

Fix option 1: use the already running backend if `8000` is active.

Fix option 2: stop the existing process:

```powershell
Stop-Process -Id <PID>
```

Then restart:

```powershell
cd C:\Users\sdkkr\Langchain_Ai_Agent\backend
uvicorn app.main:app --reload --port 8000
```

Fix option 3: use another port:

```powershell
uvicorn app.main:app --reload --port 8010
```

If you change the backend port, also update the frontend proxy in `frontend/vite.config.js`:

```js
proxy: {
  '/api': 'http://localhost:8010'
}
```

### Frontend says backend is unavailable

Check:

- Backend is running on `http://127.0.0.1:8000`
- Frontend is running on `http://localhost:5173`
- `frontend/vite.config.js` proxy points to the backend port
- Browser console and backend terminal logs for errors

### `ModuleNotFoundError`

The Python dependencies are not installed in the active virtual environment.

Fix:

```powershell
cd C:\Users\sdkkr\Langchain_Ai_Agent
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

## Development Notes

- Backend source: `backend/app/main.py`
- Tool functions: `backend/app/tools.py`
- Frontend source: `frontend/src/App.jsx`
- Frontend styles: `frontend/src/styles.css`
- Runtime memory file: `backend/data/memory.json`

The backend loads environment variables from the project root `.env` file:

```python
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
```

That means `.env` must be located here:

```text
Langchain_Ai_Agent/.env
```

## Security Notes

- Never commit `.env`.
- Keep real API keys out of `.env.example`, screenshots, chats, and public repositories.
- Rotate an API key immediately if it was exposed.
- This starter includes local tool execution features, so review `backend/app/tools.py` before deploying publicly.

## Build For Production

Build the frontend:

```powershell
cd frontend
npm run build
```

Preview the frontend build:

```powershell
npm run preview
```

For production deployment, run the FastAPI backend with a production ASGI server setup and serve the frontend build from a static host or web server.

## Quick Start Summary

```powershell
cd C:\Users\sdkkr\Langchain_Ai_Agent
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Start backend:

```powershell
cd C:\Users\sdkkr\Langchain_Ai_Agent\backend
uvicorn app.main:app --reload --port 8000
```

Start frontend in another terminal:

```powershell
cd C:\Users\sdkkr\Langchain_Ai_Agent\frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```
