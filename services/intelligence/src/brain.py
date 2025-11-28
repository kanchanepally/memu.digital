import logging
import json
import httpx
from typing import Dict, Optional, Any
from config import Config

logger = logging.getLogger("memu.brain")

class Brain:
    def __init__(self):
        self.ollama_url = Config.OLLAMA_HOST
        self.model = Config.OLLAMA_MODEL
        self.enabled = Config.AI_ENABLED
        self.timeout = Config.AI_TIMEOUT

    async def generate(self, prompt: str, system_prompt: str = None, json_mode: bool = False) -> str:
        """
        Generic generation method for Ollama.
        """
        if not self.enabled:
            return ""

        payload = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {'temperature': 0.7}
        }

        if system_prompt:
            payload['system'] = system_prompt

        # Some Ollama versions support 'format': 'json'
        if json_mode:
             payload['format'] = 'json'

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get('response', '').strip()
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return ""

    async def extract_reminder(self, content: str) -> Dict[str, Any]:
        """
        Extract task and time from a reminder string using AI.
        """
        prompt = f"""Extract the task and the time from this reminder request.
Request: "{content}"
Respond ONLY with valid JSON in this format:
{{
    "task": "what to do",
    "time": "when to do it"
}}
"""
        response = await self.generate(prompt, json_mode=True)
        try:
            # Clean up potential markdown
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response for reminder")
            return {}

    async def analyze_intent(self, content: str) -> str:
        """
        Determine if the message contains an implicit command.
        """
        prompt = f"""Analyze this message and determine if it contains an implicit command.
Message: "{content}"
Respond with ONLY one word: CALENDAR, LIST, REMINDER, or NONE
"""
        return await self.generate(prompt)

    async def summarize_chat(self, context: str) -> str:
        """
        Summarize the provided chat context.
        """
        prompt = f"""Summarize today's family/class activity in 2-3 sentences.
Focus on: important events, decisions made, upcoming plans.

{context}

Summary:"""
        return await self.generate(prompt)
