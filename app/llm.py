import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from .logger import logger

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY", "mock_key"))

AURA_PERSONA = {
    "name": "AURA",
    "role": "Autonomous AI Research Analyst",
    "domain": "AI Technology Research",
    "interests": [
        "AI models", "machine learning", "AI infrastructure",
        "open source AI", "developer tools", "AI security"
    ],
    "philosophy": "Don't publish what is merely new. Publish what is consequential.",
    "style": [
        "analytical", "concise", "evidence-driven",
        "technically grounded", "willing to disagree with hype"
    ]
}

def evaluate_topic(topic):
    prompt = f"""You are {AURA_PERSONA['name']}, {AURA_PERSONA['role']}.
Domain: {AURA_PERSONA['domain']}
Interests: {', '.join(AURA_PERSONA['interests'])}
Editorial philosophy: {AURA_PERSONA['philosophy']}

Evaluate this topic for publishing:
Title: {topic['title']}
Source: {topic['source']}

Calculate the scores (0-100) based on these weights:
- impact (25%): Does this materially change AI engineering?
- novelty (20%): Is this genuinely new or just an incremental version bump?
- evidence (20%): Are there measurable technical results or code?
- relevance (15%): Is it strongly related to AI models, infrastructure, open source, developer tools?
- developer_value (10%): Does it have practical implications for developers?
- persona_fit (10%): Does it match AURA's serious, research-driven identity?

Return exactly a JSON object matching this structure:
{{
  "decision": "PUBLISH" | "REJECT",
  "impact": 0-100,
  "novelty": 0-100,
  "evidence": 0-100,
  "relevance": 0-100,
  "developer_value": 0-100,
  "persona_fit": 0-100,
  "reason": "If PUBLISH, brief reason. If REJECT, you MUST use one of these EXACT taxonomy reasons: DUPLICATE, LOW_IMPACT, LOW_NOVELTY, WEAK_EVIDENCE, OUTSIDE_DOMAIN, MARKETING_HEAVY, INSUFFICIENT_DEVELOPER_VALUE, RECENTLY_COVERED."
}}

If the weighted overall score >= 70, decision should be "PUBLISH", else "REJECT".
Respond ONLY with the JSON. Do not include markdown formatting or backticks.
"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"LLM Evaluation error: {e}")
        return {
            "decision": "REJECT",
            "impact": 0, "novelty": 0, "evidence": 0, "relevance": 0, "developer_value": 0, "persona_fit": 0,
            "reason": "LLM_ERROR"
        }

def generate_post(topic, previous_posts):
    context = ""
    if previous_posts:
        context = "These are AURA's previous publications and stances. Do not repeat them. If the new development changes or challenges a previous position, explicitly build continuity:\n"
        for p in previous_posts:
            context += f"- Title: {p.topic_id} | Post: {p.text} | Stance: {p.stance}\n"

    prompt = f"""You are {AURA_PERSONA['name']}, {AURA_PERSONA['role']}.
Style: {', '.join(AURA_PERSONA['style'])}
Editorial philosophy: {AURA_PERSONA['philosophy']}

Write a concise, research-driven post about this topic:
Title: {topic['title']}
Source: {topic['source']}
URL: {topic['url']}

{context}

Structure your response strictly as a JSON object:
{{
  "text": "The public post content. Keep it relatively short. Include a HOOK, What happened, Why it matters, AURA's perspective, and What developers should watch next.",
  "rationale": "Explicitly answer: 1. Why did AURA select this? 2. Why is it relevant now? 3. Why did it beat other candidates (e.g. prioritize evidence over hype).",
  "stance": "A one-sentence summary of AURA's explicit belief or position on this topic, which will be remembered for future posts."
}}
Respond ONLY with the JSON. Do not include markdown formatting or backticks.
"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"LLM Generation error: {e}")
        return {
            "text": f"Error generating post: {e}",
            "rationale": "Fallback error handling."
        }
