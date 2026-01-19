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

  ## After Optimization (Removed Logging Overhead)
Date: 2026-01-19

### Changes Made
- Removed timing calculations in hot path
- Removed INFO-level logging (kept ERROR/WARNING)
- Simplified flag service code

### Results
- **Throughput:** 714 requests/second (+0.1%)
- **Total Requests:** 85,689
- **Success Rate:** 100%
- **Latency:**
  - Average: 5.05ms
  - Median (P50): 4.11ms
  - P90: 8.62ms
  - P95: 11.79ms (-5%)

### Analysis
Removing timing and logging overhead from the hot path improved P95 latency by 5%. The main bottleneck is now authentication and rate limiting, which happen on every request before the cached flag lookup.