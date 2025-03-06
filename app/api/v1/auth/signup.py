from fastapi import APIRouter, status
from app.schemas import User, SignUpForm
from fastapi_problem.error import BadRequestProblem

router = APIRouter()

# POST NEW USER (REGISTER)
@router.post("/signup")
async def create_user(
        user_form: SignUpForm
    ):
    user_exists = await User.find_by_username(user_form.username)
    if user_exists:
        raise BadRequestProblem(detail="Username already taken")

    if user_form.password != user_form.match_password:
        raise BadRequestProblem(detail="Passwords do not match")
    
    new_user = User(
        username = user_form.username,
        password = SignUpForm.hash_password(user_form.password)
    )
    await User.insert(new_user)
    return {"status": status.HTTP_201_CREATED}