from fastapi import APIRouter, status, Depends, Response
from fastapi.security import  OAuth2PasswordRequestForm
from app.schemas import User
from app.security.token import create_access_token
from typing import Annotated
from fastapi_problem.error import BadRequestProblem

router = APIRouter()

# POST FOR TOKEN (LOG IN)
@router.post("/login")
async def login(
        user_form: Annotated[OAuth2PasswordRequestForm, Depends()],
        response: Response
    ):
    
    user_exists = await User.find_by_username(user_form.username)
    if not user_exists:
        raise BadRequestProblem(detail="Wrong username or password")
    
    verify_password = user_exists.verify_password(user_form.password)
    if not verify_password:
        raise BadRequestProblem(detail="Wrong username or password")
    
    token = create_access_token(str(user_exists.id))

    response.set_cookie(
        key = "access_token",
        value = f"Bearer {token}",
        httponly = True,
        # same_site = True,
        secure = True
    )
    return {"status": status.HTTP_200_OK}