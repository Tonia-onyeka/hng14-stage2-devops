import redis
import time
import os
import signal
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = os.getenv("QUEUE_NAME", "jobs:queue")

shutdown = False

def handle_shutdown(signum, frame):
    global shutdown
    logger.info("Shutdown signal received")
    shutdown = True

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

def get_redis():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        socket_connect_timeout=5,
        socket_timeout=5,
    )

def process_job(r, job_id):
    logger.info(f"Processing job {job_id}")
    time.sleep(2)
    r.hset(f"job:{job_id}", "status", "completed")
    logger.info(f"Completed job {job_id}")

def main():
    r = get_redis()

    while not shutdown:
        try:
            job = r.brpop(QUEUE_NAME, timeout=5)
            if job:
                _, job_id = job
                process_job(r, job_id.decode())
        except redis.exceptions.RedisError as e:
            logger.error(f"Redis error: {e}")
            time.sleep(2)

    logger.info("Worker shutting down gracefully")
    sys.exit(0)

if __name__ == "__main__":
    main()
