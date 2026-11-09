from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from .database import engine, Base, get_db
from .models import JenkinsJob

# Automatically spin up database tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jenkins Web Tool API")

# Enable CORS so your future frontend dashboard tier can communicate with it
app.add_middleware(
    CORSMiddleware,
allow_origins=[
    "http://192.168.224.142:8080",  # Your specific frontend host address
    "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas for Request/Response validation
class JobBase(BaseModel):
    job_name: str
    job_type: str
    repository_url: str = None
    is_active: bool = True

class JobResponse(JobBase):
    id: int
    last_run_status: str

    class Config:
        from_attributes = True

# --- API ENDPOINTS (CRUD) ---

@app.get("/api/jobs", response_model=List[JobResponse])
def get_all_jobs(db: Session = Depends(get_db)):
    return db.query(JenkinsJob).all()

@app.post("/api/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job: JobBase, db: Session = Depends(get_db)):
    db_job = db.query(JenkinsJob).filter(JenkinsJob.job_name == job.job_name).first()
    if db_job:
        raise HTTPException(status_code=400, detail="Job name already registered")
    
    new_job = JenkinsJob(**job.model_dump())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@app.delete("/api/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    db_job = db.query(JenkinsJob).filter(JenkinsJob.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(db_job)
    db.commit()
    return