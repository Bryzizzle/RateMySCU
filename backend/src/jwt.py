import os
from datetime import datetime
from datetime import timedelta

import jwt
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer


# Helper to read numbers using var envs
def cast_to_number(id):
    temp = os.environ.get(id)
    if temp is not None:
        try:
            return float(temp)
        except ValueError:
            return None
    return None


# Configuration
# API_SECRET_KEY = os.environ.get('API_SECRET_KEY') or None
# if API_SECRET_KEY is None:
#     raise BaseException('Missing API_SECRET_KEY env var.')
API_SECRET_KEY="secret-string"
API_ALGORITHM = 'HS256'
API_ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Token url (We should later create a token url that accepts just a user and a password to use swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

# Error
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)


# Create token internal function
def create_access_token(email):
    data={'sub': email}
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=API_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    access_token = jwt.encode(to_encode, API_SECRET_KEY, algorithm=API_ALGORITHM)
    return access_token


def valid_email(email):
    return "@scu.edu" in email


async def get_current_user_email(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, API_SECRET_KEY, algorithms=[API_ALGORITHM])
        email: str = payload.get('sub')
        if email is None:
            raise CREDENTIALS_EXCEPTION
    except jwt.PyJWTError:
        raise CREDENTIALS_EXCEPTION
    if valid_email(email):
        return email
    raise CREDENTIALS_EXCEPTION
