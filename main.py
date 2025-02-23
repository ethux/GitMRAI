from fastapi import FastAPI
import logging
from src.api.Gitlab.router import router as gitlab_router

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s', handlers=[logging.StreamHandler()])

app = FastAPI()
app.include_router(gitlab_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)