<div align="center">
  <h1>🤖 ManipulatorAI</h1>

  <p>
    <strong>Next-Generation AI Sales Agent Microservice</strong><br>
    Intelligent customer engagement through human-like conversations
  </p>

  ![License](https://img.shields.io/badge/license-MIT-blue.svg)
  ![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
  ![Azure](https://img.shields.io/badge/Azure-OpenAI-0089D0.svg)
  ![Redis](https://img.shields.io/badge/Redis-Queue-DC382D.svg)
  ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791.svg)
  ![MongoDB](https://img.shields.io/badge/MongoDB-Conversations-47A248.svg)

  <p>
    <a href="#overview">Overview</a> •
    <a href="#features">Features</a> •
    <a href="#getting-started">Getting Started</a> •
    <a href="#development">Development</a> •
    <a href="#api-reference">API Reference</a>
  </p>
</div>

## Overview

ManipulatorAI is an intelligent AI-powered sales agent microservice that automatically engages with potential customers through social media interactions, guiding them through a natural conversation flow towards product interest and registration.

## Features

- 🤖 Automated customer engagement through social media
- 💬 Natural, human-like conversations powered by Azure OpenAI
- 🎯 Smart product matching and recommendations
- 📊 Redis-based queue system for reliable processing
- 🔄 Seamless handoff to Onboarding Agent
- 📱 Facebook and Instagram integration

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- MongoDB 4.4+
- Redis Server
- Azure OpenAI API access

### Installation

1. Clone the repository:
\`\`\`bash
git clone https://github.com/yourusername/manipulator-ai.git
cd manipulator-ai
\`\`\`

2. Set up a virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
\`\`\`

3. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Configure environment variables:
\`\`\`bash
cp .env.example .env
# Edit .env with your configuration
\`\`\`

5. Start the server:
\`\`\`bash
python src/main.py
\`\`\`

## Development

### Project Structure

\`\`\`
manipulator-ai/
├── src/
│   ├── api/        # API endpoints
│   ├── core/       # Core functionality
│   ├── database/   # Database models and connections
│   ├── models/     # Pydantic models
│   ├── services/   # Business logic
│   └── utils/      # Utility functions
├── tests/          # Test cases
├── config/         # Configuration files
├── requirements.txt
└── README.md
\`\`\`

### Running Tests

\`\`\`bash
pytest tests/
\`\`\`

## API Reference

Detailed API documentation is available at `/docs` when running the server.

  <p>
    <a href="#-features">Features</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-workflow">Workflow</a> •
    <a href="#-api-reference">API</a>
  </p>
</div>

---

## 🚀 Overview

**ManipulatorAI** is a cutting-edge AI Agent microservice that revolutionizes customer engagement by conducting intelligent first-time conversations with potential customers. Seamlessly integrated into multi-agent SaaS platforms, it transforms social media interactions into qualified leads through sophisticated AI-powered persuasion techniques.

### 🎯 Mission

**Primary Function**: First direct communication with potential customers
**Objective**: Convert prospects to qualified leads through intelligent conversation and seamless handoff to Onboarding Agent

## ✨ Features

<table>
<tr>
<td>

### 🧠 **Intelligent Conversation**
- Human-like dialogue patterns
- Context-aware responses
- Persuasive communication techniques

</td>
<td>

### 🎯 **Smart Targeting**
- Real-time social media integration
- Product-focused engagement
- Cross-product recommendations

</td>
</tr>
<tr>
<td>

### ⚡ **High Performance**
- Redis queue processing
- Scalable microservice architecture
- Real-time webhook triggers

</td>
<td>

### 🔄 **Seamless Integration**
- Multi-agent platform compatibility
- Azure OpenAI powered responses
- Automated lead qualification

</td>
</tr>
</table>

## 📖 Description

> **Transforming Social Media Engagement into Revenue**

ManipulatorAI is a critical component of a comprehensive **multi-agent SaaS platform** that eliminates human-powered customer communication bottlenecks. Built for business owners who demand automated, intelligent consumer attraction and engagement processes.

```mermaid
graph LR
    A[👤 Customer Interaction] --> B[🔔 Webhook Trigger]
    B --> C[📊 Redis Queue]
    C --> D[🤖 ManipulatorAI]
    D --> E[💬 AI Conversation]
    E --> F[✅ Lead Qualified]
    F --> G[🎯 Onboarding Agent]
```

### 🏢 **Enterprise-Grade Features**

| Feature | Description | Technology |
|---------|-------------|------------|
| **Social Media Integration** | Real-time Facebook/Instagram webhook processing | `REST APIs` `Webhooks` |
| **Intelligent Product Matching** | AI-powered product correlation and recommendations | `Azure OpenAI` `NLP` |
| **Conversation Persistence** | Complete chat history and context management | `MongoDB` `Session Management` |
| **Queue Management** | High-throughput request processing | `Redis` `Microservices` |
| **Knowledge Base** | Comprehensive product database with smart retrieval | `PostgreSQL` `JSON Schema` |

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Social Media Layer"
        A[📱 Facebook/Instagram Ads]
        B[👆 User Interactions]
    end

    subgraph "Processing Layer"
        C[🔔 Webhooks]
        D[📊 Redis Queue]
        E[🤖 ManipulatorAI Service]
    end

    subgraph "Intelligence Layer"
        F[🧠 Azure OpenAI]
        G[🔍 keyRetriever]
        H[🎯 tagMatcher]
    end

    subgraph "Data Layer"
        I[🗄️ PostgreSQL<br/>Product Database]
        J[💾 MongoDB<br/>Conversations]
    end

    subgraph "Integration Layer"
        K[🎯 Onboarding Agent]
        L[📊 Business Dashboard]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    E --> H
    G --> I
    H --> I
    E --> J
    E --> K
    E --> L
```

### 🔧 **Core Functionality**

<details>
<summary><strong>🎭 Social Media Integration</strong></summary>

The agent operates seamlessly in **Facebook/Instagram** environments where business clients advertise their products. Advanced webhook integration ensures real-time response to customer interactions.

**Supported Interactions:**
- ❤️ **Likes** - Engagement tracking
- 💬 **Comments** - Conversation starters
- 👆 **Clicks** - Intent signals
- 📩 **Direct Messages** - Immediate response

</details>

<details>
<summary><strong>🧠 AI-Powered Conversations</strong></summary>

Leveraging **Azure OpenAI** models for natural, persuasive conversations that feel authentically human while maintaining business objectives.

**Conversation Features:**
- 🤝 Cordial greeting and introductory dialogue
- 🎯 Product-focused conversations based on user interaction
- 🎭 Human-like persuasion techniques to encourage registration
- 🔄 Seamless handoff to Onboarding Agent upon conversion
- 🛍️ Cross-product recommendations for uninterested customers
- 💪 Persistent yet polite engagement strategies

</details>

### 🌐 **Platform Integration**

<div align="center">

```mermaid
graph LR
    subgraph "Multi-Agent Ecosystem"
        A[🤖 ManipulatorAI<br/>First Contact]
        B[🎯 Onboarding Agent<br/>Registration]
        C[📊 Analytics Agent<br/>Insights]
        D[🛡️ Security Agent<br/>Protection]
    end

    E[👥 Business Owners] --> F[📊 Management Dashboard]
    F --> A
    A --> B
    B --> C
    A --> D
```

</div>

**Ecosystem Benefits:**
- 🤖 **Automated Consumer Attraction** - Zero human intervention required
- 📊 **Comprehensive Platform Oversight** - Real-time business owner dashboards
- 🔄 **Intelligent Sales Process Automation** - End-to-end funnel management
- 🎯 **Complete Engagement Funnel** - From first contact to conversion

## 🚀 Quick Start

### Prerequisites

```bash
# Required Technologies
Python 3.9+
Redis Server
PostgreSQL 13+
MongoDB 4.4+
Azure OpenAI API Access
```

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ManipulatorAI.git
cd ManipulatorAI

# Install dependencies
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Edit .env with your configuration

# Database setup
python scripts/setup_database.py

# Start the service
python main.py
```

### Configuration

```yaml
# config.yml
azure:
  openai_api_key: "your-api-key"
  endpoint: "your-endpoint"

database:
  postgresql_url: "postgresql://user:pass@localhost/db"
  mongodb_url: "mongodb://localhost:27017/conversations"

redis:
  host: "localhost"
  port: 6379

webhooks:
  facebook_verify_token: "your-verify-token"
  instagram_verify_token: "your-verify-token"
```

## 🔄 Workflow

### 📋 **Process Overview**

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant SM as 📱 Social Media
    participant W as 🔔 Webhook
    participant R as 📊 Redis Queue
    participant MA as 🤖 ManipulatorAI
    participant AI as 🧠 Azure OpenAI
    participant DB as 🗄️ Database
    participant OA as 🎯 Onboarding Agent

    U->>SM: Interacts with ad/post
    SM->>W: Sends notification
    W->>R: Queues request
    R->>MA: Processes request
    MA->>DB: Fetches product data
    MA->>AI: Generates response
    AI->>MA: Returns conversation
    MA->>U: Sends message
    U->>MA: Responds
    MA->>OA: Transfers qualified lead
```

### 🏗️ **System Components**

| Component | Purpose | Technology Stack |
|-----------|---------|------------------|
| 🔔 **Webhook Triggers** | Real-time social media event capture | `FastAPI` `REST` |
| 📊 **Queue Processing** | High-throughput request management | `Redis` `Celery` |
| 🤖 **AI Conversation** | Intelligent customer interaction | `Azure OpenAI` `GPT-4` |
| 🗄️ **Knowledge Base** | Product information storage | `PostgreSQL` `JSON Schema` |

### 💾 **Product Database Schema**

```sql
CREATE TABLE products (
    product_id          UUID PRIMARY KEY,
    product_attributes  JSONB NOT NULL,
    product_tag         TEXT[] NOT NULL,
    product_description TEXT NOT NULL,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

-- Example record
{
    "product_id": "uuid-here",
    "product_attributes": {
        "price": "$29.99",
        "color": "Blue",
        "category": "Electronics",
        "brand": "TechCorp"
    },
    "product_tag": ["smartphone", "mobile", "tech", "communication"],
    "product_description": "Advanced smartphone with cutting-edge features..."
}
```

## 🎯 Operational Branches

<div align="center">

```mermaid
graph TD
    A[📱 Customer Interaction] --> B{Interaction Type}
    B -->|User clicks/likes ad| C[🎭 Manipulator Branch]
    B -->|User sends message| D[🎯 Convincer Branch]

    C --> E[📋 Direct Product ID]
    E --> F[🗄️ Database Query]

    D --> G[🔍 keyRetriever]
    G --> H[🎯 tagMatcher]
    H --> I[📋 Product IDs]
    I --> F

    F --> J[💬 AI Conversation]
    J --> K[✅ Lead Qualification]
    K --> L[🎯 Onboarding Agent]

    style C fill:#e1f5fe
    style D fill:#f3e5f5
    style J fill:#e8f5e8
```

</div>

### 🎭 **Branch 1: Manipulator**

**🎯 Trigger**: Direct user interaction with ads/posts

```python
# Example workflow
def manipulator_branch(interaction_data):
    product_id = extract_product_id(interaction_data)
    product_info = database.get_product(product_id)

    conversation = initiate_conversation(
        interaction_type="proactive",
        product_context=product_info
    )

    return conversation
```

**Features:**
- ⚡ **Instant Product Identification** - Direct access via interaction metadata
- 🎯 **Targeted Engagement** - Product-specific conversation starters
- 🚀 **Proactive Approach** - Agent initiates contact

### 🎯 **Branch 2: Convincer**

**🎯 Trigger**: Customer-initiated contact via messaging

```python
# Example workflow
def convincer_branch(customer_message):
    # Step 1: Extract keywords
    keywords = keyRetriever(
        message=customer_message,
        business_context=get_business_summary()
    )

    # Step 2: Match products
    product_matches = tagMatcher(
        keywords=keywords,
        correlation_threshold=0.8
    )

    return product_matches
```

**Sub-Systems:**

<details>
<summary><strong>🔍 keyRetriever Sub-system</strong></summary>

**Purpose**: Intelligent keyword extraction from customer messages

```python
def keyRetriever(message: str, business_context: str) -> List[str]:
    """
    Extract relevant keywords from customer message using LLM

    Args:
        message: Customer's text input
        business_context: Summary of business products/services

    Returns:
        List of extracted keywords related to business offerings
    """
    prompt = f"""
    Business Context: {business_context}
    Customer Message: {message}

    Extract keywords that relate to our business offerings.
    Focus on product-related terms, intents, and interests.
    """

    return llm_extract_keywords(prompt)
```

**Input/Output Flow:**
- 📥 **Input**: Customer message + Business product summary
- ⚙️ **Process**: LLM-powered topic selection and keyword identification
- 📤 **Output**: Relevant keywords related to business products

</details>

<details>
<summary><strong>🎯 tagMatcher Sub-system</strong></summary>

**Purpose**: Product correlation and intelligent matching

```python
def tagMatcher(keywords: List[str], threshold: float = 0.8) -> List[str]:
    """
    Match keywords with product tags using correlation scoring

    Args:
        keywords: Extracted keywords from customer message
        threshold: Minimum correlation score (default: 0.8)

    Returns:
        List of matched product IDs with high correlation
    """

    matches = []
    for product in database.get_all_products():
        correlation = calculate_similarity(keywords, product.tags)
        if correlation >= threshold:
            matches.append({
                'product_id': product.id,
                'score': correlation
            })

    return sorted(matches, key=lambda x: x['score'], reverse=True)
```

**Process Flow:**
- 📥 **Input**: Keywords from keyRetriever + Database product_tags
- ⚙️ **Process**: Correlation scoring with top-K retrieval (≥80% threshold)
- 📤 **Output**: Ranked product_id(s) for conversation context

</details>

## 💬 Conversation Management

### 🔧 **Pre-Conversation Setup**

```mermaid
graph LR
    A[🎯 Product Identification] --> B[🗄️ Database Query]
    B --> C[📝 Context Preparation]
    C --> D[🤖 LLM Initialization]
    D --> E[💬 Conversation Start]
```

**Setup Process:**
1. 🎯 **Product Identification** - Via appropriate branch workflow
2. 🗄️ **Database Query** - Fetch product_description(s)
3. 📝 **Context Preparation** - Prepare conversation context for LLM

### 🎨 **Prompt Engineering Strategy**

<details>
<summary><strong>👋 Welcome Protocol</strong></summary>

```python
def generate_welcome_prompt(product_info: dict, interaction_type: str) -> str:
    """
    Generate personalized welcome message based on product context
    """

    template = """
    You are a friendly sales representative for {business_name}.

    Context:
    - Customer showed interest in: {product_genre}
    - Interaction type: {interaction_type}
    - Products to focus on: {product_list}

    Guidelines:
    - Start with a warm, human-like greeting
    - Reference their specific interest
    - Offer assistance in a natural way
    - Keep it conversational, not salesy

    Generate a welcoming message that feels genuine and helpful.
    """

    return template.format(
        business_name=get_business_name(),
        product_genre=summarize_product_genre(product_info),
        interaction_type=interaction_type,
        product_list=format_product_list(product_info)
    )
```

**Protocol Features:**
- 🎯 **One-time Activation** - Triggered only for first interactions
- 🤝 **Warm Human-like Greeting** - Builds immediate rapport
- 📋 **Product Genre Summarization** - Contextual product introduction
- ❓ **Interest Confirmation** - Natural assistance offering

</details>

<details>
<summary><strong>🎭 Conversation Guidelines</strong></summary>

```yaml
# Conversation Strategy Configuration
conversation_strategy:
  tone: "polite_persuasive"
  persistence_level: "moderate"
  product_focus: "primary_then_cross_sell"

  guidelines:
    - custom_tailored_responses: true
    - polite_yet_persuasive: true
    - persistence_with_uninterested: true
    - cross_product_recommendations: true
    - graceful_conclusion: true

  thresholds:
    cross_product_correlation: 0.75
    max_persistence_attempts: 3
    conversation_timeout_minutes: 30
```

**Key Strategies:**
- 🎯 **Custom-Tailored Responses** - Specific to business products
- 🤝 **Polite Yet Persuasive** - Maintains professional communication
- 💪 **Strategic Persistence** - Gentle follow-up with uninterested customers
- 🛍️ **Cross-Product Recommendations** - 70-80% correlation threshold
- 🙏 **Graceful Conclusion** - Professional conversation ending with future engagement invitation

</details>

### 💾 **Database Management**

```mermaid
graph TB
    subgraph "Conversation Storage - MongoDB"
        A[💬 Active Conversations]
        B[📚 Chat History]
        C[🎯 User Context]
        D[📊 Conversation Analytics]
    end

    subgraph "Data Flow"
        E[🔄 Real-time Updates] --> A
        A --> F[🧠 LLM Context Feed]
        F --> G[📝 Response Generation]
        G --> B
        B --> H[📊 Analytics Processing]
    end
```

**Storage Strategy:**
- 📝 **Complete Context Preservation** - Full conversation history maintained
- 🔄 **Real-time Updates** - Immediate conversation state synchronization
- 🧠 **LLM Context Feeding** - Historical data for response generation
- 🔄 **Seamless Continuity** - Uninterrupted conversation flow across interactions

```json
// Example conversation document structure
{
  "_id": "conversation_uuid",
  "customer_id": "customer_uuid",
  "business_id": "business_uuid",
  "product_context": ["product_id_1", "product_id_2"],
  "conversation_branch": "manipulator", // or "convincer"
  "messages": [
    {
      "timestamp": "2025-07-08T10:30:00Z",
      "sender": "agent",
      "content": "Hello! I noticed you liked our smartphone ad...",
      "intent": "welcome"
    },
    {
      "timestamp": "2025-07-08T10:31:00Z",
      "sender": "customer",
      "content": "Yes, I'm looking for a new phone",
      "sentiment": "interested"
    }
  ],
  "status": "active", // active, qualified, uninterested, transferred
  "created_at": "2025-07-08T10:30:00Z",
  "updated_at": "2025-07-08T10:31:00Z"
}
```

## 🛠️ Technical Architecture

<div align="center">

```mermaid
graph TB
    subgraph "🌐 Client Layer"
        A[📱 Facebook/Instagram]
        B[👥 Business Dashboard]
    end

    subgraph "🔌 API Gateway"
        C[🔔 Webhook Endpoints]
        D[📡 REST API]
    end

    subgraph "⚡ Processing Layer"
        E[📊 Redis Queue]
        F[🤖 ManipulatorAI Service]
        G[🔍 keyRetriever]
        H[🎯 tagMatcher]
    end

    subgraph "🧠 AI Layer"
        I[🤖 Azure OpenAI GPT-4]
        J[📝 Prompt Engineering]
        K[🎭 Conversation Engine]
    end

    subgraph "💾 Data Layer"
        L[(🗄️ PostgreSQL<br/>Products)]
        M[(💾 MongoDB<br/>Conversations)]
        N[(⚡ Redis<br/>Cache)]
    end

    subgraph "🔗 Integration Layer"
        O[🎯 Onboarding Agent]
        P[📊 Analytics Service]
    end

    A --> C
    B --> D
    C --> E
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    I --> J
    J --> K
    K --> F
    G --> L
    H --> L
    F --> M
    F --> N
    F --> O
    F --> P

    style F fill:#e3f2fd
    style I fill:#fff3e0
    style L fill:#e8f5e8
    style M fill:#fce4ec
```

</div>

### 🏗️ **System Stack**

| Layer | Component | Technology | Purpose |
|-------|-----------|------------|---------|
| **🌐 Frontend** | Social Media Integration | `Facebook Graph API` `Instagram Basic Display` | Real-time interaction capture |
| **🔌 API** | Webhook Processing | `FastAPI` `Pydantic` `AsyncIO` | High-performance request handling |
| **⚡ Queue** | Message Processing | `Redis` `Celery` `Bull Queue` | Scalable async processing |
| **🤖 Core** | AI Agent Service | `Python 3.9+` `AsyncIO` `Type Hints` | Main conversation logic |
| **🧠 AI** | Language Model | `Azure OpenAI GPT-4` `LangChain` | Natural conversation generation |
| **💾 Database** | Product Knowledge | `PostgreSQL 13+` `SQLAlchemy` | Structured product data |
| **💾 Storage** | Conversations | `MongoDB 4.4+` `Motor` | Flexible chat storage |
| **⚡ Cache** | Performance | `Redis` `AsyncRedis` | High-speed data access |

### 📊 **Performance Metrics**

```yaml
Performance Targets:
  response_time: "<200ms"
  throughput: "1000+ req/sec"
  availability: "99.9%"
  conversation_latency: "<2s"

Scalability:
  horizontal_scaling: true
  auto_scaling: true
  load_balancing: true
  microservice_architecture: true
```

## 🔗 Integration Points

<div align="center">

```mermaid
graph LR
    subgraph "📥 Input Sources"
        A[📱 Social Media Webhooks]
        B[💬 Customer Messages]
        C[📊 Business Dashboard]
    end

    subgraph "🤖 ManipulatorAI"
        D[⚡ Processing Engine]
        E[🧠 AI Conversation]
        F[📝 Lead Qualification]
    end

    subgraph "📤 Output Destinations"
        G[🎯 Onboarding Agent]
        H[📊 Analytics Platform]
        I[💼 CRM Integration]
        J[📈 Business Intelligence]
    end

    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    F --> J
```

</div>

### 🔌 **API Endpoints**

```python
# Main API Routes
@app.post("/webhook/facebook")
async def facebook_webhook(payload: FacebookWebhook):
    """Handle Facebook interaction webhooks"""

@app.post("/webhook/instagram")
async def instagram_webhook(payload: InstagramWebhook):
    """Handle Instagram interaction webhooks"""

@app.post("/conversation/message")
async def process_message(message: CustomerMessage):
    """Process incoming customer messages"""

@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Retrieve conversation history"""

@app.post("/lead/qualify")
async def qualify_lead(conversation_id: str):
    """Mark lead as qualified and transfer to onboarding"""
```

### 🔄 **Data Flow**

| Stage | Input | Process | Output |
|-------|-------|---------|---------|
| **📥 Ingestion** | Social media events | Webhook validation & queuing | Structured event data |
| **🔍 Analysis** | Customer interactions | AI-powered intent detection | Product recommendations |
| **💬 Conversation** | Context + User message | LLM response generation | Personalized replies |
| **📊 Qualification** | Conversation analysis | Lead scoring algorithms | Qualified leads |
| **🔗 Transfer** | Qualified leads | Secure data handoff | Onboarding pipeline |

### 🌐 **Multi-Client Architecture**

- **🏢 Tenant Isolation** - Complete data separation per business client
- **📊 Centralized Monitoring** - Unified dashboard for all clients
- **⚖️ Resource Scaling** - Dynamic allocation based on client needs
- **🔒 Security Compliance** - Enterprise-grade data protection

---

<div align="center">

## 🚀 Get Started Today

**Ready to transform your customer engagement?**

[![Deploy](https://img.shields.io/badge/Deploy-Azure-0089D0.svg?style=for-the-badge)](https://azure.microsoft.com)
[![Documentation](https://img.shields.io/badge/Docs-Read%20More-blue.svg?style=for-the-badge)](#)
[![Demo](https://img.shields.io/badge/Demo-Try%20Now-green.svg?style=for-the-badge)](#)

</div>

---

<div align="center">
  <p>
    <sub>Built with ❤️ by Kazi Fahim Tahmid for the future of AI-powered customer engagement</sub>
  </p>

  <p>
    <a href="#-overview">Back to Top</a>
  </p>
</div>