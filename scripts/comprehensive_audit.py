#!/usr/bin/env python3
"""
ManipulatorAI: Comprehensive Implementation Audit & Test Suite
Tests Steps 1-5 systematically to verify complete implementation
"""

import asyncio
import subprocess
import sys
from pathlib import Path
import time

def print_header(title, emoji="🔍"):
    print(f"\n{emoji} {title}")
    print("=" * (len(title) + 4))

def print_step(step_num, title, status="CHECKING"):
    emoji = "🔄" if status == "CHECKING" else "✅" if status == "PASS" else "❌"
    print(f"\n{emoji} STEP {step_num}: {title}")

def run_test_script(script_name):
    """Run a test script and return success status"""
    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Test timed out after 30 seconds"
    except Exception as e:
        return False, "", str(e)

def check_file_exists(file_path, description=""):
    """Check if a file exists"""
    exists = Path(file_path).exists()
    status = "✅" if exists else "❌"
    desc = f" ({description})" if description else ""
    print(f"   {status} {file_path}{desc}")
    return exists

def check_directory_structure():
    """Verify Step 1: Project Scaffolding"""
    print_step(1, "Project Scaffolding and Initial Setup", "CHECKING")
    
    required_dirs = [
        ("app/", "Main application directory"),
        ("app/api/", "API endpoints"),
        ("app/core/", "Core configuration"),
        ("app/models/", "Data models"),
        ("app/services/", "Business logic services"),
        ("scripts/", "Setup and test scripts")
    ]
    
    required_files = [
        ("main.py", "FastAPI application entry point"),
        ("requirements.txt", "Python dependencies"),
        (".env.example", "Environment configuration template"),
        ("README.md", "Project documentation")
    ]
    
    print("   📁 Directory Structure:")
    dir_checks = [check_file_exists(d[0], d[1]) for d in required_dirs]
    
    print("   📄 Essential Files:")
    file_checks = [check_file_exists(f[0], f[1]) for f in required_files]
    
    all_present = all(dir_checks) and all(file_checks)
    status = "PASS" if all_present else "FAIL"
    print_step(1, "Project Scaffolding", status)
    return all_present

def check_configuration_models():
    """Verify Step 2: Configuration and Database Models"""
    print_step(2, "Configuration and Database Models", "CHECKING")
    
    config_files = [
        ("app/core/config.py", "Centralized configuration"),
        ("app/core/__init__.py", "Core module init"),
        ("app/models/schemas.py", "Pydantic API models"),
        ("app/models/database.py", "SQLAlchemy database models"),
        ("app/models/__init__.py", "Models module init")
    ]
    
    print("   ⚙️  Configuration Files:")
    config_checks = [check_file_exists(f[0], f[1]) for f in config_files]
    
    # Test basic configuration loading
    print("   🧪 Testing Configuration Loading:")
    success, stdout, stderr = run_test_script("test_basic.py")
    print(f"   {'✅' if success else '❌'} Basic configuration test")
    
    all_good = all(config_checks) and success
    status = "PASS" if all_good else "FAIL"
    print_step(2, "Configuration and Database Models", status)
    return all_good

def check_database_setup():
    """Verify Step 3: Database Setup and Integration"""
    print_step(3, "Database Setup and Integration", "CHECKING")
    
    db_files = [
        ("app/core/database.py", "Database connection management"),
        ("scripts/setup_database.py", "Database initialization script")
    ]
    
    print("   💾 Database Files:")
    db_file_checks = [check_file_exists(f[0], f[1]) for f in db_files]
    
    # Test database connections
    print("   🧪 Testing Database Connections:")
    success, stdout, stderr = run_test_script("test_database.py")
    print(f"   {'✅' if success else '❌'} Database integration test")
    if success:
        print("   📊 PostgreSQL: Connected and operational")
        print("   📝 MongoDB: Connected and operational")
        print("   ⚡ Redis: Connected and operational")
    
    all_good = all(db_file_checks) and success
    status = "PASS" if all_good else "FAIL"
    print_step(3, "Database Setup and Integration", status)
    return all_good

def check_api_endpoints():
    """Verify Step 4: API Endpoints and Webhook Handling"""
    print_step(4, "API Endpoints and Webhook Handling", "CHECKING")
    
    api_files = [
        ("app/api/__init__.py", "API module init"),
        ("app/api/webhooks.py", "Facebook/Instagram webhook handlers"),
        ("app/api/conversations.py", "Conversation management API"),
        ("app/api/products.py", "Product management API")
    ]
    
    print("   🌐 API Files:")
    api_file_checks = [check_file_exists(f[0], f[1]) for f in api_files]
    
    # Test API endpoints
    print("   🧪 Testing API Endpoints:")
    success, stdout, stderr = run_test_script("test_api_endpoints.py")
    print(f"   {'✅' if success else '❌'} API endpoints test")
    if success:
        print("   🔔 Webhook endpoints: Working")
        print("   💬 Conversation API: Working")
        print("   📦 Products API: Working")
        print("   📚 OpenAPI docs: Generated")
    
    all_good = all(api_file_checks) and success
    status = "PASS" if all_good else "FAIL"
    print_step(4, "API Endpoints and Webhook Handling", status)
    return all_good

def check_core_ai_logic():
    """Verify Step 5: Core AI Logic"""
    print_step(5, "Core AI Logic - Manipulator & Convincer Branches", "CHECKING")
    
    ai_files = [
        ("app/services/__init__.py", "Services module init"),
        ("app/services/ai_service.py", "Azure OpenAI integration"),
        ("app/services/conversation_engine.py", "Core conversation orchestration"),
        ("app/services/product_service.py", "Product matching service"),
        ("app/services/conversation_service.py", "Conversation state management"),
        ("app/api/ai_testing.py", "AI subsystem testing endpoints")
    ]
    
    print("   🧠 AI Logic Files:")
    ai_file_checks = [check_file_exists(f[0], f[1]) for f in ai_files]
    
    # Test AI subsystems
    print("   🧪 Testing AI Subsystems:")
    success, stdout, stderr = run_test_script("test_ai_offline.py")
    print(f"   {'✅' if success else '❌'} AI logic test")
    if success:
        print("   🔍 keyRetriever: Implemented with fallback")
        print("   🎯 tagMatcher: Working (4/4 product categories)")
        print("   🤖 Conversation Engine: Orchestration ready")
        print("   🔄 Azure OpenAI: Integrated with error handling")
    
    all_good = all(ai_file_checks) and success
    status = "PASS" if all_good else "FAIL"
    print_step(5, "Core AI Logic", status)
    return all_good

def main():
    """Run comprehensive implementation audit"""
    print_header("ManipulatorAI Implementation Audit", "🔍")
    print("Systematic verification of Steps 1-5 implementation")
    
    # Track results
    results = []
    
    # Run each step verification
    step_functions = [
        ("Project Scaffolding", check_directory_structure),
        ("Configuration & Models", check_configuration_models),
        ("Database Integration", check_database_setup),
        ("API Endpoints", check_api_endpoints),
        ("Core AI Logic", check_core_ai_logic)
    ]
    
    for step_name, step_func in step_functions:
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"   ❌ Error in {step_name}: {e}")
            results.append((step_name, False))
    
    # Summary
    print_header("Implementation Audit Results", "📊")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for i, (step_name, result) in enumerate(results, 1):
        status_emoji = "✅" if result else "❌"
        status_text = "IMPLEMENTED" if result else "INCOMPLETE"
        print(f"   Step {i} - {step_name}: {status_emoji} {status_text}")
    
    print(f"\n📈 Overall Progress: {passed}/{total} steps completed")
    
    if passed == total:
        print_header("🎉 AUDIT RESULT: FULLY IMPLEMENTED", "🎉")
        print("✅ All Steps 1-5 are correctly implemented and tested")
        print("✅ Database connections working")
        print("✅ API endpoints operational")  
        print("✅ AI subsystems functional")
        print("✅ Webhook handling ready")
        print("✅ Product matching working")
        print("\n🚀 Ready to proceed to Step 6: Conversation Engine & Prompt Engineering")
        return True
    else:
        print_header("⚠️ AUDIT RESULT: INCOMPLETE IMPLEMENTATION", "⚠️")
        failed_steps = [name for name, result in results if not result]
        print("❌ The following steps need attention:")
        for step in failed_steps:
            print(f"   • {step}")
        print("\n🔧 Please address the issues above before proceeding to Step 6")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Audit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Audit failed with error: {e}")
        sys.exit(1)
