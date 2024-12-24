# standard library imports
import torch
import logging, json
from dataclasses import dataclass
from typing import Dict, Any

# third party imports
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
from json_repair import repair_json

# local imports
from utils.logging_config import configure_logging
from configs.config import LLM_CONFIG


configure_logging()
logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration class for LLM settings"""

    base_url: str
    api_key: str
    temperature: float = 0.1

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create configuration from environment variables"""
        return cls(
            base_url=LLM_CONFIG["BASE_URL"],
            api_key=LLM_CONFIG["API_KEY"],
            temperature=LLM_CONFIG["TEMPERATURE"],
        )


class GPUManager:
    """Manages GPU-related operations"""

    @staticmethod
    def setup_gpu() -> bool:
        """Setup GPU and clear cache if available"""
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("GPU setup successful")
                return True
            logger.warning("GPU not available")
            return False
        except Exception as e:
            logger.warning(f"GPU setup failed: {e}")
            return False


class LLMClient:
    """Client for LLM operations"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = OpenAI(base_url=config.base_url, api_key=config.api_key)
        GPUManager.setup_gpu()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def get_completion(
        self, model_name: str, prompt_text: str, user_prompt: str, content: str
    ) -> str:
        """Get completion from LLM"""
        try:
            completion = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": prompt_text},
                    {"role": "user", "content": user_prompt + content},
                ],
                temperature=self.config.temperature,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in LLM completion: {e}")
            raise


class BaseParser:
    """Base class for all parser implementations"""

    def __init__(self):
        self.config = LLMConfig.from_env()
        self.llm_client = LLMClient(self.config)

    def _process_json_response(self, text: str) -> Dict[str, Any]:
        """Process JSON response from LLM"""

        # Remove markdown code blocks if present
        cleaned_text = text.strip()
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text.strip("```json").strip("```")

        cleaned_text = repair_json(cleaned_text)

        try:
            # Try parsing as JSON first
            if "{" in cleaned_text and "}" in cleaned_text:
                # Extract JSON portion if mixed with other text
                start = cleaned_text.find("{")
                end = cleaned_text.rfind("}") + 1
                json_str = cleaned_text[start:end]
                data = json.loads(json_str)
                return data if isinstance(data, dict) else {}
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {"message": "Resume Parsing Failed (F:PJR)"}
