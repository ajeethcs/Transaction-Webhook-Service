# Transaction Webhook Processing Service

A Python backend service that receives transaction webhooks from external payment processors (like RazorPay), acknowledges them immediately, and processes transactions reliably in the background.

## Features

- **Fast Webhook Acknowledgment** — Returns `202 Accepted` within 500ms
- **Background Processing** — Transactions processed asynchronously with 30s simulated delay
- **Idempotency** — Duplicate webhooks with the same `transaction_id` are handled gracefully
- **Persistent Storage** — All transactions stored with status and timing information
- **Health Check** — `GET /` endpoint for monitoring

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Framework | **FastAPI** | Async-native, automatic OpenAPI docs, built-in request validation |
| Database | **PostgreSQL** (cloud) / **SQLite** (local) | PostgreSQL for production reliability; SQLite for zero-config local dev |
| ORM | **SQLAlchemy 2.0 (async)** | Industry standard async ORM with robust migration support |
| Background Tasks | **asyncio.create_task** | Lightweight, no extra infrastructure — ideal for this use case |
| Deployment | **Render** | Free tier with managed PostgreSQL |

### Why These Choices?

- **FastAPI + asyncio** — The webhook endpoint must respond in <500ms while processing takes 30s. FastAPI's async nature enables true non-blocking I/O: the webhook handler inserts a DB record, fires off an `asyncio.create_task`, and returns immediately.
- **transaction_id as Primary Key** — Using the transaction ID as the natural primary key enforces idempotency at the database level. A duplicate insert attempt is caught before any processing begins.
- **asyncio.create_task over Celery/RQ** — For a 30s sleep simulation, a full task queue adds unnecessary complexity. `asyncio.create_task` provides fire-and-forget semantics within the same process, which is sufficient for this assessment scope.

## API Endpoints

| Method | Path | Description | Status Code |
|--------|------|-------------|-------------|
| `GET` | `/` | Health check | `200` |
| `POST` | `/v1/webhooks/transactions` | Receive webhook | `202` |
| `GET` | `/v1/transactions/{transaction_id}` | Query transaction | `200` / `404` |

## Setup & Run Locally

### Prerequisites
- Python 3.10+

### Install & Run

```bash
# Clone the repo
git clone <repo-url>
cd confluencr-assignment

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the service (uses SQLite locally by default)
uvicorn app.main:app --reload
```

The server starts at **http://localhost:8000**. Interactive API docs are available at **http://localhost:8000/docs**.

### Using PostgreSQL (optional)

Set the `DATABASE_URL` environment variable:

```bash
# .env file
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## Testing the Service

### 1. Health Check
```bash
curl http://localhost:8000/
```

### 2. Send a Transaction Webhook
```bash
curl -X POST http://localhost:8000/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_abc123def456",
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": 1500,
    "currency": "INR"
  }'
# Expected: 202 Accepted
```

### 3. Check Transaction Status (immediately)
```bash
curl http://localhost:8000/v1/transactions/txn_abc123def456
# Expected: status = "PROCESSING"
```

### 4. Check Again After ~35 Seconds
```bash
curl http://localhost:8000/v1/transactions/txn_abc123def456
# Expected: status = "PROCESSED", processed_at is populated
```

### 5. Test Idempotency (send duplicate)
```bash
curl -X POST http://localhost:8000/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_abc123def456",
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": 1500,
    "currency": "INR"
  }'
# Expected: 202 Accepted (no duplicate processing)
```

## Public API Endpoint

🌐 **Deployed at**: _[URL will be added after deployment]_

## Project Structure

```
├── app/
│   ├── main.py              # FastAPI app, health check, lifespan
│   ├── config.py            # Settings from environment
│   ├── database.py          # Async SQLAlchemy engine & session
│   ├── models.py            # Transaction ORM model
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── routes/
│   │   ├── webhooks.py      # POST /v1/webhooks/transactions
│   │   └── transactions.py  # GET /v1/transactions/{id}
│   └── services/
│       └── processor.py     # Background transaction processor
├── requirements.txt
├── Procfile
└── README.md
```
