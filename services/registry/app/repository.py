from typing import List
from sqlalchemy.orm import Session
from .models import Household

class HouseholdRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> List[Household]:
        return self.db.query(Household).limit(100).all()

