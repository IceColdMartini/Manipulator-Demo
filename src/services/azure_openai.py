"""
Azure OpenAI client configuration and utilities
"""
from typing import Optional
from openai import AsyncAzureOpenAI
from functools import lru_cache

from src.core.config import get_settings

settings = get_settings()

@lru_cache()
def get_azure_openai_client() -> AsyncAzureOpenAI:
    """
    Get Azure OpenAI client instance
    """
    return AsyncAzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
    )

async def generate_completion(
    prompt: str,
    *,
    max_tokens: int = 150,
    temperature: float = 0.7,
    deployment_name: Optional[str] = None,
) -> str:
    """
    Generate completion using Azure OpenAI
    """
    client = get_azure_openai_client()
    deployment = deployment_name or settings.AZURE_OPENAI_DEPLOYMENT_NAME
    
    response = await client.completions.create(
        model=deployment,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    
    return response.choices[0].text.strip()
