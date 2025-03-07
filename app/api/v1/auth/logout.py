from fastapi import APIRouter, status, Response, Cookie

router = APIRouter()


@router.post("/logout")
async def logout(
        response: Response,
        access_token: str | None = Cookie(default=None)
    ):
    response.delete_cookie("access_token")
    return {"status": status.HTTP_200_OK}