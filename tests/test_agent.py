import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app import models

# Setup in-memory sqlite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
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
    
    db = TestingSessionLocal()
    # Insert older post
    post1 = models.Post(id="p1", agent_id=agent_id, topic_id="t1", text="Old", rationale="R1", sources=["S1"])
    db.add(post1)
    db.commit()
    
    # Insert newer post
    post2 = models.Post(id="p2", agent_id=agent_id, topic_id="t2", text="New", rationale="R2", sources=["S2"])
    db.add(post2)
    db.commit()
    db.close()
    
    # Get feed
    response = client.get(f"/api/agent/feed?agentId={agent_id}")
    data = response.json()
    assert len(data["posts"]) == 2
    assert data["posts"][0]["id"] == "p2" # Newest first
    assert data["posts"][1]["id"] == "p1"
