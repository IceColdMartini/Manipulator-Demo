"""
Test Azure OpenAI integration
"""
import pytest
from src.services.azure_openai import get_azure_openai_client, generate_completion

def test_azure_openai_client():
    """Test Azure OpenAI client initialization"""
    client = get_azure_openai_client()
    assert client is not None
    # Second call should return cached instance
    assert get_azure_openai_client() is client

@pytest.mark.asyncio
async def test_generate_completion():
    """Test completion generation"""
    prompt = "Hello, how are you?"
    response = await generate_completion(prompt, max_tokens=10)
    assert isinstance(response, str)
    assert len(response) > 0
