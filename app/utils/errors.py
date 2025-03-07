from starlette.exceptions import HTTPException

class ExpirationProblem(HTTPException):
     status_code: int = 307
     detail: str = "Token has expired"

     def __init__(self):
         super().__init__(status_code=self.status_code, detail=self.detail)