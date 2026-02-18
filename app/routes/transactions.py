from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Transaction
from app.schemas import TransactionResponse

router = APIRouter(prefix="/v1/transactions", tags=["Transactions"])


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction status",
    description="Retrieve the current status and details of a transaction by its ID.",
)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a transaction by its ID.

    Returns the full transaction details including current status
    (PROCESSING or PROCESSED) and timing information.
    """
    result = await db.execute(
        select(Transaction).where(
            Transaction.transaction_id == transaction_id
        )
    )
    transaction = result.scalar_one_or_none()

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found",
        )

    return transaction
