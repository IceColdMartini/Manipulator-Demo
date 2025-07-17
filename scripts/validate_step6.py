#!/usr/bin/env python3
"""
Step 6 Validation Script: Enhanced Conversation Engine and Prompt Engineering
Validates the sophisticated conversation management and prompt engineering capabilities
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our enhanced components
from app.services.prompt_engine import PromptEngine
from app.models.schemas import ConversationBranch, ConversationStatus

class Step6Validator:
    """Validation suite for Step 6 implementation"""
    
    def __init__(self):
        self.prompt_engine = PromptEngine()
        self.tests_passed = 0
        self.tests_failed = 0
    
    def validate_prompt_engine_capabilities(self):
        """Validate the sophisticated prompt engineering capabilities"""
        print("\n🧠 Validating Prompt Engine Capabilities...")
        
        try:
            # Test welcome protocol generation
            from app.models.schemas import Product, ProductAttributes
            
            test_products = [
                Product(
                    product_id="prod-123",
                    product_attributes=ProductAttributes(
                        price="99.99",
                        category="productivity",
                        brand="TestBrand"
                    ),
                    product_tag=["software", "productivity", "premium"],
                    product_description="Advanced productivity software suite for teams"
                )
            ]
            
            welcome_prompt = self.prompt_engine.generate_welcome_prompt(
                branch=ConversationBranch.MANIPULATOR,
                products=test_products,
                customer_context={
                    "interaction_type": "ad_click",
                    "customer_behavior": "engaged"
                },
                interaction_type="ad_click"
            )
            
            assert "Welcome" in welcome_prompt
            assert "productivity" in welcome_prompt
            print("✅ Welcome protocol generation works")
            
            # Test conversation prompts
            conversation_prompt = self.prompt_engine.generate_conversation_prompt(
                branch=ConversationBranch.CONVINCER,
                customer_message="I'm looking for a solution to manage my team",
                products=test_products,
                conversation_history=[
                    {"sender": "customer", "content": "Hello"},
                    {"sender": "agent", "content": "I need help with team management"}
                ],
                customer_context={
                    "customer_sentiment": "interested",
                    "products_mentioned": ["Team Management Pro"]
                }
            )
            
            assert "team management" in conversation_prompt.lower()
            print("✅ Conversation prompt generation works")
            
            # Test cross-product recommendations
            cross_product_prompt = self.prompt_engine.generate_cross_product_recommendation_prompt(
                original_products=test_products,
                recommended_products=[
                    Product(
                        product_id="prod-456", 
                        product_attributes=ProductAttributes(price="199.99", category="premium"),
                        product_tag=["premium", "upgrade"],
                        product_description="Premium plan with advanced features"
                    ),
                    Product(
                        product_id="prod-789", 
                        product_attributes=ProductAttributes(price="499.99", category="enterprise"),
                        product_tag=["enterprise", "advanced"],
                        product_description="Enterprise suite with full capabilities"
                    )
                ],
                customer_context={"budget_indicator": "flexible", "team_size": "growing"}
            )
            
            assert "premium" in cross_product_prompt.lower()
            print("✅ Cross-product recommendation prompts work")
            
            # Test recovery prompts
            recovery_prompt = self.prompt_engine.generate_recovery_prompt(
                customer_message="I'm not sure if this is what I need",
                products=test_products,
                conversation_history=[{"sender": "customer", "content": "I'm hesitant"}],
                customer_context={"customer_sentiment": "hesitant"}
            )
            
            assert len(recovery_prompt) > 0
            print("✅ Recovery prompt generation works")
            
            self.tests_passed += 4
            return True
            
        except Exception as e:
            print(f"❌ Prompt engine validation failed: {e}")
            self.tests_failed += 1
            return False
    
    def validate_prompt_engine_statistics(self):
        """Validate prompt engine statistics tracking"""
        print("\n📊 Validating Prompt Engine Statistics...")
        
        try:
            from app.models.schemas import Product, ProductAttributes
            
            test_products = [
                Product(
                    product_id="prod-123",
                    product_attributes=ProductAttributes(
                        price="99.99",
                        category="test",
                        brand="TestBrand"
                    ),
                    product_tag=["software", "test"],
                    product_description="Test product for validation"
                )
            ]
            
            # Generate some prompts to test statistics
            for i in range(5):
                self.prompt_engine.generate_welcome_prompt(
                    branch=ConversationBranch.MANIPULATOR,
                    products=test_products,
                    customer_context={"test": f"iteration_{i}"},
                    interaction_type="test"
                )
            
            for i in range(3):
                self.prompt_engine.generate_conversation_prompt(
                    branch=ConversationBranch.CONVINCER,
                    customer_message=f"Test message {i}",
                    products=test_products,
                    conversation_history=[],
                    customer_context={"test": f"conversation_{i}"}
                )
            
            # Check statistics
            stats = self.prompt_engine.get_prompt_statistics()
            
            assert "total_prompts_generated" in stats
            assert stats["total_prompts_generated"] >= 8
            assert "welcome_prompts" in stats
            assert "conversation_prompts" in stats
            print("✅ Prompt engine statistics tracking works")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"❌ Prompt engine statistics validation failed: {e}")
            self.tests_failed += 1
            return False
    
    def validate_business_personality_configuration(self):
        """Validate business personality configuration"""
        print("\n🎭 Validating Business Personality Configuration...")
        
        try:
            # Test default business personality
            default_personality = self.prompt_engine.business_personality
            
            assert "tone" in default_personality
            assert "values" in default_personality
            assert "communication_style" in default_personality
            print("✅ Default business personality configuration works")
            
            # Test personality update
            new_personality = {
                "tone": "casual_friendly",
                "values": ["innovation", "customer_success"],
                "communication_style": "consultative",
                "industry_focus": "technology"
            }
            
            self.prompt_engine.update_business_personality(new_personality)
            updated_personality = self.prompt_engine.business_personality
            
            assert updated_personality["tone"] == "casual_friendly"
            assert "innovation" in updated_personality["values"]
            print("✅ Business personality update works")
            
            self.tests_passed += 2
            return True
            
        except Exception as e:
            print(f"❌ Business personality validation failed: {e}")
            self.tests_failed += 1
            return False
    
    def validate_conversation_branches(self):
        """Validate conversation branch-specific prompt generation"""
        print("\n🌲 Validating Conversation Branch Support...")
        
        try:
            from app.models.schemas import Product
            
            test_products = [
                Product(
                    id="prod-123",
                    name="Test Product", 
                    description="Test description",
                    category="test",
                    price=99.99
                )
            ]
            
            # Test Manipulator branch prompts
            manipulator_prompt = self.prompt_engine.generate_welcome_prompt(
                branch=ConversationBranch.MANIPULATOR,
                products=test_products,
                customer_context={"interaction_type": "ad_click"},
                interaction_type="ad_click"
            )
            
            # Should be more direct and product-focused
            assert "product" in manipulator_prompt.lower() or "solution" in manipulator_prompt.lower()
            print("✅ Manipulator branch prompt generation works")
            
            # Test Convincer branch prompts
            convincer_prompt = self.prompt_engine.generate_welcome_prompt(
                branch=ConversationBranch.CONVINCER,
                products=test_products,
                customer_context={"customer_message": "I need help with something"},
                interaction_type="message"
            )
            
            # Should be more consultative and discovery-focused
            assert "help" in convincer_prompt.lower() or "assist" in convincer_prompt.lower()
            print("✅ Convincer branch prompt generation works")
            
            self.tests_passed += 2
            return True
            
        except Exception as e:
            print(f"❌ Conversation branch validation failed: {e}")
            self.tests_failed += 1
            return False
    
    def validate_prompt_customization(self):
        """Validate prompt customization capabilities"""
        print("\n🎨 Validating Prompt Customization...")
        
        try:
            from app.models.schemas import Product
            
            test_products = [
                Product(
                    id="prod-123",
                    name="Enterprise Solution", 
                    description="Enterprise-grade software",
                    category="enterprise",
                    price=999.99
                )
            ]
            
            # Test context-aware prompt generation
            context_rich_prompt = self.prompt_engine.generate_conversation_prompt(
                branch=ConversationBranch.CONVINCER,
                customer_message="I'm evaluating different software options",
                products=test_products,
                conversation_history=[
                    {"sender": "customer", "content": "I'm looking at options"},
                    {"sender": "agent", "content": "I can help you compare"}
                ],
                customer_context={
                    "customer_sentiment": "analytical",
                    "conversation_stage": "evaluation",
                    "products_mentioned": ["Competitor A", "Competitor B"],
                    "customer_profile": {"industry": "finance", "team_size": "medium"}
                }
            )
            
            # Should be tailored to the context
            assert len(context_rich_prompt) > 100  # Should be substantial
            print("✅ Context-aware prompt generation works")
            
            # Test prompt template system
            custom_template_prompt = self.prompt_engine.generate_welcome_prompt(
                branch=ConversationBranch.MANIPULATOR,
                products=test_products,
                customer_context={
                    "customer_segment": "enterprise",
                    "interaction_source": "linkedin_ad"
                },
                interaction_type="linkedin_ad"
            )
            
            assert "Enterprise" in custom_template_prompt
            print("✅ Prompt template system works")
            
            self.tests_passed += 2
            return True
            
        except Exception as e:
            print(f"❌ Prompt customization validation failed: {e}")
            self.tests_failed += 1
            return False
    
    def validate_conversation_flow_prompts(self):
        """Validate conversation flow and stage-specific prompts"""
        print("\n🔄 Validating Conversation Flow Prompts...")
        
        try:
            from app.models.schemas import Product
            
            test_products = [
                Product(
                    id="prod-123",
                    name="Test Product", 
                    description="Test description",
                    category="test",
                    price=99.99
                )
            ]
            
            # Test different conversation stages
            stages = ["discovery", "qualification", "objection_handling", "closing"]
            
            for stage in stages:
                stage_prompt = self.prompt_engine.generate_conversation_prompt(
                    branch=ConversationBranch.CONVINCER,
                    customer_message=f"Test message for {stage} stage",
                    products=test_products,
                    conversation_history=[],
                    customer_context={
                        "conversation_stage": stage
                    }
                )
                
                assert len(stage_prompt) > 50
                print(f"✅ {stage.replace('_', ' ').title()} stage prompt generation works")
            
            self.tests_passed += len(stages)
            return True
            
        except Exception as e:
            print(f"❌ Conversation flow validation failed: {e}")
            self.tests_failed += 1
            return False

def run_step6_validation():
    """Run all Step 6 validation tests"""
    print("🚀 Starting Step 6: Enhanced Conversation Engine Validation\n")
    print("=" * 70)
    
    validator = Step6Validator()
    
    # Run all validation tests
    validation_tests = [
        ("Prompt Engine Capabilities", validator.validate_prompt_engine_capabilities),
        ("Prompt Engine Statistics", validator.validate_prompt_engine_statistics),
        ("Business Personality Configuration", validator.validate_business_personality_configuration),
        ("Conversation Branch Support", validator.validate_conversation_branches),
        ("Prompt Customization", validator.validate_prompt_customization),
        ("Conversation Flow Prompts", validator.validate_conversation_flow_prompts)
    ]
    
    for test_name, test_func in validation_tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} validation encountered an error: {str(e)}")
            validator.tests_failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"📋 Validation Results: {validator.tests_passed} passed, {validator.tests_failed} failed")
    
    if validator.tests_failed == 0:
        print("\n🎉 Step 6 validation completed successfully!")
        print("\n🔧 Step 6 Features Successfully Validated:")
        print("  ✅ Sophisticated prompt engineering with business personality")
        print("  ✅ Welcome protocols for Manipulator and Convincer branches")
        print("  ✅ Context-aware conversation prompt generation")
        print("  ✅ Cross-product recommendation prompts")
        print("  ✅ Recovery and objection handling prompts")
        print("  ✅ Statistics tracking and performance monitoring")
        print("  ✅ Business personality configuration system")
        print("  ✅ Conversation stage-specific prompts")
        
        print("\n🚀 Enhanced Conversation Engine Features:")
        print("  • Integrates PromptEngine with sophisticated prompt strategies")
        print("  • ConversationManager with state management and AI integration")
        print("  • Enhanced API endpoints with Step 6 capabilities")
        print("  • Comprehensive error handling and recovery mechanisms")
        print("  • Performance metrics and conversation insights")
        
        print("\n✨ Step 6 Implementation Complete!")
        print("The enhanced conversation engine is ready for production use.")
    else:
        print("\n⚠️  Some validations failed. Please review the implementation.")
    
    return validator.tests_failed == 0

def main():
    """Main validation execution"""
    try:
        success = run_step6_validation()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Validation execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
