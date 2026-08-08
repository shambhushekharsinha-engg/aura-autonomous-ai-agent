import asyncio
from datetime import datetime, timezone
import uuid

from . import discovery, llm, models
from .database import SessionLocal
from .logger import logger

DEVELOPMENT_INTERVAL = 30 # seconds
PRODUCTION_INTERVAL = 900 # 15 minutes
CURRENT_INTERVAL = DEVELOPMENT_INTERVAL

def get_previous_posts(db, agent_id, limit=5):
    return db.query(models.Post).filter(models.Post.agent_id == agent_id).order_by(models.Post.created_at.desc()).limit(limit).all()

async def autonomous_loop(agent_id: str):
    logger.info(f"Agent initialized")
    logger.info(f"Autonomous worker started for agent {agent_id}")
    
    while True:
        try:
            db = SessionLocal()
            logger.info("Starting discovery cycle")
            
            topics = discovery.discover_topics()
            logger.info(f"{len(topics)} topics discovered")
            
            for t in topics:
                try:
                    # Deduplicate by URL
                    existing = db.query(models.Topic).filter(models.Topic.url == t["url"]).first()
                    if existing:
                        logger.info(f"Topic rejected | reason=DUPLICATE | title='{t['title']}'")
                        continue
                    
                    # Evaluate
                    logger.info("Evaluating candidate...")
                    evaluation = llm.evaluate_topic(t)
                    
                    # Save Topic
                    overall_score = (
                        evaluation.get('impact', 0) * 0.25 +
                        evaluation.get('novelty', 0) * 0.20 +
                        evaluation.get('evidence', 0) * 0.20 +
                        evaluation.get('relevance', 0) * 0.15 +
                        evaluation.get('developer_value', 0) * 0.10 +
                        evaluation.get('persona_fit', 0) * 0.10
                    )
                    
                    decision = evaluation.get("decision", "reject").upper()
                    
                    db_topic = models.Topic(
                        id=t["id"],
                        title=t["title"],
                        url=t["url"],
                        source=t["source"],
                        published_at=t["published_at"],
                        score=overall_score,
                        decision=decision,
                        rejection_reason=evaluation.get("reason", "")
                    )
                    db.add(db_topic)
                    db.commit()
                    
                    if decision != "PUBLISH":
                        logger.info(f"Topic rejected | score={overall_score:.1f} | reason={evaluation.get('reason', 'LOW_SCORE')}")
                        continue
                    
                    logger.info(f"Topic accepted | score={overall_score:.1f}")
                    
                    # Retrieve Memory (past posts)
                    previous_posts = get_previous_posts(db, agent_id)
                    
                    # Generate Post
                    post_data = llm.generate_post(t, previous_posts)
                    
                    # Save Post
                    db_post = models.Post(
                        id=str(uuid.uuid4()),
                        agent_id=agent_id,
                        topic_id=t["id"],
                        text=post_data.get("text", ""),
                        rationale=post_data.get("rationale", ""),
                        sources=[t["url"]],
                        created_at=datetime.now(timezone.utc)
                    )
                    db.add(db_post)
                    db.commit()
                    
                    logger.info("Post published")
                    logger.info("Memory updated")
                except Exception as e:
                    logger.exception(f"Error processing topic '{t.get('title')}': {e}")
                
            logger.info("Cycle complete")
            db.close()
            
        except Exception as e:
            logger.exception("Autonomous cycle failed")
            
        await asyncio.sleep(CURRENT_INTERVAL)
