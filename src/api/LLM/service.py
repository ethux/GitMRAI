from mistralai import Mistral
from src.config.settings import supersettings
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s', handlers=[logging.StreamHandler()])

class MistralLLM:
    def __init__(self, diffs):
        self.api_key = supersettings.API_KEY
        self.model = supersettings.MODEL
        self.diffs = diffs
        self.client = Mistral(api_key=self.api_key)

    async def summarize(self):
        try:
            with open('system_prompt_summarize.json', 'r') as file:
                json_file = json.load(file)
                system_prompt = json_file['system_note']
                messages = [
                    {"role": "system", "content": f"{system_prompt}"},
                    {"role": "user", "content": f"{self.diffs}"}
                ]
                response = await self.client.chat.complete_async(
                    model=self.model,
                    messages=messages,
                    temperature=0.3
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {"error": str(e)}
    
    async def llm_comment_on_diff(self):
        try:
            with open('system_prompt.json', 'r') as file:
                json_file = json.load(file)
                system_prompt = json_file['system_note']
                messages = [
                    {"role": "system", "content": f"{system_prompt}"},
                    {"role": "user", "content": f"{self.diffs}"}
                ]
                response = await self.client.chat.complete_async(
                    model=self.model,
                    messages=messages,
                    temperature=0.25,
                    response_format={
                        "type": "json_object",
                    }
                )
                logger.info(f"Response: {response}")
                comment = response.choices[0].message.content
                logger.info(f"Response content: {comment}")
                return comment
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {"error": str(e)}