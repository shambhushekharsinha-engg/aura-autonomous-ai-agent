import feedparser
from datetime import datetime
import uuid
import httpx
import re
from .logger import logger

def clean_html(raw_html):
    if not raw_html:
        return ""
    cleaner = re.compile('<.*?>')
    return re.sub(cleaner, '', raw_html).strip()

def fetch_feed(url, source_name, limit=15):
    topics = []
    try:
        logger.info(f"Fetching feed from {source_name}...")
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        feed = feedparser.parse(response.text)
        
        for entry in feed.entries[:limit]:
            # Extract summary
            summary = ""
            if hasattr(entry, 'summary'):
                summary = clean_html(entry.summary)
            elif hasattr(entry, 'description'):
                summary = clean_html(entry.description)
                
            topics.append({
                "id": str(uuid.uuid4()),
                "title": entry.title,
                "url": entry.link,
                "source": source_name,
                "summary": summary[:500] if summary else "", # Keep it bounded
                "published_at": entry.published if hasattr(entry, 'published') else str(datetime.utcnow())
            })
    except Exception as e:
        logger.error(f"{source_name} Discovery Error: {e}")
    return topics

def discover_topics():
    topics = []
    
    # 1. Crowdsourced / Engineering
    topics.extend(fetch_feed('https://hnrss.org/newest?q=AI', 'Hacker News', limit=10))
    
    # 2. Primary Source / Academic
    topics.extend(fetch_feed('https://export.arxiv.org/rss/cs.AI', 'arXiv cs.AI', limit=10))
    
    # 3. High-Quality Editorial
    topics.extend(fetch_feed('https://techcrunch.com/category/artificial-intelligence/feed/', 'TechCrunch AI', limit=10))
    
    # 4. Official / Research Blog (Using MIT Tech Review as placeholder for consistent RSS)
    topics.extend(fetch_feed('https://www.technologyreview.com/topic/artificial-intelligence/feed', 'MIT Technology Review', limit=10))
        
    return topics
