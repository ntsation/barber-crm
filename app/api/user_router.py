from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

router = APIRouter()


@router.post("/", response_model=User)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return user_service.register_user(user_in)


@router.get("/", response_model=List[User])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return user_service.get_all_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return user_service.get_user(user_id)


@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return user_service.update_user(user_id, user_in)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    user_service.soft_delete_user(user_id)
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/restore", response_model=User)
def restore_user(user_id: int, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return user_service.restore_user(user_id)
