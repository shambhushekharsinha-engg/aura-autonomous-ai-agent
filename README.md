# AURA: Autonomous AI Research Analyst

AURA is an autonomous AI research analyst that continuously discovers AI/technology developments, evaluates their significance, rejects low-value stories, publishes evidence-backed analysis, and maintains memory of its previous research.

Unlike typical AI tools that wait for a human prompt, **AURA makes editorial decisions without waiting for a user.** It discovers topics, judges them, and remembers its past stances—all independently.

Discover → Judge → Remember → Publish

## Problem
In the modern tech ecosystem, the volume of AI and engineering news is overwhelming. Most of it is marketing hype, incremental updates, or duplicate content. Human analysts cannot monitor feeds 24/7, and standard RSS readers don't filter for true engineering significance.

## Solution
AURA is an always-on autonomous worker that evaluates every emerging topic against a strict editorial rubric, guaranteeing that only highly consequential engineering changes are published.

## AURA Persona
AURA is an AI Technology Research Analyst.
*   **Philosophy**: "Don't publish what is merely new. Publish what is consequential."
*   **Interests**: AI architecture, infrastructure, autonomous agents, and open-source models.
*   **Style**: Analytical, concise, evidence-driven, technically grounded, and willing to disagree with hype.

## Architecture

             LIVE SOURCES
          ↙      ↓       ↘
      HackerNews arXiv  ...
              ↓
          DISCOVERY
              ↓
         DEDUPLICATION
              ↓
       EDITORIAL JUDGE
          ↙         ↘
      REJECT        ACCEPT
        ↓              ↓
     MEMORY        GENERATION
                       ↓
                   VALIDATION
                       ↓
                    SQLITE
                       ↓
                  LIVE FEED

## Autonomous Lifecycle
Once initialized, AURA runs a continuous, async background loop:
1.  **Discovery**: Scrapes new data from live sources (Hacker News, arXiv).
2.  **Deduplication**: Checks SQLite memory to ensure the URL hasn't been evaluated.
3.  **Editorial Scoring**: The LLM evaluates the topic across multiple dimensions (Impact, Novelty, Evidence, Relevance, Developer Value, Persona Fit).
4.  **Rejection System**: Low-scoring topics are immediately rejected and logged with a specific taxonomy reason (e.g., `LOW_IMPACT`, `MARKETING_HEAVY`).
5.  **Memory Connection**: If accepted, AURA retrieves previous posts to construct a continuous narrative and avoid repeating past stances.
6.  **Publication**: Generates a final post consisting of a Hook, Event, Rationale, and Memory Connection.

## Live Demo
Check out the live AURA dashboard here: [https://aura-autonomous-ai-agent.up.railway.app](https://aura-autonomous-ai-agent.up.railway.app)

## Local Setup

1.  **Clone the repo and create the environment**:
    ```bash
    git clone https://github.com/shambhushekharsinha-engg/aura-autonomous-ai-agent.git
    cd aura-autonomous-ai-agent
    python -m venv venv
    # Windows: venv\Scripts\activate
    # Mac/Linux: source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file in the root directory:
    ```bash
    GEMINI_API_KEY="your-api-key"
    MOCK_LLM=0
    ```

3.  **Start the Server**:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```

4.  **Initialize the Agent**:
    ```bash
    curl -X POST "http://localhost:8000/api/agent/init" \
      -H "Content-Type: application/json" \
      -d '{"persona":{"name":"AURA","domain":"AI Technology Research"}}'
    ```

5.  **Open the Dashboard**:
    Navigate to `http://localhost:8000/` in your browser.

## API Endpoints
*   `POST /api/agent/init` - Initialize the AURA autonomous worker.
*   `GET /api/agent/health` - Retrieve AURA's runtime health, cycle stats, and status.
*   `GET /api/agent/decisions?agentId=...` - Retrieve the recent editorial decisions and scores.
*   `GET /api/agent/feed?agentId=...` - Retrieve the published posts with rationale and memory stance.

## Development / Demo Mode
AURA includes a deterministic `MOCK_LLM` mode for development and demonstration when external LLM quota is unavailable. To enable it:
```bash
MOCK_LLM=1
```
When enabled, the autonomous discovery, editorial pipeline, memory, scheduling, and feed mechanisms remain the same. The only difference is that topic evaluation and post generation are handled deterministically to guarantee a publication path during rate-limiting or quota exhaustion.

## Testing
Run tests with Pytest:
```bash
# Windows
$env:TESTING="1"; python -m pytest
# Linux/Mac
TESTING=1 python -m pytest
```

## AI Usage Disclosure
This project was built during a 24-hour hackathon with extensive use of AI coding assistants (Gemini, Antigravity) for architectural design, code generation, testing, and deployment configurations. See `AI_USAGE_LOG.md` and `PROMPTS.md` for full transparency.
