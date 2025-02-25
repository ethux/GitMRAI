from fastapi import Request, APIRouter, Depends, HTTPException, status
import logging
import json
import time
from src.config.settings import supersettings
from src.api.LLM.service import MistralLLM
from src.api.Gitlab.service import GitlabService

logger = logging.getLogger(__name__)

SECRET_TOKEN = supersettings.SECRET_TOKEN
if not SECRET_TOKEN:
    raise ValueError("SECRET_TOKEN must be set in the environment variables")

BASE_PATH = "/api/v1"
router = APIRouter(prefix=BASE_PATH)

async def get_request_body(request: Request) -> dict:
    """Fetch and parse the request body."""
    try:
        body = await request.body()
        return json.loads(body)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON body: {e}")
        raise HTTPException(status_code=422, detail="Invalid JSON body")

def log_request(request: Request, body: dict):
    """Log the incoming request details."""
    logger.debug(f"Request: Method={request.method}, URL={request.url}, Headers={request.headers}, Body={body}")

def verify_api_key(request: Request):
    api_key = request.headers.get("X-Gitlab-Token")
    logger.debug(f"Received API key: {api_key}")
    if api_key != SECRET_TOKEN:
        logger.error("Invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    logger.debug("API key validated successfully")

@router.post("/mr_summarize")
async def mr_summarize(request: Request, api_key: str = Depends(verify_api_key)):
    try:
        body_dict = await get_request_body(request)
        log_request(request, body_dict)
        project_id = body_dict["project"]["id"]
        merge_request_id = body_dict["object_attributes"]["iid"]
        gitlab_client = GitlabService(project_id, merge_request_id)
        diff = await gitlab_client.get_diffs()
        logger.debug(diff)
        mistral_client = MistralLLM(diff, system_prompt_file='system_prompt_summarize.json')
        summary = await mistral_client.llm_msg()
        await gitlab_client.post_comment(summary)
        return summary
    except KeyError as e:
        logger.error(f"Missing required field in request body: {e}")
        raise HTTPException(status_code=422, detail=f"Missing required field: {e}")
    except Exception as e:
        logger.error(f"Error summarizing merge request: {e}")
        return {"error": str(e)}

@router.post("/mr_description")
async def mr_description(request: Request, api_key: str = Depends(verify_api_key)):
    try:
        body_dict = await get_request_body(request)
        log_request(request, body_dict)
        project_id = body_dict["project"]["id"]
        merge_request_id = body_dict["object_attributes"]["iid"]
        gitlab_client = GitlabService(project_id, merge_request_id)
        diff = await gitlab_client.get_diffs()
        logger.debug(diff)
        mistral_client = MistralLLM(diff, system_prompt_file='system_prompt.json')
        summary = await mistral_client.llm_msg()
        await gitlab_client.update_description(summary)
        return summary
    except KeyError as e:
        logger.error(f"Missing required field in request body: {e}")
        raise HTTPException(status_code=422, detail=f"Missing required field: {e}")
    except Exception as e:
        logger.error(f"Error summarizing merge request: {e}")
        return {"error": str(e)}

@router.post("/mr_comment_on_diff")
async def mr_comment_on_diff(request: Request, api_key: str = Depends(verify_api_key)):
    try:
        body_dict = await get_request_body(request)
        log_request(request, body_dict)
        project_id = body_dict["project"]["id"]
        merge_request_id = body_dict["object_attributes"]["iid"]
        gitlab_client = GitlabService(project_id, merge_request_id)
        diff = await gitlab_client.get_diffs()
        logger.debug(diff)

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                mistral_client = MistralLLM(diff, system_prompt_file='system_prompt.json')
                comment_data_raw = await mistral_client.llm_struct()
                logger.debug(f"Raw comment_data: {comment_data_raw}")
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
            return {"error": f"Failed to decode comment_data: {e}"}

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

    except KeyError as e:
        logger.error(f"Missing required field in request body: {e}")
        raise HTTPException(status_code=422, detail=f"Missing required field: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"error": str(e)}