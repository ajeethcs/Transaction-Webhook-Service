from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True, index=True)
    source_account = Column(String, nullable=False)
    destination_account = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False, default="PROCESSING")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    processed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Transaction {self.transaction_id} status={self.status}>"
