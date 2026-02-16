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

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Robustly extract JSON from text, ignoring headers/footers/markdown.
        """
        try:
            # Try direct parse first
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try finding the JSON object boundaries
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
                
        return {}

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
        return self._extract_json(response)

    async def analyze_intent(self, content: str) -> Dict[str, str]:
        """
        Analyze natural language message and classify intent.

        Returns dict with 'intent' and 'content' keys.
        """
        prompt = f"""Analyze this message and determine what the user wants.

Message: "{content}"

Respond with JSON only:
{{"intent": "CALENDAR", "content": "the relevant extracted text"}}

Valid intents:
- CALENDAR: asking about schedule/events ("what's happening tomorrow?", "any events this week?")
- SCHEDULE: wanting to ADD an event ("soccer practice Tuesday 5pm", "dentist appointment Friday")
- LIST_ADD: adding items to shopping list ("we need milk and eggs", "add bread to the list")
- LIST_SHOW: asking to see the list ("what's on the list?", "show shopping list")
- REMINDER: setting a reminder ("remind me to call mom", "don't forget to pick up kids")
- RECALL: searching for information ("what's the WiFi password?", "when is grandma's birthday?")
- REMEMBER: storing a fact ("the WiFi password is ABC123", "grandma's birthday is March 15")
- SUMMARIZE: requesting chat summary ("what did I miss?", "summarize today")
- BRIEFING: requesting a briefing ("give me a briefing", "what's going on today?")
- CHAT: general conversation that doesn't match above
- NONE: unclear or irrelevant

"content" = the extracted relevant text.
- For LIST_ADD: return ONLY the items joined by commas (e.g., "milk, eggs, bread"). DO NOT include words like "added" or "item(s)".
- For SCHEDULE: return the event details (e.g., "Soccer 5pm").
- For REMINDER: return the task (e.g., "Call Mom 3pm").

Respond with JSON only, no explanation. No conversational text."""

        try:
            result = await self.generate(prompt, json_mode=True)
            parsed = self._extract_json(result)
            
            return {
                "intent": parsed.get("intent", "NONE").upper(),
                "content": parsed.get("content", content)
            }
        except Exception as e:
            logger.warning(f"Intent analysis failed: {e}")
            return {"intent": "NONE", "content": content}

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

    async def synthesise_cross_silo(self, query: str, context: str) -> str:
        """
        Synthesise cross-silo search results into an insightful, unified response.
        This is the 'Chief of Staff' intelligence that connects dots across data sources.
        """
        system_prompt = (
            "You are the family's Chief of Staff -- an AI that knows the family's chat history, "
            "calendar, saved facts, and photo library. When given search results from multiple sources, "
            "synthesise them into a brief, insightful response that connects the dots.\n\n"
            "Rules:\n"
            "- Be concise (3-5 sentences max)\n"
            "- Connect information across sources when possible\n"
            "- Highlight actionable insights (upcoming deadlines, patterns, suggestions)\n"
            "- Use a warm, helpful tone\n"
            "- If results are sparse, say what you found without over-interpreting\n"
            "- Never invent information not present in the data"
        )

        prompt = f"""The family asked: "{query}"

Here's what I found across their data:

{context}

Synthesise this into a brief, insightful response that connects the dots across these sources:"""

        return await self.generate(prompt, system_prompt=system_prompt)

    async def extract_calendar_event(self, content: str) -> Dict[str, Any]:
        """
        Extract event details from a natural language calendar request.

        Returns dict with keys: summary, date, time, duration, location
        """
        prompt = f"""Extract calendar event details from this request.
Request: "{content}"

Respond ONLY with valid JSON in this format:
{{
    "summary": "short event title",
    "date": "the date mentioned (e.g., 'Tuesday', 'tomorrow', 'March 15')",
    "time": "the time mentioned (e.g., '5pm', '14:00', 'noon')",
    "duration": "duration if mentioned (e.g., '1 hour', '30 minutes'), or null",
    "location": "location if mentioned, or null"
}}
"""
        response = await self.generate(prompt, json_mode=True)
        return self._extract_json(response)

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
