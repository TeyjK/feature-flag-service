# Load Test Results

## Test Environment
- MacBook Air M1, 16GB RAM
- Docker Desktop
- Single FastAPI instance (uvicorn)

## Baseline Test (Before Optimization)
Date: 2026-01-19

### Configuration
- 100 concurrent users
- 2 minute duration
- Endpoint: `/api/v1/flags/{flag_id}/evaluate`

### Results
- **Throughput:** 713 requests/second
- **Total Requests:** 85,642
- **Success Rate:** 100%
- **Latency:**
  - Average: 5.11ms
  - Median (P50): 4.07ms
  - P90: 8.75ms
  - P95: 12.39ms