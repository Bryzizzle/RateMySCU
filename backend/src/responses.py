from fastapi import HTTPException

UNAUTHORIZED_EXCEPTION = HTTPException(
    status_code=401,
    detail='Please Login to access this application'
)

NON_SCU_EXCEPTION = HTTPException(
    status_code=403,
    detail='This application is only available to SCU-affiliated individuals, please login with your @scu.edu email!'
)
