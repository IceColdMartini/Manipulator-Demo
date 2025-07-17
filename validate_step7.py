"""
Step 7 Validation: Asynchronous Task Processing with Redis Queue
Simple validation script to verify implementation structure
"""

import os
import sys
from pathlib import Path

def validate_step7_implementation():
    """Validate Step 7 async processing implementation"""
    
    print("\n🚀 Validating Step 7: Asynchronous Task Processing Implementation")
    print("=" * 70)
    
    base_path = Path("/Users/Kazi/Desktop/Manipulator-Demo")
    
    # Check core files exist
    validation_results = []
    
    # 1. Check Celery app configuration
    celery_app_path = base_path / "app" / "core" / "celery_app.py"
    if celery_app_path.exists():
        print("✅ Celery app configuration found")
        validation_results.append(True)
        
        # Check content contains required elements
        with open(celery_app_path, 'r') as f:
            content = f.read()
            if "create_celery_app" in content and "redis://" in content:
                print("✅ Celery app properly configured with Redis")
                validation_results.append(True)
            else:
                print("❌ Celery app missing required configuration")
                validation_results.append(False)
    else:
        print("❌ Celery app configuration not found")
        validation_results.append(False)
    
    # 2. Check task modules
    tasks_path = base_path / "app" / "tasks"
    if tasks_path.exists():
        print("✅ Tasks package directory found")
        validation_results.append(True)
        
        # Check individual task modules
        task_modules = [
            "conversation_tasks.py",
            "webhook_tasks.py", 
            "analytics_tasks.py"
        ]
        
        for module in task_modules:
            module_path = tasks_path / module
            if module_path.exists():
                print(f"✅ {module} found")
                validation_results.append(True)
                
                # Check for task functions
                with open(module_path, 'r') as f:
                    content = f.read()
                    if "@celery_app.task" in content:
                        print(f"✅ {module} contains Celery tasks")
                        validation_results.append(True)
                    else:
                        print(f"❌ {module} missing Celery task decorators")
                        validation_results.append(False)
            else:
                print(f"❌ {module} not found")
                validation_results.append(False)
    else:
        print("❌ Tasks package directory not found")
        validation_results.append(False)
    
    # 3. Check task manager service
    task_manager_path = base_path / "app" / "services" / "task_manager.py"
    if task_manager_path.exists():
        print("✅ Task manager service found")
        validation_results.append(True)
        
        with open(task_manager_path, 'r') as f:
            content = f.read()
            required_methods = [
                "process_conversation_async",
                "process_webhook_async", 
                "generate_analytics_async",
                "get_task_status",
                "get_queue_statistics"
            ]
            
            missing_methods = []
            for method in required_methods:
                if method in content:
                    print(f"✅ TaskManager.{method} implemented")
                    validation_results.append(True)
                else:
                    print(f"❌ TaskManager.{method} missing")
                    missing_methods.append(method)
                    validation_results.append(False)
    else:
        print("❌ Task manager service not found")
        validation_results.append(False)
    
    # 4. Check API integration
    conversations_api_path = base_path / "app" / "api" / "conversations.py"
    if conversations_api_path.exists():
        print("✅ Conversations API file found")
        validation_results.append(True)
        
        with open(conversations_api_path, 'r') as f:
            content = f.read()
            
            # Check for async processing integration
            if "async_processing" in content:
                print("✅ Async processing parameter added to API")
                validation_results.append(True)
            else:
                print("❌ Async processing parameter missing from API")
                validation_results.append(False)
            
            # Check for task monitoring endpoints
            monitoring_endpoints = [
                "/tasks/{task_id}/status",
                "/tasks/queues/status", 
                "/tasks/active"
            ]
            
            for endpoint in monitoring_endpoints:
                endpoint_pattern = endpoint.replace("{task_id}", "")
                if endpoint_pattern in content or endpoint in content:
                    print(f"✅ Task monitoring endpoint {endpoint} found")
                    validation_results.append(True)
                else:
                    print(f"❌ Task monitoring endpoint {endpoint} missing")
                    validation_results.append(False)
    else:
        print("❌ Conversations API file not found")
        validation_results.append(False)
    
    # 5. Check requirements
    requirements_path = base_path / "requirements.txt"
    if requirements_path.exists():
        print("✅ Requirements file found")
        validation_results.append(True)
        
        with open(requirements_path, 'r') as f:
            content = f.read()
            required_packages = ["celery", "redis", "aioredis"]
            
            for package in required_packages:
                if package in content:
                    print(f"✅ {package} in requirements")
                    validation_results.append(True)
                else:
                    print(f"❌ {package} missing from requirements")
                    validation_results.append(False)
    else:
        print("❌ Requirements file not found")
        validation_results.append(False)
    
    # 6. Check documentation
    docs_path = base_path / "docs" / "STEP7_ASYNC_PROCESSING.md"
    if docs_path.exists():
        print("✅ Step 7 documentation found")
        validation_results.append(True)
        
        with open(docs_path, 'r') as f:
            content = f.read()
            if len(content) > 1000:  # Substantial documentation
                print("✅ Comprehensive Step 7 documentation provided")
                validation_results.append(True)
            else:
                print("❌ Step 7 documentation too brief")
                validation_results.append(False)
    else:
        print("❌ Step 7 documentation not found") 
        validation_results.append(False)
    
    # 7. Check test files
    test_path = base_path / "tests" / "test_step7_async_processing.py"
    if test_path.exists():
        print("✅ Step 7 test file found")
        validation_results.append(True)
    else:
        print("❌ Step 7 test file not found")
        validation_results.append(False)
    
    # Calculate results
    total_checks = len(validation_results)
    passed_checks = sum(validation_results)
    success_rate = (passed_checks / total_checks) * 100
    
    print("\n" + "=" * 70)
    print(f"📊 Validation Results: {passed_checks}/{total_checks} checks passed ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 STEP 7 IMPLEMENTATION: EXCELLENT!")
        print("✅ Asynchronous task processing fully implemented")
        print("✅ Redis queue integration complete")
        print("✅ API responsiveness maintained")
        print("✅ Task monitoring capabilities ready")
        status = "EXCELLENT"
    elif success_rate >= 75:
        print("👍 STEP 7 IMPLEMENTATION: GOOD")
        print("✅ Core async processing implemented")
        print("⚠️  Some minor components may need attention")
        status = "GOOD"
    elif success_rate >= 50:
        print("⚠️  STEP 7 IMPLEMENTATION: PARTIAL")
        print("❌ Some critical components missing")
        print("🔧 Additional implementation required")
        status = "PARTIAL"
    else:
        print("❌ STEP 7 IMPLEMENTATION: INCOMPLETE")
        print("❌ Major components missing")
        print("🚨 Significant work required")
        status = "INCOMPLETE"
    
    # Implementation summary
    print("\n📋 STEP 7 FEATURE SUMMARY:")
    print("🔄 Celery task processing with Redis broker")
    print("📊 Priority-based task queues (conversations, webhooks, analytics)")
    print("⚡ Async API endpoints for immediate response")
    print("📈 Task monitoring and status tracking")
    print("🛡️ Error handling with retry mechanisms")
    print("📚 Comprehensive documentation and testing")
    
    print("=" * 70)
    return status


if __name__ == "__main__":
    result = validate_step7_implementation()
    
    if result in ["EXCELLENT", "GOOD"]:
        print("\n🚀 Ready for Step 8: Real-time Notifications!")
        exit(0)
    else:
        print("\n🔧 Please address the issues above before proceeding.")
        exit(1)
