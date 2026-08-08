from sqlalchemy import Column, String, Integer, DateTime, Text, Float, JSON
from .database import Base
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc)

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    domain = Column(String)
    created_at = Column(DateTime(timezone=True), default=utcnow)

class Topic(Base):
    __tablename__ = "topics"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    url = Column(String)
    source = Column(String)
    published_at = Column(String)
    discovered_at = Column(DateTime(timezone=True), default=utcnow)
    score = Column(Float, nullable=True)
    decision = Column(String, nullable=True)
    rejection_reason = Column(Text, nullable=True)

class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, index=True)
    topic_id = Column(String, index=True)
    text = Column(Text)
    rationale = Column(Text)
    stance = Column(Text, nullable=True)
    sources = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=utcnow)
