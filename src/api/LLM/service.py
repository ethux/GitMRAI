from mistralai import Mistral
from src.config.settings import supersettings
import json
import logging

logger = logging.getLogger(__name__)

class MistralLLM:
    def __init__(self, diffs, system_prompt_file):
        self.api_key = supersettings.API_KEY
        self.model = supersettings.MODEL
        self.temperature = supersettings.TEMPERATURE
        self.client = Mistral(api_key=self.api_key)
        self.diffs = diffs
        self.system_prompt_file = system_prompt_file

    async def llm_msg(self):
        try:
            with open(self.system_prompt_file, 'r') as file:
                json_file = json.load(file)
                system_prompt = json_file['system_prompt']
                messages = [
                    {"role": "system", "content": f"{system_prompt}"},
                    {"role": "user", "content": f"{self.diffs}"}
                ]                
                response = await self.client.chat.complete_async(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature
                )
                logger.debug(f"Response content: {response.choices[0].message.content}")
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {"error": str(e)}
    
    async def llm_struct(self):
        try:
            with open(self.system_prompt_file, 'r') as file:
                json_file = json.load(file)
                system_prompt = json_file['system_prompt']
                messages = [
                    {"role": "system", "content": f"{system_prompt}"},
                    {"role": "user", "content": f"{self.diffs}"}
                ]
                response = await self.client.chat.complete_async(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    response_format={
                        "type": "json_object",
                    }
                )
                logger.debug(f"Response content: {response.choices[0].message.content}")
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {"error": str(e)}