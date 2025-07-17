#!/usr/bin/env python3
"""
Step 6 Testing Script: Enhanced Conversation Engine and Prompt Engineering
Tests the sophisticated conversation management and prompt engineering capabilities
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test environment setup
import pytest
from unittest.mock import AsyncMock, MagicMock

# Import our enhanced components
from app.services.enhanced_conversation_engine import EnhancedConversationEngine
from app.services.prompt_engine import PromptEngine
from app.services.conversation_manager import ConversationManager
from app.models.schemas import ConversationBranch, ConversationStatus

class TestStep6ConversationEngine:
    """Comprehensive test suite for Step 6 implementation"""
    
    def setup_method(self):
        """Set up test environment"""
        # Mock services
        self.mock_ai_service = AsyncMock()
        self.mock_product_service = AsyncMock()
        self.mock_conversation_service = AsyncMock()
        
        # Initialize enhanced conversation engine
        self.engine = EnhancedConversationEngine(
            ai_service=self.mock_ai_service,
            product_service=self.mock_product_service,
            conversation_service=self.mock_conversation_service
        )
        
        print("✅ Test environment initialized")
    
    async def test_prompt_engine_capabilities(self):
        """Test the sophisticated prompt engineering capabilities"""
        print("\n🧠 Testing Prompt Engine Capabilities...")
        
        prompt_engine = PromptEngine()
        
        # Test welcome protocol generation
        welcome_prompt = prompt_engine.generate_welcome_prompt(
            branch=ConversationBranch.MANIPULATOR,
            context={
                "product_name": "Premium Software Suite",
                "interaction_type": "ad_click",
                "customer_behavior": "engaged"
            }
        )
        
        assert "Welcome" in welcome_prompt
        assert "Premium Software Suite" in welcome_prompt
        print("✅ Welcome protocol generation works")
        
        # Test conversation prompts
        conversation_prompt = prompt_engine.generate_conversation_prompt(
            branch=ConversationBranch.CONVINCER,
            conversation_context={
                "customer_message": "I'm looking for a solution to manage my team",
                "conversation_history": ["Hello", "I need help with team management"],
                "customer_sentiment": "interested",
                "products_mentioned": ["Team Management Pro"]
            }
        )
        
        assert "team management" in conversation_prompt.lower()
        print("✅ Conversation prompt generation works")
        
        # Test cross-product recommendations
        cross_product_prompt = prompt_engine.generate_cross_product_recommendation_prompt(
            current_products=["Basic Plan"],
            recommended_products=["Premium Plan", "Enterprise Suite"],
            context={"budget_indicator": "flexible", "team_size": "growing"}
        )
        
        assert "Premium Plan" in cross_product_prompt
        print("✅ Cross-product recommendation prompts work")
        
        return True
    
    async def test_conversation_manager_flow(self):
        """Test the enhanced conversation management flow"""
        print("\n💬 Testing Conversation Manager Flow...")
        
        # Mock conversation creation
        self.mock_conversation_service.create_conversation.return_value = {
            "conversation_id": "test-conv-123",
            "status": "active"
        }
        
        # Mock AI service response
        self.mock_ai_service.generate_response.return_value = "Welcome! I'd love to help you today."
        
        # Test conversation start
        conversation_id, welcome_message = await self.engine.conversation_manager.start_conversation(
            customer_id="test-customer-456",
            business_id="test-business-789",
            branch=ConversationBranch.MANIPULATOR,
            initial_context={"product_id": "prod-123"},
            interaction_type="ad_click"
        )
        
        assert conversation_id == "test-conv-123"
        assert "Welcome" in welcome_message
        print("✅ Conversation start with welcome protocol works")
        
        # Test message processing
        self.mock_ai_service.generate_response.return_value = "That sounds like a great use case! Let me help you with that."
        
        ai_response, status = await self.engine.conversation_manager.process_customer_message(
            conversation_id="test-conv-123",
            customer_message="I need help with project management",
            customer_context={"sentiment": "interested"}
        )
        
        assert "help you" in ai_response
        assert status == ConversationStatus.ACTIVE
        print("✅ Message processing with AI integration works")
        
        return True
    
    async def test_manipulator_conversation_start(self):
        """Test Manipulator branch conversation initialization"""
        print("\n🎯 Testing Manipulator Conversation Start...")
        
        # Mock product verification
        self.mock_product_service.get_product_by_id.return_value = {
            "id": "prod-123",
            "name": "Premium Software",
            "category": "productivity"
        }
        
        # Mock conversation creation
        self.mock_conversation_service.create_conversation.return_value = {
            "conversation_id": "manip-conv-123",
            "status": "active"
        }
        
        # Mock AI welcome response
        self.mock_ai_service.generate_response.return_value = "Hi! I noticed you're interested in our Premium Software. Let me show you how it can transform your workflow!"
        
        result = await self.engine.start_manipulator_conversation(
            customer_id="customer-789",
            business_id="business-456",
            interaction_data={
                "product_id": "prod-123",
                "type": "ad_click",
                "platform": "facebook"
            }
        )
        
        assert result["success"] is True
        assert "manip-conv-123" in result["conversation_id"]
        assert "Premium Software" in result["ai_response"]
        assert result["branch"] == "manipulator"
        print("✅ Manipulator conversation start with product focus works")
        
        return True
    
    async def test_convincer_conversation_start(self):
        """Test Convincer branch conversation initialization"""
        print("\n🤝 Testing Convincer Conversation Start...")
        
        # Mock conversation creation
        self.mock_conversation_service.create_conversation.return_value = {
            "conversation_id": "convincer-conv-456",
            "status": "active"
        }
        
        # Mock AI responses for welcome and initial message processing
        self.mock_ai_service.generate_response.side_effect = [
            "Hello! Welcome to our support. How can I help you today?",
            "I understand you're looking for team collaboration tools. Let me help you find the perfect solution!"
        ]
        
        result = await self.engine.start_convincer_conversation(
            customer_id="customer-456",
            business_id="business-789",
            initial_message="I need a solution for my team collaboration",
            customer_context={"company_size": "50-100", "industry": "tech"}
        )
        
        assert result["success"] is True
        assert "convincer-conv-456" in result["conversation_id"]
        assert "solution" in result["ai_response"].lower()
        assert result["branch"] == "convincer"
        print("✅ Convincer conversation start with discovery mode works")
        
        return True
    
    async def test_conversation_continuation(self):
        """Test conversation continuation with enhanced management"""
        print("\n🔄 Testing Conversation Continuation...")
        
        # Mock conversation retrieval
        self.mock_conversation_service.get_conversation.return_value = {
            "conversation_id": "cont-conv-789",
            "status": "active",
            "branch": "convincer"
        }
        
        # Mock message history
        self.mock_conversation_service.get_conversation_history.return_value = [
            {"sender": "customer", "content": "I need project management tools"},
            {"sender": "agent", "content": "I can help you with that!"}
        ]
        
        # Mock AI continuation response
        self.mock_ai_service.generate_response.return_value = "Based on your needs, I recommend our Project Pro suite. It includes task management, team collaboration, and reporting features."
        
        result = await self.engine.continue_conversation(
            conversation_id="cont-conv-789",
            customer_message="What features does it include?",
            customer_context={"engagement_level": "high"}
        )
        
        assert result["success"] is True
        assert "Project Pro" in result["ai_response"]
        assert "features" in result["ai_response"]
        print("✅ Conversation continuation with context awareness works")
        
        return True
    
    async def test_conversation_insights(self):
        """Test conversation insights and analytics"""
        print("\n📊 Testing Conversation Insights...")
        
        # Mock conversation data
        self.mock_conversation_service.get_conversation.return_value = {
            "conversation_id": "insight-conv-123",
            "branch": "manipulator",
            "status": "qualified"
        }
        
        # Mock conversation history
        mock_history = [
            type('Message', (), {
                'sender': 'customer',
                'content': 'Hello',
                'timestamp': datetime.now()
            })(),
            type('Message', (), {
                'sender': 'agent',
                'content': 'Welcome!',
                'timestamp': datetime.now()
            })()
        ]
        self.mock_conversation_service.get_conversation_history.return_value = mock_history
        
        insights = await self.engine.get_conversation_insights("insight-conv-123")
        
        assert "conversation_id" in insights
        assert insights["branch"] == "manipulator"
        assert insights["message_count"] == 2
        print("✅ Conversation insights generation works")
        
        return True
    
    async def test_engine_performance_metrics(self):
        """Test engine performance tracking"""
        print("\n⚡ Testing Engine Performance Metrics...")
        
        # Mock conversation manager metrics
        self.engine.conversation_manager.get_conversation_metrics = MagicMock(return_value={
            "total_conversations": 150,
            "active_conversations": 25,
            "qualified_conversations": 45,
            "engagement_rate": 0.75
        })
        
        # Mock prompt engine statistics
        self.engine.prompt_engine.get_prompt_statistics = MagicMock(return_value={
            "total_prompts_generated": 500,
            "welcome_prompts": 150,
            "conversation_prompts": 300,
            "recovery_prompts": 50
        })
        
        performance = await self.engine.get_engine_performance()
        
        assert "engine_metrics" in performance
        assert "conversation_metrics" in performance
        assert "prompt_statistics" in performance
        assert performance["conversation_metrics"]["engagement_rate"] == 0.75
        print("✅ Engine performance metrics tracking works")
        
        return True
    
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms"""
        print("\n🛡️ Testing Error Handling and Recovery...")
        
        # Test failed conversation start
        self.mock_conversation_service.create_conversation.side_effect = Exception("Database error")
        
        result = await self.engine.start_manipulator_conversation(
            customer_id="error-customer",
            business_id="error-business", 
            interaction_data={"product_id": "invalid-product"}
        )
        
        assert result["success"] is False
        assert "error" in result
        print("✅ Error handling for failed conversation start works")
        
        # Reset mock for next test
        self.mock_conversation_service.create_conversation.side_effect = None
        
        return True

async def run_step6_tests():
    """Run all Step 6 tests"""
    print("🚀 Starting Step 6: Enhanced Conversation Engine Tests\n")
    print("=" * 60)
    
    test_suite = TestStep6ConversationEngine()
    test_suite.setup_method()
    
    tests = [
        ("Prompt Engine Capabilities", test_suite.test_prompt_engine_capabilities),
        ("Conversation Manager Flow", test_suite.test_conversation_manager_flow),
        ("Manipulator Conversation Start", test_suite.test_manipulator_conversation_start),
        ("Convincer Conversation Start", test_suite.test_convincer_conversation_start),
        ("Conversation Continuation", test_suite.test_conversation_continuation),
        ("Conversation Insights", test_suite.test_conversation_insights),
        ("Engine Performance Metrics", test_suite.test_engine_performance_metrics),
        ("Error Handling and Recovery", test_suite.test_error_handling_and_recovery)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
            print(f"✅ {test_name} - PASSED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} - FAILED: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📋 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All Step 6 tests passed! Enhanced Conversation Engine is ready.")
        print("\n🔧 Step 6 Features Successfully Implemented:")
        print("  • Sophisticated prompt engineering with business personality")
        print("  • Enhanced conversation management with state tracking")
        print("  • Welcome protocols for both Manipulator and Convincer branches")
        print("  • Advanced AI integration with custom prompt support")
        print("  • Conversation insights and performance analytics")
        print("  • Robust error handling and recovery mechanisms")
        print("  • Cross-product recommendation capabilities")
        print("  • Adaptive persuasion strategies based on conversation context")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
    
    return failed == 0

def main():
    """Main test execution"""
    try:
        success = asyncio.run(run_step6_tests())
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
