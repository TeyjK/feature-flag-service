# Feature Flag Service

High-throughput backend service for feature flag evaluation. Handles 714 RPS with 11.79ms P95 latency using three-tier caching (Redis → PostgreSQL → in-memory).

## What This Does

Lets applications toggle features on/off for specific users without redeploying. Uses consistent hashing to ensure users get stable assignments even when rollout percentages change.

**Core features:**
- Deterministic user bucketing (MurmurHash3)
- Three-tier caching with graceful degradation
- API key auth + rate limiting (1000 req/min)
- JSON structured logging

---

## Architecture
```
Client Request
    ↓
Authentication + Rate Limiting
    ↓
Redis Cache (1-2ms) → PostgreSQL (10-20ms) → In-Memory Snapshot
    ↓
Consistent Hashing Evaluation
    ↓
Response
```

**Key components:**
- **Redis**: Hot cache, 60s TTL
- **PostgreSQL**: Source of truth for flags and API keys
- **In-memory snapshot**: Last-resort fallback when both fail
- **Evaluation engine**: `hash(user_id:flag_id) % 10000 < (rollout% * 100)`

---

## Quick Start

**Prerequisites:** Docker, Python 3.11+
```bash
# Clone and setup
git clone <repo>
cd feature-flag-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start services
cp .env.example .env
docker-compose up -d

# Run migrations
docker-compose exec postgres psql -U username -d flags -f /migrations/001_initial_schema.sql

# Generate API key
python3 -c "import secrets; print(secrets.token_hex(16))"

# Insert key (replace YOUR_KEY)
docker-compose exec postgres psql -U username -d flags -c "
  CREATE EXTENSION IF NOT EXISTS pgcrypto;
  INSERT INTO api_keys (key_id, key_hash, name, rate_limit)
  VALUES ('test-key', encode(digest('YOUR_KEY', 'sha256'), 'hex'), 'Test Key', 100000);
"

# Start app
uvicorn app.main:app --reload

# Test at http://localhost:8000/docs
```

---

## API

**Authentication:** All endpoints require `X-API-Key` header.

### Evaluate Flag (Hot Path)
```
GET /api/v1/flags/{flag_id}/evaluate?user_id={user_id}&environment=prod
```

Returns:
```json
{
  "flag_id": "new-checkout",
  "enabled": true,
  "user_id": "user-123",
  "evaluated_at": "2026-01-19T12:00:00Z"
}
```

**Logic:**
1. If `flag.enabled == false` → return `enabled: false`
2. Compute `hash(user_id:flag_id) % 10000`
3. Return `enabled: (bucket < rollout_percentage * 100)`

### Other Endpoints
- `GET /flags/{flag_id}` - Get single flag
- `GET /flags?environment={env}` - List all flags
- `POST /flags` - Create flag
- `PUT /flags/{flag_id}` - Update flag (increments version, invalidates cache)
- `DELETE /flags/{flag_id}` - Delete flag

Full docs: `http://localhost:8000/docs`

---

## Performance

**Test setup:** MacBook Air M4, 100 concurrent users, 2min sustained load

| Metric | Value |
|--------|-------|
| Throughput | 714 req/s |
| Success Rate | 100% |
| P50 | 4.11ms |
| P95 | 11.79ms |

**Optimization attempt:** Cached API keys in Redis to reduce database hits. Result: performance degraded (P95: 19.61ms) due to Redis pool exhaustion. Fixed by increasing pool from 50→200 connections, then removed caching overhead entirely. Final result: 5% improvement over baseline.

---

## Design Decisions

**Why consistent hashing?**  
Same user always gets same bucket. Increasing rollout from 25%→50% keeps original 25% enabled. Alternative (random assignment) would cause users to flip-flop between enabled/disabled.

**Why cache-aside pattern?**  
System works even if cache fails. Simpler than write-through. Tradeoff: 60s staleness acceptable for feature flags.

**Why MurmurHash3?**  
Fast (2-3x faster than SHA-256) and sufficient distribution for bucketing. Don't need cryptographic security, just uniform distribution.

**Why % 10000**  
Finer granularity (0.01% precision) and better distribution. Reduces modulo bias.

**Why three-tier caching?**  
Availability > consistency for feature flags. Better to serve stale data (99% rollout when cache says 100%) than return errors.

---

## Testing
```bash

# Load tests
uvicorn app.main:app --reload
k6 run load_tests/baseline.js  # in another terminal
```

---

## What I'd Add Next

- Flag versioning with rollback
- User attribute targeting (age, country, platform)
- Metrics dashboard (Grafana)
- Client SDKs (Python, Node.js)
- Chaos testing with quantified blast radius

---

## Project Structure
```
app/
├── api/           # Endpoints, auth, rate limiting
├── services/      # Business logic, hashing, snapshot
├── middleware/    # Logging, request timing
├── cache.py       # Redis operations
├── database.py    # PostgreSQL pool
└── main.py        # FastAPI app

migrations/        # Database schema
load_tests/        # k6 performance tests
```