// MongoDB Database Initialization Script for ManipulatorAI
// This script sets up the initial collections, indexes, and sample data

// Switch to the application database
db = db.getSiblingDB('manipulator_conversations');

// Create application user with read/write permissions
db.createUser({
  user: "manipulator_app",
  pwd: "secure_app_password",
  roles: [
    {
      role: "readWrite",
      db: "manipulator_conversations"
    }
  ]
});

// Create conversations collection with schema validation
db.createCollection("conversations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["conversation_id", "customer_id", "business_id", "status", "created_at"],
      properties: {
        conversation_id: {
          bsonType: "string",
          description: "Unique conversation identifier"
        },
        customer_id: {
          bsonType: "string",
          description: "Customer identifier"
        },
        business_id: {
          bsonType: "string",
          description: "Business identifier"
        },
        product_id: {
          bsonType: ["string", "null"],
          description: "Optional product identifier"
        },
        platform: {
          bsonType: "string",
          enum: ["facebook", "instagram", "google", "web", "api"],
          description: "Platform where conversation originated"
        },
        status: {
          bsonType: "string",
          enum: ["active", "completed", "abandoned", "error"],
          description: "Conversation status"
        },
        conversation_type: {
          bsonType: "string",
          enum: ["manipulator", "support", "general"],
          description: "Type of conversation"
        },
        messages: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["message_id", "sender", "content", "timestamp"],
            properties: {
              message_id: {
                bsonType: "string",
                description: "Unique message identifier"
              },
              sender: {
                bsonType: "string",
                enum: ["customer", "ai", "agent"],
                description: "Message sender type"
              },
              content: {
                bsonType: "string",
                description: "Message content"
              },
              timestamp: {
                bsonType: "date",
                description: "Message timestamp"
              },
              metadata: {
                bsonType: "object",
                description: "Additional message metadata"
              }
            }
          }
        },
        ai_context: {
          bsonType: "object",
          description: "AI conversation context and state"
        },
        manipulation_strategy: {
          bsonType: "object",
          description: "Active manipulation strategy details"
        },
        customer_profile: {
          bsonType: "object",
          description: "Customer profile and behavioral data"
        },
        performance_metrics: {
          bsonType: "object",
          description: "Conversation performance tracking"
        },
        created_at: {
          bsonType: "date",
          description: "Conversation creation timestamp"
        },
        updated_at: {
          bsonType: "date",
          description: "Last update timestamp"
        },
        ended_at: {
          bsonType: ["date", "null"],
          description: "Conversation end timestamp"
        }
      }
    }
  }
});

// Create conversation_analytics collection
db.createCollection("conversation_analytics", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["conversation_id", "analytics_type", "data", "generated_at"],
      properties: {
        conversation_id: {
          bsonType: "string",
          description: "Related conversation identifier"
        },
        business_id: {
          bsonType: "string",
          description: "Business identifier"
        },
        analytics_type: {
          bsonType: "string",
          enum: ["sentiment", "engagement", "conversion", "performance", "summary"],
          description: "Type of analytics data"
        },
        data: {
          bsonType: "object",
          description: "Analytics data payload"
        },
        time_period: {
          bsonType: "object",
          description: "Time period for analytics calculation"
        },
        generated_at: {
          bsonType: "date",
          description: "Analytics generation timestamp"
        }
      }
    }
  }
});

// Create customer_sessions collection
db.createCollection("customer_sessions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["session_id", "customer_id", "platform", "started_at"],
      properties: {
        session_id: {
          bsonType: "string",
          description: "Unique session identifier"
        },
        customer_id: {
          bsonType: "string",
          description: "Customer identifier"
        },
        business_id: {
          bsonType: "string",
          description: "Business identifier"
        },
        platform: {
          bsonType: "string",
          description: "Session platform"
        },
        conversation_ids: {
          bsonType: "array",
          items: {
            bsonType: "string"
          },
          description: "List of conversation IDs in this session"
        },
        session_data: {
          bsonType: "object",
          description: "Session-specific data and context"
        },
        started_at: {
          bsonType: "date",
          description: "Session start timestamp"
        },
        ended_at: {
          bsonType: ["date", "null"],
          description: "Session end timestamp"
        },
        duration_seconds: {
          bsonType: ["int", "null"],
          description: "Session duration in seconds"
        }
      }
    }
  }
});

// Create ai_training_data collection
db.createCollection("ai_training_data", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["data_type", "content", "created_at"],
      properties: {
        data_type: {
          bsonType: "string",
          enum: ["conversation", "customer_response", "successful_manipulation", "failed_attempt"],
          description: "Type of training data"
        },
        content: {
          bsonType: "object",
          description: "Training data content"
        },
        labels: {
          bsonType: "array",
          items: {
            bsonType: "string"
          },
          description: "Data labels for training"
        },
        quality_score: {
          bsonType: "number",
          minimum: 0,
          maximum: 1,
          description: "Data quality score (0-1)"
        },
        business_id: {
          bsonType: "string",
          description: "Associated business identifier"
        },
        created_at: {
          bsonType: "date",
          description: "Data creation timestamp"
        }
      }
    }
  }
});

// Create indexes for performance

// Conversations collection indexes
db.conversations.createIndex({ "conversation_id": 1 }, { unique: true });
db.conversations.createIndex({ "customer_id": 1, "business_id": 1 });
db.conversations.createIndex({ "status": 1 });
db.conversations.createIndex({ "platform": 1 });
db.conversations.createIndex({ "created_at": 1 });
db.conversations.createIndex({ "updated_at": 1 });
db.conversations.createIndex({ "business_id": 1, "created_at": -1 });
db.conversations.createIndex({ "messages.timestamp": 1 });

// Conversation analytics indexes
db.conversation_analytics.createIndex({ "conversation_id": 1 });
db.conversation_analytics.createIndex({ "business_id": 1, "analytics_type": 1 });
db.conversation_analytics.createIndex({ "generated_at": 1 });
db.conversation_analytics.createIndex({ "analytics_type": 1, "generated_at": -1 });

// Customer sessions indexes
db.customer_sessions.createIndex({ "session_id": 1 }, { unique: true });
db.customer_sessions.createIndex({ "customer_id": 1, "business_id": 1 });
db.customer_sessions.createIndex({ "platform": 1 });
db.customer_sessions.createIndex({ "started_at": 1 });
db.customer_sessions.createIndex({ "conversation_ids": 1 });

// AI training data indexes
db.ai_training_data.createIndex({ "data_type": 1 });
db.ai_training_data.createIndex({ "business_id": 1 });
db.ai_training_data.createIndex({ "quality_score": 1 });
db.ai_training_data.createIndex({ "created_at": 1 });
db.ai_training_data.createIndex({ "labels": 1 });

// Compound indexes for common queries
db.conversations.createIndex({ 
  "business_id": 1, 
  "status": 1, 
  "created_at": -1 
});

db.conversations.createIndex({ 
  "customer_id": 1, 
  "conversation_type": 1, 
  "created_at": -1 
});

db.conversation_analytics.createIndex({ 
  "business_id": 1, 
  "analytics_type": 1, 
  "generated_at": -1 
});

// Text indexes for search functionality
db.conversations.createIndex({ 
  "messages.content": "text",
  "customer_profile.name": "text",
  "ai_context.summary": "text"
}, {
  name: "conversation_text_search",
  weights: {
    "messages.content": 10,
    "customer_profile.name": 5,
    "ai_context.summary": 3
  }
});

// TTL index for automatic cleanup of old analytics data (90 days)
db.conversation_analytics.createIndex(
  { "generated_at": 1 }, 
  { expireAfterSeconds: 7776000 } // 90 days
);

// Insert sample data for development and testing
const sampleConversationId = "conv_" + new ObjectId().str;
const sampleCustomerId = "cust_demo_001";
const sampleBusinessId = "biz_demo_001";

// Sample conversation
db.conversations.insertOne({
  conversation_id: sampleConversationId,
  customer_id: sampleCustomerId,
  business_id: sampleBusinessId,
  product_id: "prod_demo_001",
  platform: "web",
  status: "active",
  conversation_type: "manipulator",
  messages: [
    {
      message_id: "msg_001",
      sender: "customer",
      content: "Hi, I'm interested in your products",
      timestamp: new Date(),
      metadata: {
        source: "web_chat",
        ip_address: "192.168.1.1"
      }
    },
    {
      message_id: "msg_002",
      sender: "ai",
      content: "Hello! I'd love to help you find the perfect product. What specific features are you looking for?",
      timestamp: new Date(),
      metadata: {
        strategy: "engagement_building",
        confidence: 0.95
      }
    }
  ],
  ai_context: {
    current_strategy: "engagement_building",
    customer_sentiment: "positive",
    conversation_stage: "discovery",
    next_actions: ["product_recommendation", "pain_point_identification"]
  },
  manipulation_strategy: {
    primary_approach: "consultative_selling",
    psychological_triggers: ["authority", "social_proof"],
    current_phase: "rapport_building"
  },
  customer_profile: {
    name: "Demo Customer",
    estimated_budget: "medium",
    pain_points: ["efficiency", "cost"],
    behavioral_traits: ["analytical", "cautious"]
  },
  performance_metrics: {
    engagement_score: 0.8,
    response_time_avg: 1.2,
    message_count: 2
  },
  created_at: new Date(),
  updated_at: new Date(),
  ended_at: null
});

// Sample analytics data
db.conversation_analytics.insertOne({
  conversation_id: sampleConversationId,
  business_id: sampleBusinessId,
  analytics_type: "engagement",
  data: {
    engagement_score: 0.8,
    response_rate: 1.0,
    avg_response_time: 1.2,
    sentiment_trend: "positive",
    key_topics: ["product_inquiry", "feature_comparison"]
  },
  time_period: {
    start: new Date(),
    end: new Date()
  },
  generated_at: new Date()
});

// Sample customer session
db.customer_sessions.insertOne({
  session_id: "sess_" + new ObjectId().str,
  customer_id: sampleCustomerId,
  business_id: sampleBusinessId,
  platform: "web",
  conversation_ids: [sampleConversationId],
  session_data: {
    user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    referrer: "https://google.com",
    page_views: 3,
    time_on_site: 180
  },
  started_at: new Date(),
  ended_at: null,
  duration_seconds: null
});

// Sample training data
db.ai_training_data.insertOne({
  data_type: "successful_manipulation",
  content: {
    conversation_excerpt: [
      {
        sender: "ai",
        message: "I understand you're looking for value. This product actually saves most customers 30% on their monthly costs."
      },
      {
        sender: "customer", 
        message: "That sounds interesting, tell me more about the savings."
      }
    ],
    outcome: "increased_engagement",
    strategy_used: "value_proposition"
  },
  labels: ["cost_savings", "value_emphasis", "customer_interest"],
  quality_score: 0.9,
  business_id: sampleBusinessId,
  created_at: new Date()
});

// Create database-level settings
db.runCommand({
  "collMod": "conversations",
  "validationLevel": "strict",
  "validationAction": "error"
});

print("MongoDB database initialization completed successfully!");
print("Database: manipulator_conversations");
print("Collections created:");
print("- conversations (with schema validation)");
print("- conversation_analytics");
print("- customer_sessions");
print("- ai_training_data");
print("Indexes created for optimal performance");
print("Sample data inserted for development and testing");
print("Application user 'manipulator_app' created with read/write permissions");
