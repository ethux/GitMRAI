from fastapi import FastAPI
from fastapi import FastAPI
from src.api.Gitlab.router import router as gitlab_router

app = FastAPI()
app.include_router(gitlab_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)