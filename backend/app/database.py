import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# This URL will dynamically point to local docker or k8s postgres pod
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5432/jenkins_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency utility to yield database sessions to API routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
