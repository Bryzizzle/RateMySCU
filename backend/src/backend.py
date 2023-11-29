import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from .database import *

app = FastAPI()
load_dotenv()
connection = create_connection(os.getenv('POSTGRES_DATABASE'), os.getenv('POSTGRES_USER'),
    os.getenv('POSTGRES_PASSWORD'), os.getenv('POSTGRES_HOST'), os.getenv('POSTGRES_PORT'))


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

    
@app.get("/getEvals")
async def select_evaluations():
    table_name = "evals"
    query = "SELECT * FROM " + table_name + ";"
    try:
        evals = select_query(connection, query)
        return { "status": "200", "result": evals }
    except Exception as e:
        return { "status": "500", "error": e }
