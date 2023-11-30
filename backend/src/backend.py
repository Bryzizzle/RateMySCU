import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from .database import *
from .scueval.structs import *
from .evalupload import *


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


@app.get("/check")
async def health_check():
    return {"status": "OK", "version": "dev"}


# @app.get("{full_path:path}")
# async def not_api_call():
#     return RedirectResponse("https://ratemyscu.bryan.cf")

    
@app.post("/getEvals")
async def select_evaluations(request: EvalRequest):
    try:
        query = request_query_builder(request)
        print(query)
        evals = select_query(connection, query)
        return { "status": "200", "result": evals }
    except Exception as e:
        return { "status": "500", "error": e }

def request_query_builder(request: EvalRequest):
    query = "SELECT * FROM evals WHERE "
    queryBuilder = []
    if request.id:
        queryBuilder.append("id='" + request.id + "'")
    if request.classname:
        queryBuilder.append("classname='" + request.classname + "'")
    if request.classcode:
        queryBuilder.append("classcode='" + request.classcode + "'")
    if request.quarter:
        queryBuilder.append("quarter='" + request.quarter + "'")
    if request.year:
        queryBuilder.append("year=" + str(request.year))
    if request.professor:
        queryBuilder.append("professor='" + request.professor + "'")
    if request.overall and request.overallSearch:
        if request.overallSearch == "greaterThan":
            queryBuilder.append("overall>=" + str(request.overall))
        elif request.overallSearch == "lessThan":
            queryBuilder.append("overall<=" + str(request.overall))
        elif request.overallSearch == "equals":
            queryBuilder.append("overall=" + str(request.overall))
    query += " AND ".join(queryBuilder) + ";"
    return query

# WIP
@app.get("/test")
async def test():
    test_upload_system(connection)
    return {"status": "200"}