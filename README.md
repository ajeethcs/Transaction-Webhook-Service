# Transaction Webhook Processing Service

A Python backend service that receives transaction webhooks from external payment processors (like RazorPay), acknowledges them immediately, and processes transactions reliably in the background.

## Setup & Run Locally

### Prerequisites
- Python 3.10+

### Install & Run

```bash
# Clone the repo
git clone https://github.com/ajeethcs/Transaction-Webhook-Service
cd confluencr-assignment

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the service (uses SQLite locally by default)
uvicorn app.main:app --reload
```

The server starts at **http://localhost:8000**. API docs are available at **http://localhost:8000/docs**.

## Technical Choices

- **FastAPI**: Chosen for its high performance and native support for asynchronous programming.
- **Asynchronous Database Access**: Using **SQLAlchemy (Async)** with `asyncpg` (for PostgreSQL) or `aiosqlite` (for local development) to ensure the database operations do not block the main event loop.
- **Background Task Processing**: Using `asyncio.create_task` for lightweight, non-blocking background processing. This allows the service to acknowledge webhook receipts within the 500ms requirement while continuing to process the data.
- **Pydantic**: Used for strict data validation and schema definition, ensuring only valid transaction data is accepted.
- **Idempotency**: Implemented a check on the `transaction_id` to ensure that duplicate webhooks from the same transaction are not processed multiple times, which is critical for reliable financial processing.

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

### 4. Check Again After 35 Seconds
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

Deployed at: https://transaction-webhook-service-e8eq.onrender.com/

