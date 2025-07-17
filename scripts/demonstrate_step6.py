#!/usr/bin/env python3
"""
Step 6 Demonstration: Enhanced Conversation Engine in Action
Shows the sophisticated conversation management and prompt engineering capabilities
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def demonstrate_step6():
    """Demonstrate Step 6 Enhanced Conversation Engine capabilities"""
    print("🚀 Step 6: Enhanced Conversation Engine Demonstration")
    print("=" * 70)
    
    # Import Step 6 components
    print("\n📦 Importing Step 6 Components...")
    from app.services.prompt_engine import PromptEngine
    from app.models.schemas import ConversationBranch, ConversationStatus, Product, ProductAttributes
    
    # Initialize PromptEngine
    print("\n🧠 Initializing Enhanced PromptEngine...")
    prompt_engine = PromptEngine()
    
    # Show business personality
    print("\n🎭 Business Personality Configuration:")
    personality = prompt_engine.business_personality
    for key, value in personality.items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    # Create test products for demonstration
    print("\n📦 Creating Test Products...")
    test_products = [
        Product(
            product_id="prod-001",
            product_attributes=ProductAttributes(
                price="99.99",
                category="productivity",
                brand="ManipulatorAI"
            ),
            product_tag=["software", "productivity", "team-management"],
            product_description="Advanced team management and productivity software suite"
        ),
        Product(
            product_id="prod-002", 
            product_attributes=ProductAttributes(
                price="199.99",
                category="premium",
                brand="ManipulatorAI"
            ),
            product_tag=["premium", "advanced", "analytics"],
            product_description="Premium analytics and reporting suite with advanced features"
        )
    ]
    
    print(f"  ✅ Created {len(test_products)} test products")
    
    # Demonstrate Welcome Prompts
    print("\n🤝 Demonstrating Welcome Prompts...")
    
    # Manipulator branch welcome
    print("\n📢 Manipulator Branch Welcome (from ad click):")
    manipulator_welcome = prompt_engine.generate_welcome_prompt(
        branch=ConversationBranch.MANIPULATOR,
        products=test_products,
        customer_context={
            "interaction_type": "ad_click",
            "customer_behavior": "engaged",
            "product_interest": "team-management"
        },
        interaction_type="ad_click"
    )
    print(f"  💬 {manipulator_welcome[:200]}...")
    
    # Convincer branch welcome
    print("\n📢 Convincer Branch Welcome (from direct message):")
    convincer_welcome = prompt_engine.generate_welcome_prompt(
        branch=ConversationBranch.CONVINCER,
        products=test_products,
        customer_context={
            "customer_message": "I need help with team collaboration",
            "customer_sentiment": "interested"
        },
        interaction_type="message"
    )
    print(f"  💬 {convincer_welcome[:200]}...")
    
    # Demonstrate Conversation Prompts
    print("\n💭 Demonstrating Conversation Prompts...")
    
    conversation_prompt = prompt_engine.generate_conversation_prompt(
        branch=ConversationBranch.CONVINCER,
        customer_message="What features does your team management software include?",
        products=test_products,
        conversation_history=[
            {"sender": "customer", "content": "I'm looking for team management tools"},
            {"sender": "agent", "content": "I'd be happy to help you find the right solution"}
        ],
        customer_context={
            "customer_sentiment": "interested",
            "conversation_stage": "discovery",
            "team_size": "10-20 people"
        }
    )
    print(f"  💭 Context-aware response: {conversation_prompt[:250]}...")
    
    # Demonstrate Cross-Product Recommendations
    print("\n🔄 Demonstrating Cross-Product Recommendations...")
    
    cross_product_prompt = prompt_engine.generate_cross_product_recommendation_prompt(
        original_products=[test_products[0]],
        recommended_products=[test_products[1]],
        customer_context={
            "budget_indicator": "flexible",
            "current_usage": "basic_features",
            "growth_stage": "expanding"
        }
    )
    print(f"  🎯 Upselling recommendation: {cross_product_prompt[:250]}...")
    
    # Demonstrate Recovery Prompts
    print("\n🔧 Demonstrating Recovery Prompts...")
    
    recovery_prompt = prompt_engine.generate_recovery_prompt(
        customer_message="I'm not sure this is what I need",
        products=test_products,
        conversation_history=[
            {"sender": "customer", "content": "I'm hesitant about this"},
            {"sender": "agent", "content": "I understand your concerns"}
        ],
        customer_context={
            "customer_sentiment": "hesitant",
            "objection_type": "uncertain_fit"
        }
    )
    print(f"  🛟 Recovery strategy: {recovery_prompt[:250]}...")
    
    # Show Statistics
    print("\n📊 Prompt Engine Statistics:")
    stats = prompt_engine.get_prompt_statistics()
    for key, value in stats.items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    # Demonstrate Business Personality Update
    print("\n🎨 Demonstrating Business Personality Updates...")
    
    new_personality = {
        "tone": "casual_friendly",
        "approach": "consultative_partnership",
        "persistence_level": "gentle_follow_up",
        "empathy_level": "very_high",
        "expertise_level": "industry_expert"
    }
    
    prompt_engine.update_business_personality(new_personality)
    print("  ✅ Business personality updated successfully")
    
    updated_personality = prompt_engine.business_personality
    print("  📝 New personality configuration:")
    for key, value in updated_personality.items():
        print(f"    • {key.replace('_', ' ').title()}: {value}")
    
    # Final Summary
    print("\n" + "=" * 70)
    print("🎉 Step 6 Demonstration Complete!")
    print("\n✨ Demonstrated Capabilities:")
    print("  • Sophisticated prompt engineering with business personality")
    print("  • Welcome protocols for both conversation branches")
    print("  • Context-aware conversation prompt generation")
    print("  • Cross-product recommendation strategies")
    print("  • Recovery and objection handling prompts")
    print("  • Business personality configuration and updates")
    print("  • Statistics tracking and performance monitoring")
    
    print("\n🚀 Enhanced Conversation Engine Features:")
    print("  • Manipulator branch for ad-driven conversations")
    print("  • Convincer branch for discovery-focused interactions")
    print("  • Advanced conversation state management")
    print("  • AI integration with custom prompt support")
    print("  • Comprehensive conversation analytics")
    
    print("\n🎯 Step 6 Implementation: Production Ready!")
    
    return True

def main():
    """Main demonstration execution"""
    try:
        demonstrate_step6()
        return 0
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
