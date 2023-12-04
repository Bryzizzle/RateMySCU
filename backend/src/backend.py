import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
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
    overallSearch: Optional[str] = None # greaterThan, lessThan, equals


app = FastAPI()
connection = create_connection(os.environ.get('POSTGRES_DATABASE'), os.environ.get('POSTGRES_USER'),
    os.environ.get('POSTGRES_PASSWORD'), os.environ.get('POSTGRES_HOST'), os.environ.get('POSTGRES_PORT'))


@app.get("/api/v0")
async def root():
    return health_check()


@app.get("/api/{api_path:path}")
async def invalid_endpoint():
    raise HTTPException(status_code=404, detail="Invalid API Endpoint")


@app.get("/check") # added function to create connection
async def health_check():
    global connection 
    connection = create_connection(os.environ.get('POSTGRES_DATABASE'), os.environ.get('POSTGRES_USER'),
        os.environ.get('POSTGRES_PASSWORD'), os.environ.get('POSTGRES_HOST'), os.environ.get('POSTGRES_PORT'))
    return {"status": "OK", "version": "dev"}


# @app.get("{full_path:path}")
# async def not_api_call():
#     return RedirectResponse("https://ratemyscu.bryan.cf")


# select_evaluations: POST endpoint for returning evaluations based on search criteria
@app.post("/getEvals")
async def select_evaluations(request: EvalRequest):
    try:
        # build query and get evals from database
        query = request_query_builder(request)
        print(query)
        evals = select_query(connection, query)

        return { "status": "200", "result": evals }
    except Exception as e:
        return { "status": "500", "error": str(e) }

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
    try:
        upload_system(connection, file.filename)
        return { "status": "200", "file name": file.filename }
    except Exception as e:
        return { "status": "500", "error": str(e) }
