from typing import List
from sqlalchemy.orm import Session
from .models import Payment

class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> List[Payment]:
        return self.db.query(Payment).limit(100).all()

