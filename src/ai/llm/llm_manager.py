"""LLM manager with actual API integration"""

import logging
import os
from typing import Optional, List, Dict, Any
import json
from src.config import settings

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

class LLMManager:
    """Manages interactions with various LLMs"""
    
    def __init__(self):
        """Initialize LLM manager with API clients"""
        self.current_model = "openai"  # Default to OpenAI
        self.openai_client = None
        self.claude_client = None
        self.gemini_model = None
        
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize all LLM API clients"""
        # OpenAI
        if settings.openai_api_key and AsyncOpenAI:
            try:
                self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("[LLM] OpenAI client initialized")
            except Exception as e:
                logger.warning(f"[LLM] Failed to initialize OpenAI: {e}")
        
        # Anthropic Claude
        if settings.anthropic_api_key and anthropic:
            try:
                self.claude_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
                logger.info("[LLM] Claude client initialized")
            except Exception as e:
                logger.warning(f"[LLM] Failed to initialize Claude: {e}")
        
        # Google Gemini
        if settings.google_api_key and genai:
            try:
                genai.configure(api_key=settings.google_api_key)
                self.gemini_model = genai.GenerativeModel(settings.gemini_model)
                logger.info("[LLM] Gemini client initialized")
            except Exception as e:
                logger.warning(f"[LLM] Failed to initialize Gemini: {e}")
    
    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        model: str = "openai"
    ) -> str:
        """Generate response from LLM"""
        logger.info(f"[LLM] Generating response with {model}")
        
        try:
            if model == "openai" and self.openai_client:
                return await self._openai_response(prompt, system_prompt, temperature)
            elif model == "claude" and self.claude_client:
                return await self._claude_response(prompt, system_prompt, temperature)
            elif model == "gemini" and self.gemini_model:
                return await self._gemini_response(prompt, system_prompt, temperature)
            else:
                logger.error(f"[LLM] Model {model} not available")
                return "죄송합니다. LLM을 사용할 수 없습니다."
        except Exception as e:
            logger.error(f"[LLM] Error generating response: {e}", exc_info=True)
            return f"오류 발생: {str(e)}"
    
    async def _openai_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Get response from OpenAI GPT-4"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"[LLM] OpenAI error: {e}")
            raise
    
    async def _claude_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Get response from Claude"""
        try:
            message = self.claude_client.messages.create(
                model=settings.claude_model,
                max_tokens=2000,
                system=system_prompt or "You are NOVA AI, a helpful Windows agent assistant.",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            
            return message.content[0].text
        except Exception as e:
            logger.error(f"[LLM] Claude error: {e}")
            raise
    
    async def _gemini_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Get response from Google Gemini"""
        try:
            full_prompt = f"{system_prompt or ''}\n\n{prompt}" if system_prompt else prompt
            response = self.gemini_model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2000
                )
            )
            
            return response.text
        except Exception as e:
            logger.error(f"[LLM] Gemini error: {e}")
            raise
    
    async def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user intent using LLM"""
        logger.info(f"[LLM] Analyzing intent: {user_input}")
        
        prompt = f"""
사용자의 입력을 분석하고 JSON 형식으로 응답하세요:
입력: {user_input}

JSON 형식 (한국어):
{{
    "intent": "사용자의 의도 (예: program_launch, file_search, web_search)",
    "action": "수행할 액션",
    "parameters": {{
        "key": "value"
    }},
    "confidence": 0.95,
    "requires_confirmation": false
}}
        """
        
        try:
            response = await self.generate_response(prompt)
            
            # Try to parse JSON response
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass
            
            # Fallback if JSON parsing fails
            return {
                "intent": "unknown",
                "action": user_input,
                "parameters": {},
                "confidence": 0.5,
                "requires_confirmation": True
            }
        except Exception as e:
            logger.error(f"[LLM] Intent analysis failed: {e}")
            return {
                "intent": "error",
                "action": user_input,
                "parameters": {},
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def plan_tasks(self, user_request: str) -> List[Dict[str, Any]]:
        """Plan tasks from user request using LLM"""
        logger.info(f"[LLM] Planning tasks: {user_request}")
        
        prompt = f"""
다음 사용자 요청을 구체적인 작업 단계로 분해하세요:
요청: {user_request}

JSON 배열 형식으로 응답 (각 항목은 다음 필드 포함):
[
    {{
        "step": 1,
        "task": "작업 이름",
        "tool": "사용할 도구 (browser, file, system, voice, screen, network)",
        "action": "구체적 액션",
        "parameters": {{
            "key": "value"
        }},
        "depends_on": [0],
        "description": "작업 설명"
    }}
]
        """
        
        try:
            response = await self.generate_response(prompt)
            
            # Try to parse JSON response
            try:
                json_start = response.find('[')
                json_end = response.rfind(']') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass
            
            # Fallback
            return [{"task": user_request, "tool": "system"}]
        except Exception as e:
            logger.error(f"[LLM] Task planning failed: {e}")
            return [{"task": user_request, "tool": "system", "error": str(e)}]
    
    async def generate_task_name(self, action: str) -> str:
        """Generate a descriptive name for a task"""
        logger.debug(f"[LLM] Generating task name for: {action}")
        
        try:
            response = await self.generate_response(
                f"이 액션을 한국어로 한 문장으로 간단하게 설명하세요 (10단어 이하): {action}",
                temperature=0.3
            )
            return response.strip()
        except Exception as e:
            logger.error(f"[LLM] Task naming failed: {e}")
            return action
