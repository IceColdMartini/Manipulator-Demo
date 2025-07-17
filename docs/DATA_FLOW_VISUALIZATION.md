# 🌊 ManipulatorAI Data Flow Visualization

## 📊 Complete Data Flow Map

This document provides a clear visualization of how data flows through ManipulatorAI system.

---

## 🔄 Main Data Flow Patterns

### Pattern 1: Webhook-Triggered Conversation Flow
```
📱 Social Media Platform (Facebook/Instagram)
    │
    ▼ [Webhook Event]
🌐 /webhook/facebook or /webhook/instagram
    │
    ▼ [Signature Verification]
🔒 Security Layer
    │
    ▼ [Event Parsing]
📋 Extract Customer Data & Intent
    │
    ▼ [Queue Task]
🔴 Redis Task Queue
    │
    ▼ [Background Processing]
⚙️  Celery Worker
    │
    ▼ [Start Conversation]
🧠 Enhanced Conversation Engine
    │
    ├─── [Product Matching] ──► 📊 PostgreSQL
    │
    ├─── [AI Processing] ──► 🤖 OpenAI/Azure OpenAI
    │
    ▼ [Store Conversation]
💾 MongoDB
    │
    ▼ [Response]
📤 Back to Social Media Platform
```

### Pattern 2: Direct API Conversation Flow
```
👤 Client Application
    │
    ▼ [POST /conversation/message]
🌐 FastAPI Endpoint
    │
    ▼ [Request Validation]
✅ Pydantic Schema Validation
    │
    ▼ [Branch Detection]
🎯 Manipulator vs Convincer Branch
    │
    ▼ [Enhanced Processing]
🧠 Enhanced Conversation Engine
    │
    ├─── [Context Analysis] ──► 🧪 Prompt Engine
    │
    ├─── [Product Lookup] ──► 📊 PostgreSQL
    │
    ├─── [AI Generation] ──► 🤖 OpenAI/Azure OpenAI
    │
    ├─── [Conversation History] ──► 💾 MongoDB
    │
    ▼ [Response Generation]
📤 JSON Response to Client
```

### Pattern 3: Async Task Processing Flow
```
👤 Client Request (async_processing=true)
    │
    ▼ [Create Task ID]
🏷️  Generate Unique Task Identifier
    │
    ▼ [Queue Task]
🔴 Redis Task Queue (Priority: High)
    │
    ▼ [Immediate Response]
📤 Task ID + Status: "queued"
    │
    ▼ [Background Processing]
⚙️  Celery Worker
    │
    ├─── [Process Message] ──► 🧠 Conversation Engine
    │
    ├─── [Store Results] ──► 💾 MongoDB
    │
    ▼ [Update Task Status]
🔴 Redis (Task Results)
    │
    ▼ [Client Polling]
👤 GET /conversation/task/{task_id}/status
    │
    ▼ [Return Results]
📤 Complete Conversation Response
```

---

## 🗄️ Database Data Flow

### PostgreSQL (Structured Data)
```
📊 PostgreSQL Database: manipulator_ai
├── 📋 products
│   ├── id, name, description, category
│   ├── features, pricing, target_audience
│   └── created_at, updated_at
│
├── 👥 customers (if stored)
│   ├── id, facebook_id, instagram_id
│   ├── profile_data, preferences
│   └── created_at, last_interaction
│
└── 📈 analytics
    ├── conversation_metrics
    ├── product_performance
    └── engagement_stats
```

### MongoDB (Document Data)
```
💾 MongoDB Database: manipulator_conversations
├── 💬 conversations
│   ├── conversation_id, customer_id
│   ├── messages: [
│   │   {
│   │     timestamp, sender, content,
│   │     ai_metadata, sentiment_score
│   │   }
│   │ ]
│   ├── branch_type: "manipulator" | "convincer"
│   ├── state: "active" | "completed" | "abandoned"
│   ├── context: { source, industry, company_size }
│   └── created_at, updated_at
│
├── 🎯 customer_profiles
│   ├── customer_id, platform_data
│   ├── conversation_history
│   ├── product_interests
│   └── behavioral_data
│
└── 📊 conversation_analytics
    ├── response_times, engagement_metrics
    ├── conversion_tracking
    └── ai_performance_data
```

### Redis (Cache & Queue Data)
```
🔴 Redis Database
├── 🔄 Task Queues
│   ├── conversations (Priority: High)
│   ├── webhooks (Priority: Medium)
│   └── analytics (Priority: Low)
│
├── 📱 Session Cache
│   ├── conversation_state:{conv_id}
│   ├── customer_context:{customer_id}
│   └── temp_data:{session_id}
│
├── 🏷️  Task Results
│   ├── task_result:{task_id}
│   ├── task_status:{task_id}
│   └── task_metadata:{task_id}
│
└── 🚀 Performance Cache
    ├── product_cache:{query_hash}
    ├── ai_response_cache:{prompt_hash}
    └── rate_limit:{customer_id}
```

---

## 🎯 Component Data Exchange

### 1. Conversation Engine ↔ AI Service
```
Request:
{
  "prompt": "Enhanced conversation prompt",
  "context": "Previous conversation history",
  "customer_data": "Demographics, preferences",
  "business_personality": "Tone, approach, expertise"
}

Response:
{
  "generated_response": "AI-generated message",
  "confidence_score": 0.95,
  "suggested_actions": ["follow_up", "product_demo"],
  "conversation_state": "negotiation"
}
```

### 2. Product Service ↔ Database
```
Query:
{
  "customer_message": "I need CRM software",
  "filters": {
    "company_size": "small_business",
    "budget_range": "low",
    "industry": "retail"
  }
}

Response:
{
  "matched_products": [
    {
      "id": 1,
      "name": "BasicCRM",
      "match_score": 0.92,
      "why_matched": "Perfect for small retail businesses"
    }
  ]
}
```

### 3. Task Manager ↔ Redis
```
Task Creation:
{
  "task_id": "task_abc123",
  "task_type": "process_conversation",
  "priority": "high",
  "payload": {
    "customer_id": "cust_456",
    "message": "Customer message",
    "context": { ... }
  },
  "created_at": "2025-07-16T10:00:00Z"
}

Task Status:
{
  "task_id": "task_abc123",
  "status": "completed",
  "result": {
    "conversation_id": "conv_789",
    "response": "AI response",
    "processing_time": 2.34
  },
  "completed_at": "2025-07-16T10:00:02Z"
}
```

---

## 🚦 Error Flow Patterns

### Error Detection ↔ Recovery
```
🚨 Error Detected
    │
    ▼ [Log Error]
📝 Structured Logging (JSON)
    │
    ▼ [Classify Error]
🔍 Error Handler Analysis
    │
    ├─── [Database Error] ──► 🔄 Retry with Backoff
    │
    ├─── [AI Service Error] ──► 🤖 Fallback Response
    │
    ├─── [Validation Error] ──► ❌ Return 422 with Details
    │
    └─── [Unknown Error] ──► 🛡️  Generic Error Response
    │
    ▼ [Error Recovery]
🔧 Graceful Degradation
    │
    ▼ [Continue Operation]
✅ System Maintains Functionality
```

---

## 📈 Performance Data Flow

### Monitoring ↔ Metrics Collection
```
📊 Performance Metrics
├── 🕐 Response Times
│   ├── API endpoint latency
│   ├── Database query time
│   └── AI service response time
│
├── 🔢 Throughput Metrics
│   ├── Requests per second
│   ├── Tasks processed per minute
│   └── Conversations per hour
│
├── 🎯 Business Metrics
│   ├── Conversion rates
│   ├── Engagement scores
│   └── Customer satisfaction
│
└── 🔧 System Health
    ├── Memory usage
    ├── CPU utilization
    └── Database connections
```

---

## 🎮 Testing Data Flow

### Test Request ↔ System Response
```
🧪 Test Input
    │
    ▼ [API Call]
🌐 ManipulatorAI Endpoint
    │
    ▼ [Processing]
⚙️  All System Components
    │
    ▼ [Response]
📤 Test Output
    │
    ▼ [Validation]
✅ Expected vs Actual Results
    │
    ▼ [Logging]
📝 Test Results Documentation
```

---

## 🔒 Security Data Flow

### Request ↔ Security Validation
```
📱 Incoming Request
    │
    ▼ [Signature Verification]
🔐 HMAC Validation (Webhooks)
    │
    ▼ [Rate Limiting]
🚦 Redis-based Rate Limiting
    │
    ▼ [Input Validation]
✅ Pydantic Schema Validation
    │
    ▼ [Authorization]
🔑 JWT Token Validation (if required)
    │
    ▼ [Process Request]
⚙️  Secure Request Processing
```

---

This data flow visualization helps understand exactly how information moves through ManipulatorAI, making debugging and optimization much easier!
