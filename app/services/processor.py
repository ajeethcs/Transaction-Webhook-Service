import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def process_transaction(transaction_id: str) -> None:
    """
    Background task that processes a transaction.

    Simulates external API calls with a 30-second delay,
    then updates the transaction status to PROCESSED.
    Uses its own database session (independent of the request lifecycle).
    """
    logger.info(f"Starting background processing for {transaction_id}")

    try:
        # Simulate external API call processing time
        await asyncio.sleep(30)

        # Update transaction status in a fresh session
        async with AsyncSessionLocal() as session:
            from app.models import Transaction

            result = await session.execute(
                select(Transaction).where(
                    Transaction.transaction_id == transaction_id
                )
            )
            transaction = result.scalar_one_or_none()

            if transaction is None:
                logger.error(f"Transaction {transaction_id} not found during processing")
                return

            if transaction.status == "PROCESSED":
                logger.info(f"Transaction {transaction_id} already processed, skipping")
                return

            transaction.status = "PROCESSED"
            transaction.processed_at = datetime.now(timezone.utc)
            await session.commit()

            logger.info(f"Transaction {transaction_id} processed successfully")

    except Exception as e:
        logger.error(f"Error processing transaction {transaction_id}: {e}")
        # Transaction stays in PROCESSING status — can be retried
        raise
