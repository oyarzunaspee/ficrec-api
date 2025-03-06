from passlib.context import CryptContext
PW_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")