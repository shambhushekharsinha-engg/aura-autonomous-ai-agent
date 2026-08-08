import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import tempfile

from app.main import app
from app.database import Base, get_db
from app import models

# Setup sqlite for testing
temp_db_file = tempfile.NamedTemporaryFile(delete=False)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{temp_db_file.name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_init_creates_agent():
    response = client.post(
        "/api/agent/init",
        json={"persona": {"name": "Test AURA", "domain": "Testing"}}
    )
    assert response.status_code == 200
    data = response.json()
    assert "agentId" in data
    
    # Verify in DB
    db = TestingSessionLocal()
    agent = db.query(models.Agent).filter(models.Agent.id == data["agentId"]).first()
    assert agent is not None
    assert agent.name == "Test AURA"
    db.close()

def test_feed_returns_empty_initially():
    # Init agent
    init_res = client.post("/api/agent/init", json={"persona": {"name": "AURA", "domain": "Test"}})
    agent_id = init_res.json()["agentId"]
    
    # Get feed
    response = client.get(f"/api/agent/feed?agentId={agent_id}")
    assert response.status_code == 200
    data = response.json()
    assert "posts" in data
    assert len(data["posts"]) == 0

def test_posts_persist_and_sorted_newest_first():
    init_res = client.post("/api/agent/init", json={"persona": {"name": "AURA", "domain": "Test"}})
    agent_id = init_res.json()["agentId"]

    # Insert mock posts directly to db
    db = TestingSessionLocal()
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    p1 = models.Post(id="p1", agent_id=agent_id, topic_id="t1", text="old", rationale="r", created_at=now - timedelta(hours=1))
    p2 = models.Post(id="p2", agent_id=agent_id, topic_id="t2", text="new", rationale="r", created_at=now)
    db.add(p1)
    db.add(p2)
    db.commit()
    db.close()
    
    response = client.get(f"/api/agent/feed?agentId={agent_id}")
    assert response.status_code == 200
    posts = response.json()["posts"]
    assert len(posts) == 2
    assert posts[0]["id"] == "p2" # Newest first
    assert posts[1]["id"] == "p1"

def test_decisions_endpoint():
    init_res = client.post("/api/agent/init", json={"persona": {"name": "AURA", "domain": "Test"}})
    agent_id = init_res.json()["agentId"]

    db = TestingSessionLocal()
    t = models.Topic(id="t1", title="Test Topic", url="http", source="HN", score=85, decision="PUBLISH", rejection_reason="")
    db.add(t)
    db.commit()
    db.close()

    response = client.get(f"/api/agent/decisions?agentId={agent_id}")
    assert response.status_code == 200
    data = response.json()
    assert "decisions" in data
    assert len(data["decisions"]) == 1
    assert data["decisions"][0]["topic"] == "Test Topic"
    assert data["decisions"][0]["decision"] == "PUBLISH"

def test_health_endpoint():
    response = client.get("/api/agent/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "autonomous" in data
    assert "workerRunning" in data
    assert "cyclesCompleted" in data
