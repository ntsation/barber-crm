from app.repositories.user_repository import IUserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User as UserModel
from fastapi import HTTPException


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def register_user(self, user_in: UserCreate):
        user = self.user_repo.get_by_email(user_in.email)
        if user:
            raise HTTPException(status_code=400, detail="User already exists")
        return self.user_repo.create(user_in)

    def get_user(self, id: int) -> UserModel:
        user = self.user_repo.get_by_id(id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_all_users(self, skip: int = 0, limit: int = 100):
        return self.user_repo.get_all(skip=skip, limit=limit)

    def update_user(self, id: int, user_in: UserUpdate):
        user = self.user_repo.get_by_id(id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user_in.email and user_in.email != user.email:
            existing_user = self.user_repo.get_by_email(user_in.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
        return self.user_repo.update(id, user_in)

    def soft_delete_user(self, id: int):
        user = self.user_repo.get_by_id(id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self.user_repo.soft_delete(id)

    def restore_user(self, id: int):
        user = self.user_repo.restore(id)
        if not user:
            raise HTTPException(
                status_code=404, detail="User not found or already active"
            )
        return user
