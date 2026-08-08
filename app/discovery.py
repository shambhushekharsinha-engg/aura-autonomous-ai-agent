import feedparser
from datetime import datetime
import uuid
import httpx
from .logger import logger

def discover_topics():
    topics = []
    
    # Source 1: Hacker News AI
    try:
        logger.info("Fetching Hacker News feed...")
        response = httpx.get('https://hnrss.org/newest?q=AI', timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        hn_feed = feedparser.parse(response.text)
        
        for entry in hn_feed.entries[:5]:
            topics.append({
                "id": str(uuid.uuid4()),
                "title": entry.title,
                "url": entry.link,
                "source": "Hacker News",
                "published_at": entry.published if hasattr(entry, 'published') else str(datetime.utcnow())
            })
    except Exception as e:
        logger.error(f"HN Discovery Error: {e}")
        
    # Source 2: ArXiv CS.AI
    try:
        logger.info("Fetching arXiv feed...")
        response = httpx.get('https://export.arxiv.org/rss/cs.AI', timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        arxiv_feed = feedparser.parse(response.text)
        
        for entry in arxiv_feed.entries[:5]:
            topics.append({
                "id": str(uuid.uuid4()),
                "title": entry.title,
                "url": entry.link,
                "source": "arXiv cs.AI",
                "published_at": entry.published if hasattr(entry, 'published') else str(datetime.utcnow())
            })
    except Exception as e:
        logger.error(f"ArXiv Discovery Error: {e}")
        
    return topics
