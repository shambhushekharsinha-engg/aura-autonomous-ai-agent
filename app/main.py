from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid
import asyncio
from datetime import timezone

from . import models, schemas, database, agent
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AURA - Autonomous AI Research Analyst")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def read_index():
    return FileResponse('app/static/index.html')

@app.post("/api/agent/init", response_model=schemas.InitResponse)
async def init_agent(req: schemas.InitRequest, db: Session = Depends(database.get_db)):
    agent_id = "global-aura-agent-v1"
    
    # Check if global agent already exists
    db_agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    
    if not db_agent:
        # Create the global agent in DB
        db_agent = models.Agent(
            id=agent_id,
            name=req.persona.name,
            domain=req.persona.domain
        )
        db.add(db_agent)
        db.commit()
        
    # Start the autonomous loop if it's not already running
    import os
    if not os.getenv("TESTING"):
        if not agent.state.get("workerRunning"):
            asyncio.create_task(agent.autonomous_loop(agent_id))
    
    return {"agentId": agent_id}

@app.get("/api/agent/feed", response_model=schemas.FeedResponse)
def get_feed(agentId: str, db: Session = Depends(database.get_db)):
    # Validate agent exists
    db_agent = db.query(models.Agent).filter(models.Agent.id == agentId).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    posts = db.query(models.Post).filter(models.Post.agent_id == agentId).order_by(models.Post.created_at.desc()).limit(20).all()
    
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

@app.get("/api/agent/stats", response_model=schemas.StatsResponse)
def get_stats(agentId: str, db: Session = Depends(database.get_db)):
    db_agent = db.query(models.Agent).filter(models.Agent.id == agentId).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    discovered = db.query(models.Topic).count()
    published = db.query(models.Post).filter(models.Post.agent_id == agentId).count()
    rejected = db.query(models.Topic).filter(models.Topic.decision != "PUBLISH").count()
    
    return {
        "discovered": discovered,
        "published": published,
        "rejected": rejected,
        "status": "autonomous"
    }

@app.get("/api/agent/decisions", response_model=schemas.DecisionsResponse)
def get_decisions(agentId: str, db: Session = Depends(database.get_db)):
    topics = db.query(models.Topic).order_by(models.Topic.discovered_at.desc()).limit(15).all()
    
    decisions = []
    for t in topics:
        decisions.append({
            "topic": t.title,
            "decision": t.decision if t.decision else "REJECT",
            "score": t.score if t.score else 0.0,
            "reason": t.rejection_reason,
            "createdAt": t.discovered_at.isoformat() if t.discovered_at else ""
        })
    return {"decisions": decisions}

@app.get("/api/agent/health", response_model=schemas.HealthResponse)
def get_health(db: Session = Depends(database.get_db)):
    discovered = db.query(models.Topic).count()
    rejected = db.query(models.Topic).filter(models.Topic.decision != "PUBLISH").count()
    published = db.query(models.Post).count()
    
    status = "error" if agent.state.get("lastError") else "healthy"
    if not agent.state.get("workerRunning"):
        status = "offline"
        
    return {
        "status": status,
        "autonomous": True,
        "workerRunning": agent.state.get("workerRunning", False),
        "lastCycleAt": agent.state.get("lastCycleAt"),
        "nextCycleAt": agent.state.get("nextCycleAt"),
        "cyclesCompleted": agent.state.get("cyclesCompleted", 0),
        "topicsDiscovered": discovered,
        "topicsRejected": rejected,
        "postsPublished": published
    }
