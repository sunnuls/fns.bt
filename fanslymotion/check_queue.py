"""Check Redis queue status"""
from redis import Redis
from rq import Queue
from rq.registry import FailedJobRegistry, StartedJobRegistry
from rq.job import Job

r = Redis(host='localhost', port=6379, db=0)
q = Queue('svd_jobs', connection=r)
started = StartedJobRegistry(queue=q)
failed = FailedJobRegistry(queue=q)

print(f"Queue: {len(q)} tasks")
print(f"Started: {len(started)} tasks")
print(f"Failed: {len(failed)} tasks")

if len(started) > 0:
    print("\nStarted jobs:")
    for job_id in started.get_job_ids():
        job = Job.fetch(job_id, connection=r)
        print(f"  {job_id}: {job.get_status()}")

if len(failed) > 0:
    print("\nFailed jobs:")
    for job_id in failed.get_job_ids()[:3]:  # Last 3
        job = Job.fetch(job_id, connection=r)
        print(f"  {job_id}: {job.get_status()}")
        if job.exc_info:
            print(f"    Error: {job.exc_info[:200]}")

