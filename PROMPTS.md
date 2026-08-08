# Development Prompts

This file records the actual prompts used with the AI coding assistant (Antigravity/Gemini) during the 24-hour hackathon to build AURA.

## Architecture & Foundation

**User Prompt:**
> "Let's build an autonomous AI agent in Python for a hackathon. The deadline is 24 hours. The agent needs to be a 'Research Analyst' that continuously monitors tech news (Hacker News, arXiv), evaluates them using Gemini, and publishes a feed of high-quality posts. I want to use FastAPI for the backend and SQLite for persistent memory. Don't use heavy frameworks like LangChain, keep the architecture vanilla and transparent."

## Autonomous Loop Implementation

**User Prompt:**
> "Implement the autonomous worker loop in `app/agent.py`. It needs to use `asyncio` to run continuously in the background alongside the FastAPI server. It should fetch RSS feeds, deduplicate them against the SQLite database, evaluate them using our Gemini prompts, and save the accepted posts. Make sure it sleeps for 30 seconds between cycles and never crashes if the LLM or network fails."

## LLM Integration & Evaluation

**User Prompt:**
> "Write the `evaluate_topic` and `generate_post` functions in `app/llm.py` using the new `google-genai` SDK for `gemini-2.0-flash`. The evaluator prompt must score the topic across impact, novelty, evidence, relevance, developer value, and persona fit. If the score is >= 70, return PUBLISH, otherwise REJECT with a taxonomy reason (like LOW_IMPACT). The generation prompt must retrieve the last 5 posts from SQLite to maintain 'memory' and avoid repeating past stances."

## Resilience & MOCK_LLM

**User Prompt:**
> "We hit a 429 Quota Exceeded error on the Gemini API. The worker correctly caught it and didn't crash, which is great for resilience. However, we need a way to demonstrate the happy path if the quota is dead during the presentation. Implement a deterministic `MOCK_LLM` fallback in `app/llm.py`. Use a hash of the topic title to generate a stable score between 40 and 95 so it rejects some topics and accepts others realistically, rather than accepting 5/5 at once. Make the mock text sound like genuine AURA research analysis."

## Dashboard UI

**User Prompt:**
> "Create a beautiful 'Control Room' dashboard in `index.html`. It needs to fetch data from `/api/agent/health`, `/api/agent/decisions`, and `/api/agent/feed`. Use a dark, sleek hacker aesthetic. Show the live worker status, the cycle countdown, the editorial judgments (with rejection reasons in red), and the final published feed with AURA's stance memory."

## Deployment

**User Prompt:**
> "We need to deploy this to Railway. Create the necessary deployment configuration. We need a `Procfile` and a `railway.toml` file to ensure the Uvicorn worker starts automatically and binds to the correct `$PORT`."
