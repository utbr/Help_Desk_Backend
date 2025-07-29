from fastapi import FastAPI
from app.API.router import api_router as router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Backend")

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)