from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
from starlette.responses import RedirectResponse

from .evalupload import *
from .responses import UNAUTHORIZED_EXCEPTION, NON_SCU_EXCEPTION
from .database import get_connection, request_query_builder

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get('SESSION_SECRET')
)

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


# Endpoints for OAuth
@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request):
    """
    OAuth redirect destination, saves the user information and redirect the user back to the frontend

    :param request: Request structure for authentication
    """

    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return UNAUTHORIZED_EXCEPTION

    user = token.get('userinfo')
    if user["hd"] == "scu.edu":
        request.session['user'] = dict(user)
    return RedirectResponse(url='https://ratemyscu.bryan.cf/')


@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        return {"status": "loggedin", "email": user["email"]}
    return {"status": "loggedout"}


@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


@app.get("/api/v0")
async def root():
    return health_check()


@app.get("/api/{api_path:path}")
async def invalid_endpoint():
    raise HTTPException(status_code=404, detail="Invalid API Endpoint")


@app.get("/check")
async def health_check():
    return {"status": "OK", "version": "dev"}


# @app.get("{full_path:path}")
# async def not_api_call():
#     return RedirectResponse("https://ratemyscu.bryan.cf")


@app.post("/getEvals")
async def select_evaluations(req: Request, request: EvalRequest):
    """
    POST endpoint for returning evaluations based on search criteria

    :param req: The request provided by a middleware for authentication
    :param request: The request (formatted as an evaluation) provided by the user
    :return:
    """

    if req.session.get("user", None) is None or req.session["user"].get("hd", None) != "scu.edu":
        return NON_SCU_EXCEPTION
    try:
        connection = get_connection()
        # build query and get evals from database
        query = request_query_builder(request)
        print(query)
        evals = select_query(connection, query)

        return {"status": "200", "result": evals}
    except Exception as e:
        return {"status": "500", "error": str(e)}


@app.post("/uploadEvals")
async def manual_upload_evaluations(file: UploadFile):
    """
    Endpoint to process and upload evaluation PDFs to the database

    :param file: File passed in by the request
    """

    # This is the id that should be use in the evals
    file_id = file.filename.split(".")[0]
    print(f"Processing evaluation with ID: {file_id}")

    try:
        connection = get_connection()
        upload_system(connection, file)
        return {"status": "200", "filename": file_id}
    except Exception as e:
        return {"status": "500", "error": str(e)}


@app.get("/getIDs")
async def get_all_ids():
    """
    Endpoint to get all the evaluation IDs currently in the database
    """
    try:
        cursor = get_connection().cursor()
        cursor.execute("SELECT id FROM evals")

        result = [row[0] for row in cursor.fetchall()]
        print(result)

        return {"status": "200", "result": result}
    except Exception as e:
        return {"status": "500", "error": str(e)}
