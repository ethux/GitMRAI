from fastapi import Request, APIRouter, HTTPException, status, Depends
from supabase import Client
import logging
import json
import time
from src.config.settings import supersettings
from src.api.LLM.service import MistralLLM
from src.api.Gitlab.service import GitlabService
from src.api.auth.db.database import get_db
from src.api.auth.db.models import User
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s', handlers=[logging.StreamHandler()])

SECRET_TOKEN = supersettings.SECRET_TOKEN
if not SECRET_TOKEN:
    raise ValueError("SECRET_TOKEN must be set in the environment variables")

BASE_PATH = "/api/v1"
router = APIRouter(prefix=BASE_PATH)
templates = Jinja2Templates(directory="src/templates")

async def get_current_user(request: Request, db: Client = Depends(get_db)):
    token = request.headers.get('X-Gitlab-Token')
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No token provided")
    user = db.table('users').select("*").eq("api_key", token).execute()
    user = user.data[0] if user.data else None
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    logger.info(f"User: {user}")
    return user

async def get_request_body(request: Request) -> dict:
    """Fetch and parse the request body."""
    body = await request.body()
    return json.loads(body)

def log_request(request: Request, body: dict):
    """Log the incoming request details."""
    logger.info(f"Request: Method={request.method}, URL={request.url}, Headers={request.headers}, Body={body}")

@router.post("/mr_summarize")
async def mr_summarize(request: Request, current_user: User = Depends(get_current_user)):
    try:
        body_dict = await get_request_body(request)
        log_request(request, body_dict)
        project_id = body_dict["project"]["id"]
        merge_request_id = body_dict["object_attributes"]["iid"]
        gitlab_client = GitlabService(project_id, merge_request_id)
        diff = await gitlab_client.get_diffs()
        logger.info(diff)
        mistral_client = MistralLLM(diff)
        summary = await mistral_client.summarize()
        await gitlab_client.post_comment(summary)
        return summary
    except Exception as e:
        logger.error(f"Error summarizing merge request: {e}")
        return {"error": str(e)}

@router.post("/mr_comment_on_diff")
async def mr_comment_on_diff(request: Request, current_user: User = Depends(get_current_user)):
    try:
        body_dict = await get_request_body(request)
        log_request(request, body_dict)
        project_id = body_dict["project"]["id"]
        merge_request_id = body_dict["object_attributes"]["iid"]
        gitlab_client = GitlabService(project_id, merge_request_id)
        diff = await gitlab_client.get_diffs()
        logger.info(diff)

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                mistral_client = MistralLLM(diff)
                comment_data_raw = await mistral_client.llm_comment_on_diff()
                logger.info(f"Raw comment_data: {comment_data_raw}")
                break
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} to get comment data failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Failed to get comment data.")
                    return {"error": str(e)}

        try:
            comment_data = json.loads(comment_data_raw)
        except json.JSONDecodeError as e:
            return {"error": "Failed to decode comment_data"}

        comments = comment_data.get('comments', [])
        for comment in comments:
            if "error" in comment:
                return {"error": comment['error']}
            body = comment.get('body', '')
            position = comment.get('position', {})
            if not isinstance(position, dict):
                return {"error": "position is not a dictionary"}

            diff_id = diff["iid"]
            await gitlab_client.post_comment_on_diff(diff_id, body, position)

        return {"message": "Comments posted successfully"}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"error": str(e)}

@router.get("/mr_summarize", response_class=HTMLResponse)
async def get_mr_summarize(request: Request):
    return templates.TemplateResponse("mr_summarize.html", {"request": request})

@router.get("/mr_comment_on_diff", response_class=HTMLResponse)
async def get_mr_comment_on_diff(request: Request):
    return templates.TemplateResponse("mr_comment_on_diff.html", {"request": request})