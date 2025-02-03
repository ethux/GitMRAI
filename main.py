from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.api.Gitlab.router import router as gitlab_router
from src.api.auth.users.router import router as users_router

app = FastAPI()

templates = Jinja2Templates(directory="src/templates")

app.include_router(gitlab_router)
app.include_router(users_router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)