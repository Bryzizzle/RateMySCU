import os

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from fastapi import FastAPI
from fastapi import Request
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse, RedirectResponse


from .jwt import create_token
from .jwt import CREDENTIALS_EXCEPTION
from .jwt import valid_email

# Create the auth app
auth_app = FastAPI()

# OAuth settings
# GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or None
# GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') or None
# if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
#     raise BaseException('Missing env variables')
GOOGLE_CLIENT_ID="744412575012-m7ku9m3bap3pqnn09639gtgc523k13bb.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"

# Set up OAuth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# Set up the middleware to read the request session
# SECRET_KEY = os.environ.get('SECRET_KEY') or None
# if SECRET_KEY is None:
#     raise 'Missing SECRET_KEY'
SECRET_KEY="secret-string"
auth_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Frontend URL:
# FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://127.0.0.1:7000/token'


@auth_app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('token')  # This creates the url for our /token endpoint
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_app.get('/token')
async def auth(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise CREDENTIALS_EXCEPTION
    user_data = await oauth.google.parse_id_token(request, access_token)
    if valid_email(user_data['email']):
        return JSONResponse({"status": "200", "access_token": create_token(user_data['email'])})
    raise CREDENTIALS_EXCEPTION


@auth_app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        return {"status": "loggedin"}
    return {"status": "loggedout"}


@auth_app.route('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
