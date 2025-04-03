from mistralai import Mistral
from src.config.settings import supersettings
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MistralLLM:
    def __init__(self, diffs: Dict[str, Any], system_prompt_file: str):
        """
        Initialize the MistralLLM with diffs and system prompt file.

        Args:
            diffs (Dict[str, Any]): The diffs to be processed.
            system_prompt_file (str): The path to the system prompt file.
        """
        self.api_key = supersettings.API_KEY
        self.model = supersettings.MODEL
        self.temperature = supersettings.TEMPERATURE
        self.client = Mistral(api_key=self.api_key)
        self.diffs = diffs
        self.system_prompt_file = system_prompt_file

    async def llm_msg(self) -> str:
        """
        Generate a message using the LLM.

        Returns:
            str: The generated message.

        Raises:
            Exception: If an error occurs while generating the message.
        """
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
        except FileNotFoundError:
            logger.error(f"System prompt file not found: {self.system_prompt_file}")
            return {"error": "System prompt file not found"}
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from system prompt file: {self.system_prompt_file}")
            return {"error": "Failed to decode JSON from system prompt file"}
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {"error": str(e)}

    async def llm_struct(self) -> str:
        """
        Generate a structured response using the LLM.

        Returns:
            str: The generated structured response.

        Raises:
            Exception: If an error occurs while generating the structured response.
        """
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
        except FileNotFoundError:
            logger.error(f"System prompt file not found: {self.system_prompt_file}")
            return {"error": "System prompt file not found"}
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from system prompt file: {self.system_prompt_file}")
            return {"error": "Failed to decode JSON from system prompt file"}
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {"error": str(e)}