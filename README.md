# AURA - Autonomous AI Research Analyst

AURA is an autonomous agent designed to read research papers, Hacker News, and other tech sources, evaluating them against its editorial philosophy ("Don't publish what is merely new. Publish what is consequential.") and posting insightful analysis with memory of its past stances.

## Getting Started

1. Set up the environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Set your `GEMINI_API_KEY` in `.env`

3. Start the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

4. Initialize the agent (once):
```bash
curl -X POST "http://localhost:8000/api/agent/init" \
  -H "Content-Type: application/json" \
  -d '{"persona":{"name":"AURA","domain":"AI Technology Research"}}'
```

5. Open the Dashboard:
Navigate to `http://localhost:8000/` in your browser to view the autonomous research control room, activity timeline, editorial decisions, and feed.

## API Documentation

- `POST /api/agent/init` - Initialize the AURA autonomous worker.
- `GET /api/agent/health` - Retrieve AURA's runtime health, cycle stats, and status.
- `GET /api/agent/decisions?agentId=...` - Retrieve the recent editorial decisions and scores.
- `GET /api/agent/feed?agentId=...` - Retrieve the published posts with rationale and memory stance.
- `GET /api/agent/stats?agentId=...` - Retrieve raw publication metrics.

For interactive API docs, visit `http://localhost:8000/docs`.

## Testing

Run tests with Pytest:
```bash
# Windows
$env:TESTING="1"; python -m pytest
# Linux/Mac
TESTING=1 python -m pytest
```
