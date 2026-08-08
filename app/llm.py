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

import hashlib

def get_deterministic_score(title):
    h = int(hashlib.md5(title.encode('utf-8')).hexdigest(), 16)
    return 40 + (h % 56)

def evaluate_topic(topic):
    if os.getenv("MOCK_LLM") == "1":
        score = get_deterministic_score(topic['title'])
        if score >= 75:
            return {
                "decision": "PUBLISH",
                "impact": score, "novelty": score - 2, "evidence": score + 3, "relevance": score, "developer_value": score - 5, "persona_fit": score + 2,
                "reason": "MOCK_PUBLISH"
            }
        else:
            reasons = ["LOW_IMPACT", "LOW_NOVELTY", "WEAK_EVIDENCE", "OUTSIDE_DOMAIN", "MARKETING_HEAVY"]
            reason = reasons[score % len(reasons)]
            return {
                "decision": "REJECT",
                "impact": score, "novelty": score, "evidence": score, "relevance": score, "developer_value": score, "persona_fit": score,
                "reason": reason
            }
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
    if os.getenv("MOCK_LLM") == "1":
        title = topic['title']
        t_low = title.lower()
        
        # 1. Theme Classification & Framework
        if any(w in t_low for w in ["security", "cve", "vulnerability", "attack", "hack", "bypass"]):
            theme = "Security"
            framework_analysis = f"The attack surface highlighted by '{title}' exposes critical gaps in current infrastructure. The primary consequence isn't just the immediate vulnerability, but the systemic risk when mitigations lag behind discovery."
            framework_stance = f"Security mitigations for '{title[:30]}...' must move from reactive patching to structural infrastructure isolation."
            framework_rationale = "Selected because it provides concrete evidence of expanding attack surfaces requiring fundamental mitigation."
        elif any(w in t_low for w in ["model", "benchmark", "sota", "gpt", "claude", "llama", "parameter"]):
            theme = "Models"
            framework_analysis = f"While '{title}' demonstrates improvements on standard benchmarks, the raw evaluation quality often masks underlying weaknesses. Reproducibility and practical significance matter far more than incremental capability gains on saturated tests."
            framework_stance = f"For '{title[:30]}...', benchmark gains matter less than deployment reproducibility."
            framework_rationale = "Selected to contextualize incremental model updates against actual practical engineering value."
        elif any(w in t_low for w in ["agent", "autonomous", "bot", "auto"]):
            theme = "Agents"
            framework_analysis = f"The agent behavior observed in '{title}' illustrates a critical shift in infrastructure implications. As systems scale autonomously, traditional human-centric safeguards fail, requiring agent-aware rate limiting and identity verification."
            framework_stance = f"Autonomous interactions in '{title[:30]}...' prove infrastructure needs strict machine-readable safeguards."
            framework_rationale = "Selected because it highlights systemic infrastructure implications of autonomous behaviors."
        elif any(w in t_low for w in ["open source", "github", "oss", "repo", "license"]):
            theme = "Open Source"
            framework_analysis = f"The ecosystem impact of '{title}' raises immediate questions about maintainability. Developer consequences often diverge from initial hype, and true value depends entirely on community governance and long-term viability."
            framework_stance = f"The true impact of '{title[:30]}...' relies entirely on long-term community maintainability."
            framework_rationale = "Selected because it affects open-source ecosystem governance and developer maintainability."
        elif any(w in t_low for w in ["chip", "gpu", "nvidia", "hardware", "compute", "tpu"]):
            theme = "Hardware"
            framework_analysis = f"The underlying compute constraints exposed by '{title}' dictate the economics of modern deployment. Developer impact is downstream of these hardware realities, shifting optimization from software to fundamental infrastructure."
            framework_stance = f"Hardware economics in '{title[:30]}...' dictate downstream developer constraints."
            framework_rationale = "Selected because compute economics fundamentally constrain software deployment."
        else:
            theme = "General AI"
            framework_analysis = f"The technical changes introduced by '{title}' lack immediate second-order consequences without deeper evidence. However, tracking this vector is necessary to understand how the broader ecosystem adapts to incremental shifts."
            framework_stance = f"The technical shifts in '{title[:30]}...' require further evidence before confirming second-order consequences."
            framework_rationale = "Selected to track macro-technical shifts across the ecosystem."

        # 2. Previous Memory Context
        memory_str = ""
        if previous_posts and previous_posts[0].stance:
            prev = previous_posts[0].stance
            memory_str = f"\n\n**Memory Context:** This reinforces an earlier pattern AURA identified: '{prev}'. The continuity suggests a hardening trend."

        # 3. Assemble Post
        text = f"**Analysis: {title}**\n\n{framework_analysis}{memory_str}"
        rationale = f"1. {framework_rationale}\n2. Matches AURA's {theme} domain focus.\nSource: {topic.get('source', 'arXiv/HN')}"
        
        return {
            "text": text,
            "rationale": rationale,
            "stance": framework_stance
        }
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
