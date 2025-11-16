from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List
from src.core.config import settings
from src.utils.logger import get_logger

logger = get_logger("DBManager")

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    context_id = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)


class AgentLog(Base):
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    context_id = Column(String(100), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    action = Column(String(200), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration = Column(Float, nullable=True)
    details = Column(Text, nullable=True)


class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    context_id = Column(String(100), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    result_type = Column(String(50), nullable=False)
    result_data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    validated = Column(Boolean, default=False)


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
    
    def initialize(self):
        """Initialize database connection and create tables."""
        try:
            self.engine = create_engine(
                settings.database_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )
            Base.metadata.create_all(bind=self.engine)
            self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
            logger.info(f"Database initialized at {settings.postgres_host}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise
    
    def get_session(self) -> Session:
        """Get database session."""
        if not self.SessionLocal:
            self.initialize()
        return self.SessionLocal()
    
    def create_task(self, context_id: str) -> Task:
        """Create a new task."""
        session = self.get_session()
        try:
            task = Task(context_id=context_id, status="running")
            session.add(task)
            session.commit()
            session.refresh(task)
            logger.info(f"Created task: {context_id}")
            return task
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create task {context_id}: {e}")
            raise
        finally:
            session.close()
    
    def update_task_status(self, context_id: str, status: str, success: bool = False, error: Optional[str] = None):
        """Update task status."""
        session = self.get_session()
        try:
            task = session.query(Task).filter(Task.context_id == context_id).first()
            if task:
                task.status = status
                task.success = success
                if error:
                    task.error_message = error
                if status == "completed":
                    task.completed_at = datetime.utcnow()
                session.commit()
                logger.info(f"Updated task {context_id} status to {status}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update task {context_id}: {e}")
        finally:
            session.close()
    
    def log_agent_action(self, context_id: str, agent_name: str, action: str, duration: Optional[float] = None, details: Optional[str] = None):
        """Log agent action."""
        session = self.get_session()
        try:
            log = AgentLog(
                context_id=context_id,
                agent_name=agent_name,
                action=action,
                duration=duration,
                details=details
            )
            session.add(log)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to log action for {agent_name}: {e}")
        finally:
            session.close()
    
    def save_result(self, context_id: str, agent_name: str, result_type: str, result_data: str, validated: bool = False):
        """Save agent result."""
        session = self.get_session()
        try:
            result = Result(
                context_id=context_id,
                agent_name=agent_name,
                result_type=result_type,
                result_data=result_data,
                validated=validated
            )
            session.add(result)
            session.commit()
            logger.info(f"Saved result for {agent_name} in context {context_id}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save result: {e}")
        finally:
            session.close()
    
    def get_task(self, context_id: str) -> Optional[Task]:
        """Retrieve task by context_id."""
        session = self.get_session()
        try:
            return session.query(Task).filter(Task.context_id == context_id).first()
        finally:
            session.close()
    
    def get_results(self, context_id: str) -> List[Result]:
        """Get all results for a context."""
        session = self.get_session()
        try:
            return session.query(Result).filter(Result.context_id == context_id).all()
        finally:
            session.close()


db_manager = DatabaseManager()
