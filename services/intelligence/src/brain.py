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
        system_prompt = """You are a helpful family assistant. Summarize conversations concisely, 
focusing on: decisions made, action items, important information shared, and upcoming plans.
Keep summaries brief (2-4 sentences) and family-friendly."""

        prompt = f"""Summarize this family chat in 2-3 sentences.
Focus on: important events, decisions made, upcoming plans.

{context}

Summary:"""
        return await self.generate(prompt, system_prompt=system_prompt)

    async def summarize_recall_results(self, query: str, raw_results: str) -> str:
        """
        Summarize recall results when they're too long to display directly.
        Helps distill relevant information from mixed facts + chat history.
        """
        system_prompt = """You are a helpful family assistant with access to family memories and chat history.
When asked to summarize search results, extract the most relevant information that answers the query.
Be concise and direct. If there are contradictions, note the most recent information."""

        prompt = f"""The user asked about: "{query}"

Here's what I found in saved facts and chat history:

{raw_results}

Provide a brief, helpful summary (2-4 sentences) answering what the user wanted to know about "{query}":"""

        return await self.generate(prompt, system_prompt=system_prompt)

    async def is_model_available(self) -> bool:
        """
        Check if the configured model is available in Ollama.
        """
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [m.get('name', '') for m in data.get('models', [])]
                    # Check for exact match or match without tag
                    model_base = self.model.split(':')[0]
                    return any(self.model in m or model_base in m for m in models)
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
        return False

    async def pull_model_if_needed(self) -> bool:
        """
        Pull the model if it's not already available.
        Returns True if model is ready, False otherwise.
        """
        if await self.is_model_available():
            logger.info(f"Model {self.model} is available")
            return True

        logger.info(f"Pulling model {self.model}...")
        try:
            async with httpx.AsyncClient(timeout=300) as client:  # 5 min timeout for pull
                response = await client.post(
                    f"{self.ollama_url}/api/pull",
                    json={"name": self.model, "stream": False}
                )
                if response.status_code == 200:
                    logger.info(f"Successfully pulled model {self.model}")
                    return True
                else:
                    logger.error(f"Failed to pull model: {response.text}")
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
        return False
