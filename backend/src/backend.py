from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/api/v0")
async def root():
    return health_check()


@app.get("/api/{api_path:path}")
async def invalid_endpoint():
    raise HTTPException(status_code=404, detail="Invalid API Endpoint")


@app.get("/check")
async def health_check():
    raise {"status": "OK", "version": "dev"}


@app.get("{full_path:path}")
async def not_api_call():
    return RedirectResponse("https://ratemyscu.bryan.cf")
