"""Check last failed job error"""
from redis import Redis
from rq import Queue
from rq.registry import FailedJobRegistry
from rq.job import Job

r = Redis(host='localhost', port=6379, db=0)
q = Queue('svd_jobs', connection=r)
failed = FailedJobRegistry(queue=q)

if len(failed) > 0:
    job_id = failed.get_job_ids()[-1]  # Last failed
    job = Job.fetch(job_id, connection=r)
    print(f"Job ID: {job_id}")
    print(f"Status: {job.get_status()}")
    print(f"\nFull error:")
    print(job.exc_info)
else:
    print("No failed jobs")

