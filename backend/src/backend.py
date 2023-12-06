import os

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from fastapi import FastAPI, HTTPException, UploadFile, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
from starlette.responses import HTMLResponse, RedirectResponse

from pydantic import BaseModel
from typing import Optional

from .database import *
from .scueval.structs import *
from .evalupload import *


# BACKEND API FOR ACCESSING EVALUATIONS DATABASE

# EvalRequest: object for eval request body
class EvalRequest(BaseModel):
    id: Optional[str] = None
    classname: Optional[str] = None
    classcode: Optional[str] = None
    quarter: Optional[str] = None
    year: Optional[int] = None
    professor: Optional[str] = None
    overall: Optional[float] = None
    overallSearch: Optional[str] = None  # greaterThan, lessThan, equals

# Error
CREDENTIALS_EXCEPTION = HTTPException(
    status_code='401',
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key="!secret")

# Set up OAuth
config_data = {'GOOGLE_CLIENT_ID': os.environ.get('GOOGLE_CLIENT_ID'),
               'GOOGLE_CLIENT_SECRET': os.environ.get('GOOGLE_CLIENT_SECRET')}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
print("oauth registered")

# Endpoints for OAuth
@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return CREDENTIALS_EXCEPTION
    user = token.get('userinfo')
    if "@scu.edu" in user["email"]:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/')


@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        return {"status": "loggedin", "email": user["email"]}
    return {"status": "loggedout"}


@app.route('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


# Create a connection to Postgres database
def getConnection():
    return create_connection(os.environ.get('POSTGRES_DATABASE'), os.environ.get('POSTGRES_USER'),
                             os.environ.get('POSTGRES_PASSWORD'), os.environ.get('POSTGRES_HOST'),
                             os.environ.get('POSTGRES_PORT'))


@app.get("/api/v0")
async def root():
    return health_check()


@app.get("/api/{api_path:path}")
async def invalid_endpoint():
    raise HTTPException(status_code=404, detail="Invalid API Endpoint")


@app.get("/check")  # added function to create connection
async def health_check():
    return {"status": "OK", "version": "dev"}


# @app.get("{full_path:path}")
# async def not_api_call():
#     return RedirectResponse("https://ratemyscu.bryan.cf")


# select_evaluations: POST endpoint for returning evaluations based on search criteria
@app.post("/getEvals")
async def select_evaluations(request: EvalRequest, email: str):
    if "@scu.edu" not in email:
        return CREDENTIALS_EXCEPTION
    try:
        connection = getConnection()
        # build query and get evals from database
        query = request_query_builder(request)
        print(query)
        evals = select_query(connection, query)

        return {"status": "200", "result": evals}
    except Exception as e:
        return {"status": "500", "error": str(e)}


# request_query_builder: builds an SQL query based on request body from select_evalutations
def request_query_builder(request: EvalRequest):
    query = "SELECT * FROM evals"
    query_builder = []
    if any(field is not None for field in dict(request).values()):
        query += (" WHERE ")
        if request.id:
            query_builder.append("id='" + request.id + "'")
        if request.classname:
            query_builder.append("classname='" + request.classname + "'")
        if request.classcode:
            query_builder.append("classcode='" + request.classcode + "'")
        if request.quarter:
            query_builder.append("quarter='" + request.quarter + "'")
        if request.year:
            query_builder.append("year=" + str(request.year))
        if request.professor:
            query_builder.append("professor='" + request.professor + "'")
        if request.overall and request.overallSearch:
            if request.overallSearch == "greaterThan":
                query_builder.append("overall>=" + str(request.overall))
            elif request.overallSearch == "lessThan":
                query_builder.append("overall<=" + str(request.overall))
            elif request.overallSearch == "equals":
                query_builder.append("overall=" + str(request.overall))
    query += " AND ".join(query_builder) + ";"
    return query


# test: temporary GET endpoint for testing evaluation upload system
@app.post("/uploadEvals")
async def manual_upload_evaluations(file: UploadFile):
    # This is the id that should be use in the evals
    file_id = file.filename.split(".")[0]
    print(f"Processing evaluation with ID: {file_id}")

    try:
        connection = getConnection()
        upload_system(connection, file)
        return {"status": "200", "filename": file_id}
    except Exception as e:
        return {"status": "500", "error": str(e)}


@app.get("/getIDs")
async def get_all_ids():
    try:
        cursor = getConnection().cursor()
        cursor.execute("SELECT id FROM evals")

        result = [row[0] for row in cursor.fetchall()]
        print(result)

        return {"status": "200", "result": result}
    except Exception as e:
        return {"status": "500", "error": str(e)}
