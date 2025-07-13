#!/usr/bin/env python3
"""
Simple test script to verify our configuration and models work
without requiring database connections
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_configuration():
    """Test if configuration loads correctly"""
    print("🔧 Testing configuration...")
    try:
        from app.core.config import settings
        print(f"✅ App Name: {settings.app_name}")
        print(f"✅ App Version: {settings.app_version}")
        print(f"✅ Debug Mode: {settings.debug}")
        print(f"✅ Configuration loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def test_models():
    """Test if Pydantic models work correctly"""
    print("\n📋 Testing Pydantic models...")
    try:
        from app.models.schemas import (
            ProductCreate, ProductAttributes, ConversationCreate, 
            ConversationBranch, MessageSender, ConversationMessage
        )
        from datetime import datetime
        
        # Test Product model
        product_attrs = ProductAttributes(
            price="$29.99",
            color="Blue",
            category="Electronics",
            brand="TestBrand"
        )
        
        product_create = ProductCreate(
            product_attributes=product_attrs,
            product_tag=["test", "electronics", "gadget"],
            product_description="Test product description"
        )
        print(f"✅ Product model: {product_create.product_attributes.brand}")
        
        # Test Conversation model
        conversation_create = ConversationCreate(
            customer_id="test_customer",
            business_id="test_business",
            product_context=["test_product_id"],
            conversation_branch=ConversationBranch.MANIPULATOR
        )
        print(f"✅ Conversation model: {conversation_create.conversation_branch}")
        
        # Test Message model
        message = ConversationMessage(
            timestamp=datetime.now(),
            sender=MessageSender.AGENT,
            content="Hello! How can I help you today?",
            intent="greeting"
        )
        print(f"✅ Message model: {message.sender}")
        
        print("✅ All Pydantic models work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Model testing failed: {e}")
        return False

def test_imports():
    """Test if all our modules can be imported"""
    print("\n📦 Testing module imports...")
    try:
        from app.models import schemas, database
        from app.core import config
        from app.services import product_service, conversation_service
        print("✅ All modules imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Import testing failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("🚀 Starting basic functionality tests...\n")
    
    tests = [
        test_configuration,
        test_models,
        test_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! The foundation is solid.")
        print("\n📋 Next steps:")
        print("   1. Set up PostgreSQL database")
        print("   2. Set up MongoDB")
        print("   3. Set up Redis")
        print("   4. Run the full database tests")
    else:
        print("💥 Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
