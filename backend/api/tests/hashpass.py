import bcrypt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

new_password = "testor123#"  # replace with your chosen password
hashed_password = hash_password(new_password)
print(hashed_password)

