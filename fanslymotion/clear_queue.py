"""Clear failed jobs from Redis queue"""
from redis import Redis
from rq.registry import FailedJobRegistry
from rq import Queue

r = Redis(host='localhost', port=6379, db=0)
q = Queue('svd_jobs', connection=r)
failed = FailedJobRegistry(queue=q)

count = len(failed.get_job_ids())
for job_id in failed.get_job_ids():
    failed.remove(job_id)

print(f"Cleared {count} failed jobs")

