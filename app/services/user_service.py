from app.repositories.user_repository import IUserRepository
from app.schemas.user import UserCreate
from fastapi import HTTPException

class UserService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def register_user(self, user_in: UserCreate):
        user = self.user_repo.get_by_email(user_in.email)
        if user:
            raise HTTPException(status_code=400, detail="User already exists")
        return self.user_repo.create(user_in)
