from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import uuid
import asyncio
from datetime import timezone

from . import models, schemas, database, agent
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AURA - Autonomous AI Research Analyst")

@app.post("/api/agent/init", response_model=schemas.InitResponse)
def init_agent(req: schemas.InitRequest, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    # Create the agent in DB
    agent_id = str(uuid.uuid4())
    db_agent = models.Agent(
        id=agent_id,
        name=req.persona.name,
        domain=req.persona.domain
    )
    db.add(db_agent)
    db.commit()
    
    # Start the autonomous loop in the background
    asyncio.create_task(agent.autonomous_loop(agent_id))
    
    return {"agentId": agent_id}

@app.get("/api/agent/feed", response_model=schemas.FeedResponse)
def get_feed(agentId: str, db: Session = Depends(database.get_db)):
    # Validate agent exists
    db_agent = db.query(models.Agent).filter(models.Agent.id == agentId).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    posts = db.query(models.Post).filter(models.Post.agent_id == agentId).order_by(models.Post.created_at.desc()).all()
    
    feed_posts = []
    for p in posts:
        # Convert datetime to ISO 8601 with Z timezone if aware
        dt_str = p.created_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if p.created_at else ""
        feed_posts.append({
            "id": p.id,
            "createdAt": dt_str,
            "text": p.text,
            "rationale": p.rationale,
            "stance": p.stance,
            "sources": p.sources if p.sources else []
        })
        
    return {"posts": feed_posts}
