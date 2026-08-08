import asyncio
from datetime import datetime, timezone
import uuid

from . import discovery, llm, models
from .database import SessionLocal
from .logger import logger

DEVELOPMENT_INTERVAL = 30 # seconds
PRODUCTION_INTERVAL = 900 # 15 minutes
CURRENT_INTERVAL = DEVELOPMENT_INTERVAL

state = {
    "workerRunning": False,
    "lastCycleAt": None,
    "nextCycleAt": None,
    "cyclesCompleted": 0,
    "lastError": None
}

def is_semantic_duplicate(new_title, recent_topics):
    new_words = set(new_title.lower().split())
    for t in recent_topics:
        old_words = set(t.title.lower().split())
        overlap = new_words.intersection(old_words)
        # If more than 50% of the new title words are in an old title (ignoring stop words realistically, but this is a simple proxy)
        if len(new_words) > 3 and len(overlap) / len(new_words) > 0.6:
            return True
    return False

def get_previous_posts(db, agent_id, limit=5):
    return db.query(models.Post).filter(models.Post.agent_id == agent_id).order_by(models.Post.created_at.desc()).limit(limit).all()

async def autonomous_loop(agent_id: str):
    logger.info(f"Agent initialized")
    logger.info(f"Autonomous worker started for agent {agent_id}")
    
    state["workerRunning"] = True
    
    while True:
        cycle_start_time = datetime.now(timezone.utc)
        state["lastCycleAt"] = cycle_start_time.isoformat()
        state["nextCycleAt"] = None
        
        try:
            db = SessionLocal()
            logger.info("Starting discovery cycle")
            
            topics = discovery.discover_topics()
            logger.info(f"{len(topics)} topics discovered from feeds")
            
            recent_published_topics = db.query(models.Topic).filter(models.Topic.decision == "PUBLISH").order_by(models.Topic.discovered_at.desc()).limit(10).all()
            
            novel_topics_processed = 0
            for t in topics:
                if novel_topics_processed >= 3:
                    break # Only process 3 new items per cycle to ensure a steady stream for the demo
                    
                try:
                    # Deduplicate by URL
                    existing = db.query(models.Topic).filter(models.Topic.url == t["url"]).first()
                    if existing:
                        continue
                        
                    novel_topics_processed += 1
                        
                    # Deduplicate by semantic similarity (title word overlap)
                    if is_semantic_duplicate(t["title"], recent_published_topics):
                        logger.info(f"Topic rejected | reason=DUPLICATE_CONCEPT | title='{t['title']}'")
                        
                        db_topic = models.Topic(
                            id=t["id"], title=t["title"], url=t["url"], source=t["source"],
                            published_at=t["published_at"], score=0, decision="REJECT", rejection_reason="DUPLICATE_CONCEPT"
                        )
                        db.add(db_topic)
                        db.commit()
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
                    
                    decision = "PUBLISH" if overall_score >= 70 else "REJECT"
                    
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
                    
                    # VALIDATION
                    text = post_data.get("text", "")
                    rationale = post_data.get("rationale", "")
                    stance = post_data.get("stance", "")
                    
                    if not text or not rationale or not stance or len(text) < 10:
                        logger.error(f"VALIDATION FAILED: Post missing required fields. Discarding.")
                        db_topic.decision = "REJECT"
                        db_topic.rejection_reason = "VALIDATION_FAILED"
                        db.commit()
                        continue
                    
                    # Save Post
                    db_post = models.Post(
                        id=str(uuid.uuid4()),
                        agent_id=agent_id,
                        topic_id=t["id"],
                        text=text,
                        rationale=rationale,
                        stance=stance,
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
            state["cyclesCompleted"] += 1
            state["lastError"] = None
            db.close()
            
        except Exception as e:
            logger.exception("Autonomous cycle failed")
            state["lastError"] = str(e)
            
        next_cycle = datetime.now(timezone.utc).timestamp() + CURRENT_INTERVAL
        state["nextCycleAt"] = datetime.fromtimestamp(next_cycle, tz=timezone.utc).isoformat()
        await asyncio.sleep(CURRENT_INTERVAL)
