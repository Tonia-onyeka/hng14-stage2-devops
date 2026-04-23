import os
import uuid
import redis
from fastapi import FastAPI, HTTPException

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    decode_responses=True  # Fixes the .decode() requirement
)

@app.post("/jobs", status_code=201)
def create_job():
    try:
        job_id = str(uuid.uuid4())
        
       
        pipe = r.pipeline()
        pipe.lpush("jobs:queue", job_id)
        pipe.hset(f"job:{job_id}", mapping={"status": "queued"})
        pipe.execute()
        
        return {"job_id": job_id}
    except redis.ConnectionError:
        raise HTTPException(status_code=503, detail="Redis storage is unavailable")

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {"job_id": job_id, "status": status}
