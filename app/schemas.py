from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WebhookRequest(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier")
    source_account: str = Field(..., description="Source account ID")
    destination_account: str = Field(..., description="Destination account ID")
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(..., description="Currency code (e.g. INR, USD)")


class TransactionResponse(BaseModel):
    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str = "HEALTHY"
    current_time: datetime


class WebhookAckResponse(BaseModel):

    message: str = "Webhook received"
    transaction_id: str
