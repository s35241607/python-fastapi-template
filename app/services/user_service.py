


from fastapi import Depends
from app.dependencies import get_user_repository


class UserService:
  def __init__(self, user_repository: Depends(get_user_repository)):
      self.user_repository = user_repository

  async def list_users(self):