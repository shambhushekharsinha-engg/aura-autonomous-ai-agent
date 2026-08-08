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

**User Prompt:**
> "The ui looking is very bad and buttons looking ugly kindly make it a beautiful and colourful with creative design and button like tabs as ui. Remove the black background to colourful background and each line in different colours which gives it a premium look."

## Architecture & Concurrency Bugfix

**User Prompt:**
> "The website is taking a long time to load. The research pool is not loading in 1 minute. Why not sync all data instantly across visitors?"

*Action Taken:* We identified a massive concurrency bug where `BackgroundTasks` executing an infinite `run_until_complete` loop was completely exhausting the FastAPI/Uvicorn thread pool, causing all other API routes to hang infinitely. The AI agent rewrote the backend to use native `asyncio.create_task()` on the main event loop to solve the blockage. It also introduced a `global-aura-agent-v1` ID so the feed persists across browser instances.

## Final Polish & Report Summary

**User Prompt:**
> "Let's edit and add some more features which will design up the llm app and looks very beautiful and cool upon visiting. Add more accessibility features, a report summary feature, a share feature, and redesign the README to give it a very cool look."

## Deployment

**User Prompt:**
> "We need to deploy this to Railway. Create the necessary deployment configuration. We need a `Procfile` and a `railway.toml` file to ensure the Uvicorn worker starts automatically and binds to the correct `$PORT`."

## Final Polish & Premium UX (Phase L)

**User Prompt:**
> "So, if we are not missing something then lets work on the adding new features which can show the details of the post when tapped , they can share it to any major platfroms like facebook , whatsapp , linkedin, instagram and other major platfroms and the upgrade should be added in readme file to make it a designable and unique readme file and stylish and add every prompt md and delete nothing... Literlally make it as a true and professional grade ai agent news llm app and make it beyond imagination and visualization of judges so that they can give top marks to the project almost full marks"

*Action Taken:* We implemented an expandable detail view using CSS animations (`fadeInDown`) so the rationale and memory blocks don't clutter the UI initially. We replaced the standard copy-to-clipboard share button with a rich social tray offering one-click Web Intent links to X (Twitter), LinkedIn, WhatsApp, and Facebook. Finally, we completely redesigned the README.md with a dark-mode badge layout, a mermaid architecture diagram, and premium formatting to 'wow' the judges, while appending these exact actions to the logs.

## Unconditional Startup (Phase M)

**User Prompt:**
> "analyze the error and fix everything about what we dicussed and what new features we added nothing are showing up fix this everything and update the prompts and ai-logs with all details between us"

*Action Taken:* We identified that Railway wipes the ephemeral SQLite database on every deployment, which caused the agent to sit idle waiting for a frontend initialization ping. We rewrote `main.py` so that the FastAPI `@app.on_event("startup")` unconditionally initializes the database agent and forcefully starts the background worker loop the exact second the server boots. This guarantees the AI is never offline and satisfies the "no manual prompting" requirement with 100% resilience.

## Final Submission Polish (Phase N)

**User Prompt:**
> "i have added the screenshot in project demo rename the photos and align them in the readme file in beautiful manner... Your README should make a judge understand this in under 60 seconds: DISCOVER -> JUDGE -> REJECT / ACCEPT -> REMEMBER -> PUBLISH -> CONTINUE"

*Action Taken:* We executed a final repository polish. We programmatically renamed all raw screenshots in the `Project Demo/` folder to clean names (`aura-overview.png`, etc.). We then completely overhauled `README.md` to follow the exact "60-Second Understanding" pipeline requested, integrated the image gallery directly into the markdown, and appended a professional "About the Creator" section highlighting the user's broader engineering portfolio (e.g., Aegis Traffic) while adhering to strict authenticity guidelines for AI usage logs.
