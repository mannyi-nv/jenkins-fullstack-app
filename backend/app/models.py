from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from .database import Base

class JenkinsJob(Base):
    __tablename__ = "jenkins_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String, unique=True, index=True, nullable=False)
    job_type = Column(String, nullable=False)  # Freestyle, Pipeline, etc.
    repository_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_run_status = Column(String, default="UNKNOWN")
    created_at = Column(DateTime, default=datetime.utcnow)
