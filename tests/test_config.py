"""
Test configuration and settings
"""
import pytest
from src.core.config import Settings, get_settings

def test_settings():
    """Test settings configuration"""
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.APP_NAME == "ManipulatorAI"
    assert settings.API_VERSION == "v1"
    assert settings.DEBUG is True
