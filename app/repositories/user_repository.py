from typing import List, Optional
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate


class IUserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserModel]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[UserModel]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        pass

    @abstractmethod
    def create(self, user: UserCreate) -> UserModel:
        pass

    @abstractmethod
    def update(self, id: int, user: UserUpdate) -> Optional[UserModel]:
        pass

    @abstractmethod
    def soft_delete(self, id: int) -> bool:
        pass

    @abstractmethod
    def restore(self, id: int) -> Optional[UserModel]:
        pass


class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return (
            self.db.query(UserModel)
            .filter(UserModel.email == email, UserModel.is_active == True)
            .first()
        )

    def get_by_id(self, id: int) -> Optional[UserModel]:
        return (
            self.db.query(UserModel)
            .filter(UserModel.id == id, UserModel.is_active == True)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        return (
            self.db.query(UserModel)
            .filter(UserModel.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, user: UserCreate) -> UserModel:
        db_user = UserModel(
            email=user.email,
            full_name=user.full_name,
            hashed_password=f"hashed_{user.password}",
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update(self, id: int, user: UserUpdate) -> Optional[UserModel]:
        db_user = self.get_by_id(id)
        if not db_user:
            return None
        update_data = user.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def soft_delete(self, id: int) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.id == id).first()
        if not db_user:
            return False
        db_user.is_active = False
        db_user.deleted_at = func.now()
        self.db.commit()
        return True

    def restore(self, id: int) -> Optional[UserModel]:
        db_user = self.db.query(UserModel).filter(UserModel.id == id).first()
        if not db_user:
            return None
        db_user.is_active = True
        db_user.deleted_at = None
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
