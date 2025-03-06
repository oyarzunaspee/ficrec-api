from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import  OAuth2PasswordRequestForm
from app.schemas import User, Token
from typing import Annotated
from fastapi_problem.error import BadRequestProblem

router = APIRouter()

# POST FOR TOKEN (LOG IN)
@router.post("/login")
async def login(
        user_form: Annotated[OAuth2PasswordRequestForm, Depends()]
    ):
    
    user_exists = await User.find_by_username(user_form.username)
    if user_exists is None:
        raise BadRequestProblem(detail="Wrong username or password")
    
    verify_password = user_exists.verify_password(user_form.password)
    if verify_password is False:
        raise BadRequestProblem(detail="Wrong username or password")
    
    token = Token.create_access_token(user_exists)

    return {"status": status.HTTP_200_OK, "access_token": token}