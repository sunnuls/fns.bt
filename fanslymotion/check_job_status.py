"""Check job status from Redis."""
import redis
import json

r = redis.Redis(decode_responses=False)
job_id = '31e1d7c4-0211-4b41-ac3a-17b6e71e3662'
meta_key = f'job:{job_id}:metadata'

meta = r.get(meta_key)
if meta:
    data = json.loads(meta)
    print(f"Job ID: {job_id}")
    print(f"Status: {data.get('status')}")
    print(f"Progress: {data.get('progress', 0)}%")
    print(f"Message: {str(data.get('message', 'N/A'))[:200]}")
    print(f"Started: {data.get('started_at', 'N/A')}")
    if data.get('error'):
        print(f"Error: {str(data.get('error'))[:300]}")
else:
    print("Job not found in Redis")

