from typing import List, Optional
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.schemas.user import UserCreate

class IUserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserModel]:
        pass

    @abstractmethod
    def create(self, user: UserCreate) -> UserModel:
        pass

class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def create(self, user: UserCreate) -> UserModel:
        db_user = UserModel(
            email=user.email,
            full_name=user.full_name,
            hashed_password=f"hashed_{user.password}"  # Simplificado para o exemplo
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
