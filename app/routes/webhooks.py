import asyncio
import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Transaction
from app.schemas import WebhookRequest, WebhookAckResponse
from app.services.processor import process_transaction

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/webhooks", tags=["Webhooks"])


@router.post(
    "/transactions",
    response_model=WebhookAckResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive transaction webhook",
    description="Accepts a transaction webhook, acknowledges immediately, and processes in the background.",
)
async def receive_transaction_webhook(
    payload: WebhookRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Receive a transaction webhook from a payment processor.

    - Returns 202 Accepted immediately (within 500ms)
    - Checks for duplicate transaction_id (idempotency)
    - Enqueues background processing with 30s simulated delay
    """
    # Check if transaction already exists (idempotency)
    result = await db.execute(
        select(Transaction).where(
            Transaction.transaction_id == payload.transaction_id
        )
    )
    existing = result.scalar_one_or_none()

    if existing is not None:
        logger.info(f"Duplicate webhook for {payload.transaction_id}, returning 202 (idempotent)")
        return WebhookAckResponse(
            message="Webhook already received",
            transaction_id=payload.transaction_id,
        )

    # Create new transaction record with PROCESSING status
    transaction = Transaction(
        transaction_id=payload.transaction_id,
        source_account=payload.source_account,
        destination_account=payload.destination_account,
        amount=payload.amount,
        currency=payload.currency,
        status="PROCESSING",
    )
    db.add(transaction)
    await db.commit()

    # start the background task 
    asyncio.create_task(process_transaction(payload.transaction_id))

    return WebhookAckResponse(
        message="Webhook received",
        transaction_id=payload.transaction_id,
    )
