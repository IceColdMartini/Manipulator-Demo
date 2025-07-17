# 🎯 ManipulatorAI Complete End-to-End Developer Guide

## 🌟 Executive Summary

ManipulatorAI is a sophisticated AI-powered conversation manipulation system that transforms social media interactions into qualified leads. Here's how to test and understand the complete data flow as a developer.

---

## 🚀 Quick Start Testing (Choose Your Method)

### Method 1: Docker Deployment (Recommended)
```bash
# 1. Ensure Docker is running
open -a Docker

# 2. Configure environment
cd /Users/Kazi/Desktop/Manipulator-Demo
cp .env.example .env
# Edit .env with your OpenAI API key

# 3. Deploy full stack
./scripts/deploy.sh deploy

# 4. Run comprehensive tests
./scripts/test_e2e.sh
```

### Method 2: Local Development
```bash
# 1. Setup Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Start databases manually (requires local Redis, PostgreSQL, MongoDB)
# Or use Docker for databases only:
docker-compose up -d redis postgres mongodb

# 3. Start application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Test in another terminal
./scripts/test_e2e.sh
```

---

## 🔄 Complete Data Flow Walkthrough

### 📱 Scenario 1: Facebook Ad Interaction (Manipulator Branch)

**Data Flow Step-by-Step:**

1. **Customer Interaction on Facebook**
   ```
   Customer sees ad → Clicks → Comments: "Interested in your CRM software"
   ```

2. **Facebook Webhook Event**
   ```json
   POST /webhook/facebook
   {
     "object": "page",
     "entry": [{
       "messaging": [{
         "sender": {"id": "customer_123"},
         "message": {"text": "Interested in your CRM software"}
       }]
     }]
   }
   ```

3. **ManipulatorAI Processing**
   ```
   Webhook → Security Verification → Redis Queue → Celery Worker
   ```

4. **AI Processing Chain**
   ```
   Extract Intent → Product Matching → AI Response Generation → Store Conversation
   ```

5. **Database Updates**
   ```
   PostgreSQL: Product match scores
   MongoDB: Conversation history
   Redis: Task status, caching
   ```

6. **Response Back to Facebook**
   ```json
   {
     "conversation_id": "conv_abc123",
     "response": "Hi! I'm excited you're interested in our CRM! 
                  Based on your business type, I think our BasicCRM 
                  would be perfect. Can I show you how it can 
                  increase your sales by 30%?",
     "next_actions": ["product_demo", "feature_highlight"]
   }
   ```

### 💬 Scenario 2: Direct API Conversation (Convincer Branch)

**Test Command:**
```bash
curl -X POST http://localhost:8000/conversation/message \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "direct_customer_456",
    "message": "I need help finding the right business software",
    "customer_context": {
      "source": "direct_message", 
      "company_size": "medium_business",
      "industry": "manufacturing"
    },
    "conversation_branch": "convincer"
  }'
```

**Data Flow:**
```
API Call → Validation → Branch Detection (Convincer) → Context Analysis
     ↓
AI Prompt Engineering → OpenAI/Azure API → Response Generation
     ↓  
MongoDB Storage ← PostgreSQL Product Query → Response Assembly
     ↓
JSON Response to Client
```

**Expected Response:**
```json
{
  "conversation_id": "conv_convincer_456",
  "response": "Hello! I'd love to help you find the perfect solution for your manufacturing business. What specific challenges are you facing with your current business processes?",
  "conversation_branch": "convincer",
  "conversation_state": "discovery",
  "next_actions": ["needs_assessment", "pain_point_identification"]
}
```

### ⚡ Scenario 3: Async Task Processing

**Test Command:**
```bash
curl -X POST "http://localhost:8000/conversation/message?async_processing=true" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "async_customer_789",
    "message": "Tell me about all your software products",
    "customer_context": {"urgency": "high"}
  }'
```

**Data Flow:**
```
API Request → Task ID Generation → Redis Queue → Immediate Response
     ↓
Background Processing (Celery) → AI Processing → Result Storage
     ↓
Client Polls Status → Retrieve Results → Return Complete Response
```

**Response Sequence:**
```json
// Immediate response
{
  "task_id": "task_xyz789",
  "status": "queued",
  "estimated_completion": "30 seconds"
}

// Status check: GET /conversation/task/task_xyz789/status
{
  "task_id": "task_xyz789",
  "status": "completed", 
  "result": {
    "conversation_id": "conv_async_789",
    "response": "I'd be happy to tell you about our complete software suite...",
    "processing_time": 2.34
  }
}
```

---

## 🧪 Practical Testing Examples

### Test 1: Health and Basic Functionality
```bash
# Basic health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs

# Check all endpoints
curl http://localhost:8000/ | jq
```

### Test 2: Conversation Engine Deep Dive
```bash
# Test conversation continuation
CONV_ID="conv_abc123"  # From previous test

curl -X POST "http://localhost:8000/conversation/$CONV_ID/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "That sounds expensive, do you have cheaper options?",
    "customer_context": {
      "price_sensitivity": "high",
      "engagement_level": "interested_but_cautious"
    }
  }'
```

### Test 3: Product Matching Intelligence
```bash
# Test AI product matching
curl -X POST http://localhost:8000/ai/match-products \
  -H "Content-Type: application/json" \
  -d '{
    "customer_message": "I run a small restaurant and need help with inventory",
    "customer_context": {
      "industry": "food_service",
      "company_size": "small_business",
      "budget_range": "medium"
    }
  }'
```

### Test 4: Webhook Processing
```bash
# Simulate Facebook webhook
curl -X POST http://localhost:8000/webhook/facebook \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=test_signature" \
  -d '{
    "object": "page",
    "entry": [{
      "messaging": [{
        "sender": {"id": "facebook_user_123"},
        "recipient": {"id": "page_456"},
        "message": {
          "text": "Hi! I clicked on your ad about project management software"
        }
      }]
    }]
  }'
```

---

## 🗄️ Database Data Examples

### PostgreSQL: Product Data Structure
```sql
-- Example products table
SELECT * FROM products WHERE category = 'crm' LIMIT 3;

-- Results:
id | name      | description           | target_audience  | pricing
1  | BasicCRM  | Simple CRM solution   | small_business   | 29/month
2  | ProCRM    | Advanced CRM platform | enterprise       | 199/month  
3  | StartCRM  | Startup-friendly CRM  | startups         | 9/month
```

### MongoDB: Conversation Data Structure
```javascript
// Example conversation document
db.conversations.findOne()

{
  "_id": "conv_abc123",
  "customer_id": "customer_123",
  "conversation_branch": "manipulator",
  "messages": [
    {
      "timestamp": "2025-07-16T10:00:00Z",
      "sender": "customer",
      "content": "Interested in your CRM software",
      "sentiment_score": 0.8
    },
    {
      "timestamp": "2025-07-16T10:00:02Z", 
      "sender": "ai",
      "content": "Hi! I'm excited you're interested...",
      "ai_metadata": {
        "model": "gpt-4",
        "confidence": 0.95,
        "processing_time": 1.2
      }
    }
  ],
  "state": "active",
  "context": {
    "source": "facebook_ad",
    "company_size": "small_business",
    "industry": "retail"
  },
  "analytics": {
    "engagement_score": 0.85,
    "conversion_probability": 0.72
  }
}
```

### Redis: Task and Cache Data
```bash
# Check task queues
redis-cli LLEN conversation_queue    # Active conversation tasks
redis-cli LLEN webhook_queue         # Pending webhook tasks
redis-cli LLEN analytics_queue       # Background analytics tasks

# Check task results
redis-cli GET task_result:task_xyz789

# Check cached data
redis-cli GET product_cache:crm_small_business
redis-cli GET conversation_state:conv_abc123
```

---

## 🔧 Component Integration Testing

### 1. AI Service Integration
```python
# Test AI service directly (Python shell)
from app.services.ai_service import AzureOpenAIService

ai_service = AzureOpenAIService()
response = await ai_service.generate_conversation_response(
    prompt="Customer interested in CRM software",
    context="Small business, retail industry",
    conversation_history=[]
)
print(response.content)
```

### 2. Database Service Integration
```python
# Test database connections
from app.core.database import db_manager

# Check connections
await db_manager.connect_postgresql()
await db_manager.connect_mongodb() 
await db_manager.connect_redis()

# Test queries
from app.services.product_service import ProductService
products = await ProductService.search_products("CRM", {"company_size": "small"})
```

### 3. Task Manager Integration
```python
# Test async task processing
from app.services.task_manager import task_manager

task_id = await task_manager.queue_conversation_task(
    customer_id="test_customer",
    message="Test message",
    context={}
)

# Check task status
status = await task_manager.get_task_status(task_id)
print(f"Task {task_id}: {status}")
```

---

## 📊 Performance and Monitoring

### Key Metrics to Monitor

1. **Response Times**
   ```bash
   # API response time
   curl -w "@curl-format.txt" -s http://localhost:8000/health
   
   # Database query performance
   tail -f logs/performance.log | grep "query_time"
   ```

2. **Task Processing**
   ```bash
   # Celery task monitoring
   open http://localhost:5555  # Flower dashboard
   
   # Task queue lengths
   redis-cli INFO | grep queue
   ```

3. **Error Rates**
   ```bash
   # Check error logs
   tail -f logs/api.log | grep ERROR
   
   # Monitor error rates
   grep -c "ERROR" logs/api.log
   ```

### Performance Benchmarks

- **API Response Time**: < 200ms for sync operations
- **Task Processing**: < 5 seconds for conversation generation
- **Database Queries**: < 100ms for product searches
- **AI Service**: < 3 seconds for response generation

---

## 🚨 Troubleshooting Common Issues

### Issue 1: Service Not Starting
```bash
# Check Docker status
docker --version
docker-compose --version

# Check logs
docker-compose logs app
docker-compose logs postgres
```

### Issue 2: AI Service Errors
```bash
# Verify API key
echo $OPENAI_API_KEY | wc -c  # Should be > 40 characters

# Test API directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

### Issue 3: Database Connection Issues
```bash
# Check database containers
docker-compose ps

# Test connections
psql -h localhost -U postgres -d manipulator_ai -c "SELECT 1;"
mongosh mongodb://localhost:27017/manipulator_conversations --eval "db.stats()"
redis-cli ping
```

---

## 🎯 Expected Outcomes

After running through this guide, you should see:

1. ✅ **All services running** (API, databases, workers)
2. ✅ **API responding** to health checks and documentation
3. ✅ **Conversations working** in both manipulator and convincer branches
4. ✅ **Async processing** functioning with task queuing
5. ✅ **Webhooks handling** social media events
6. ✅ **Data flowing** correctly between all components
7. ✅ **Monitoring active** via Flower dashboard
8. ✅ **Error handling** gracefully managing failures

---

## 🚀 Next Steps

1. **Add Real API Keys**: Configure with actual OpenAI/Facebook credentials
2. **Load Testing**: Use tools like `locust` for performance testing
3. **Integration Testing**: Connect to real Facebook/Instagram webhooks
4. **Monitoring Setup**: Implement Prometheus/Grafana for production
5. **Security Hardening**: Enable all security features for production

This guide gives you complete visibility into how ManipulatorAI processes data from initial customer contact through final response delivery!
