import json
import datetime
from typing import Generator
from sqlalchemy import create_engine, Column, String, Float, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

Base = declarative_base()

class DiagramRecord(Base):
    __tablename__ = "diagrams"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(160), nullable=False)
    diagram_type = Column(String(64), nullable=False, index=True)
    spec_json = Column(Text, nullable=False)
    svg_content = Column(Text, nullable=False)
    html_content = Column(Text, nullable=False)
    created_by = Column(String(120), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

class AuditRecord(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False, index=True)
    actor = Column(String(120), nullable=False)
    action = Column(String(64), nullable=False)
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(64), nullable=False)
    details_json = Column(Text, nullable=False)

class EvalRunRecord(Base):
    __tablename__ = "eval_runs"

    id = Column(String(64), primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    executed_by = Column(String(120), nullable=False)
    total_samples = Column(Integer, nullable=False)
    passed_samples = Column(Integer, nullable=False)
    pass_rate = Column(Float, nullable=False)
    results_json = Column(Text, nullable=False)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def log_audit(db: Session, actor: str, action: str, resource_type: str, resource_id: str, details: dict):
    import uuid
    record = AuditRecord(
        id=str(uuid.uuid4()),
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details_json=json.dumps(details)
    )
    db.add(record)
    db.commit()
