"""Database models"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class VoiceProfile(Base):
    """Voice profile for authentication"""
    __tablename__ = "voice_profiles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    feature_vector = Column(Text)  # JSON-encoded features
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Memory(Base):
    """User memory/preferences"""
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    category = Column(String(50))  # e.g., 'preference', 'habit', 'project'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TaskLog(Base):
    """Task execution log"""
    __tablename__ = "task_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    task_name = Column(String(100), nullable=False)
    parameters = Column(Text)  # JSON
    result = Column(Text)  # JSON
    success = Column(Integer, default=0)  # 0=failed, 1=success
    duration = Column(Float)  # execution time in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
