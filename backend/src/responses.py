from fastapi import HTTPException

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=401,
    detail='Could not validate credentials'
)