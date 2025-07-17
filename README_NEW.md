# ManipulatorAI 🤖

**Advanced AI-powered conversation manipulation and webhook processing platform**

ManipulatorAI is a sophisticated system that combines artificial intelligence, asynchronous task processing, and multi-platform webhook integration to create engaging, persuasive conversations with customers across various digital platforms.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🔄 **Asynchronous Task Processing**
- **Redis-backed Celery** task queue for responsive API
- **Priority-based queues** (conversations → high, webhooks → medium, analytics → low)
- **Real-time task monitoring** with Flower dashboard
- **Automatic retry mechanisms** with exponential backoff

### 💬 **Intelligent Conversation Engine**
- **AI-powered conversation manipulation** using OpenAI/Azure OpenAI
- **Dynamic conversation strategies** based on customer behavior
- **Multi-turn conversation handling** with context preservation
- **Customer profiling and behavioral analysis**

### 🌐 **Multi-Platform Webhook Integration**
- **Facebook/Instagram** webhook processing
- **Google platform** integration
- **Generic webhook** handler for custom platforms
- **Asynchronous webhook processing** for fast response times

### 📊 **Comprehensive Analytics**
- **Real-time conversation analytics** and insights
- **Performance metrics** and engagement tracking
- **Customer behavior analysis** and profiling
- **Automated reporting** with scheduled analytics

### 🛡️ **Production-Ready Infrastructure**
- **Comprehensive error handling** with recovery mechanisms
- **Structured logging** with JSON format and rotation
- **Health monitoring** and system status endpoints
- **Docker containerization** with multi-stage builds

### 🔐 **Security & Monitoring**
- **Rate limiting** and DDoS protection
- **CORS configuration** for secure cross-origin requests
- **Comprehensive audit logging** for compliance
- **Performance monitoring** with detailed metrics

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Git** for cloning the repository
- **OpenAI API key** or **Azure OpenAI** credentials

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/manipulator-ai.git
cd manipulator-ai

# Copy environment configuration
cp .env.example .env

# Edit .env with your API keys and configuration
nano .env  # or your preferred editor
```

### 2. Configure Environment

Update `.env` with your credentials:

```bash
# Core API Keys (required)
OPENAI_API_KEY=your-openai-api-key-here
# OR for Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=your-azure-openai-endpoint

# Social Media Integration
FACEBOOK_VERIFY_TOKEN=your-facebook-verify-token
FACEBOOK_ACCESS_TOKEN=your-facebook-access-token

# Security
SECRET_KEY=your-super-secret-key-change-in-production
```

### 3. Deploy with Docker

```bash
# Full deployment (recommended)
./scripts/deploy.sh deploy

# Or manually
docker-compose up -d
```

### 4. Verify Installation

```bash
# Check service status
./scripts/deploy.sh status

# Check health
curl http://localhost:8000/health

# Access API documentation
open http://localhost:8000/docs
```

## 📋 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   FastAPI App   │    │  Celery Workers │
│     (Nginx)     │◄──►│   (Main API)    │◄──►│ (Async Tasks)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                       ┌────────▼────────┐              │
                       │     Redis       │◄─────────────┘
                       │ (Broker/Cache)  │
                       └─────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐    ┌────────▼────────┐    ┌─────────▼────────┐
│   PostgreSQL   │    │    MongoDB      │    │     Flower      │
│ (Structured    │    │ (Conversations  │    │   (Monitoring)  │
│    Data)       │    │  & Analytics)   │    │                 │
└────────────────┘    └─────────────────┘    └──────────────────┘
```

## 🛠️ Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Setup pre-commit hooks
pre-commit install

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Celery Workers

```bash
# Start Celery worker
celery -A app.core.celery_app:celery_app worker --loglevel=info

# Start Celery beat scheduler
celery -A app.core.celery_app:celery_app beat --loglevel=info

# Monitor with Flower
celery -A app.core.celery_app:celery_app flower
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test suite
pytest tests/test_conversations.py

# Run Step 7 validation
python tests/test_step7_async_processing.py
```

## 📖 API Documentation

### Key Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/docs` | GET | Interactive API documentation |
| `/health` | GET | System health check |
| `/status` | GET | Detailed system status |
| `/api/v1/conversations/message` | POST | Process customer messages |
| `/api/v1/conversations/webhook-interaction` | POST | Handle webhook events |
| `/api/v1/conversations/tasks/{id}/status` | GET | Check task status |

### Example API Usage

#### Process Customer Message (Async)

```bash
curl -X POST "http://localhost:8000/api/v1/conversations/message" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_123",
    "message": "I'm interested in your products",
    "customer_id": "customer_456",
    "async_processing": true
  }'
```

Response:
```json
{
  "conversation_id": "pending",
  "response": "Message received and being processed",
  "status": "processing",
  "task_id": "async_task_789"
}
```

#### Check Task Status

```bash
curl "http://localhost:8000/api/v1/conversations/tasks/async_task_789/status"
```

Response:
```json
{
  "task_id": "async_task_789",
  "status": "SUCCESS",
  "progress": 100,
  "result": {
    "conversation_id": "conv_123",
    "ai_response": "I'd be happy to help you find the perfect product..."
  }
}
```

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build and deploy all services
./scripts/deploy.sh deploy

# Monitor services
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs

# Backup data
./scripts/deploy.sh backup
```

### Docker Compose Services

- **app**: Main FastAPI application
- **celery-worker**: Async task processing
- **celery-beat**: Scheduled task execution
- **redis**: Message broker and cache
- **postgres**: Structured data storage
- **mongodb**: Conversation and analytics storage
- **flower**: Task monitoring dashboard
- **nginx**: Load balancer (optional)

### Environment Configuration

Key environment variables:

```bash
# Application
APP_ENV=production
DEBUG=false
SECRET_KEY=your-production-secret-key

# Databases
POSTGRES_HOST=postgres
MONGO_HOST=mongodb
REDIS_HOST=redis

# Celery
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_MAX_TASKS_PER_CHILD=1000

# Monitoring
FLOWER_USER=admin
FLOWER_PASSWORD=secure_password
```

## 📊 Monitoring & Observability

### Application Metrics

- **Response Time**: API endpoint performance
- **Task Queue Health**: Celery worker status and queue depth
- **Error Rates**: Application and task failure rates
- **Conversation Metrics**: AI response quality and engagement

### Available Dashboards

1. **Flower Dashboard** (http://localhost:5555)
   - Celery task monitoring
   - Worker status and performance
   - Queue statistics

2. **API Documentation** (http://localhost:8000/docs)
   - Interactive API testing
   - Schema documentation
   - Authentication testing

3. **Health Checks** (http://localhost:8000/health)
   - System component status
   - Database connectivity
   - Service health metrics

### Logging

Structured JSON logging with rotation:

```bash
# Application logs
logs/app.log          # General application logs
logs/api.log          # API request/response logs
logs/tasks.log        # Celery task execution logs
logs/conversations.log # AI conversation logs
logs/performance.log  # Performance metrics
logs/error.log        # Error and exception logs
```

## 🔧 Configuration

### Core Settings

The application uses environment-based configuration. Key settings include:

| Setting | Description | Default |
|---------|-------------|---------|
| `APP_ENV` | Environment (development/production) | development |
| `DEBUG` | Enable debug mode | false |
| `API_HOST` | API server host | 0.0.0.0 |
| `API_PORT` | API server port | 8000 |
| `LOG_LEVEL` | Logging level | INFO |

### AI Configuration

| Setting | Description |
|---------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_MODEL` | AI model to use (gpt-4, gpt-3.5-turbo) |
| `OPENAI_MAX_TOKENS` | Maximum tokens per response |
| `OPENAI_TEMPERATURE` | AI creativity level (0-1) |

### Task Processing

| Setting | Description |
|---------|-------------|
| `CELERY_WORKER_CONCURRENCY` | Number of worker processes |
| `CELERY_TASK_TIME_LIMIT` | Task timeout (seconds) |
| `CELERY_WORKER_MAX_TASKS_PER_CHILD` | Tasks per worker restart |

## 🚦 Deployment Guide

### Production Checklist

- [ ] **Security**: Update all default passwords and secrets
- [ ] **SSL/TLS**: Configure HTTPS certificates
- [ ] **Firewall**: Restrict database access to application only
- [ ] **Monitoring**: Set up log aggregation and alerting
- [ ] **Backup**: Configure automated database backups
- [ ] **Scaling**: Configure load balancing for multiple instances

### Scaling Recommendations

**Small Deployment (< 1000 conversations/day)**
- 1 FastAPI instance
- 2 Celery workers
- Shared Redis/PostgreSQL/MongoDB

**Medium Deployment (< 10,000 conversations/day)**
- 2-3 FastAPI instances behind load balancer
- 4-6 Celery workers
- Dedicated database instances

**Large Deployment (> 10,000 conversations/day)**
- Auto-scaling FastAPI instances
- Celery worker auto-scaling based on queue depth
- Database clustering and read replicas
- Redis clustering for high availability

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Standards

- **Python**: Follow PEP 8 and use type hints
- **Testing**: Maintain >90% test coverage
- **Documentation**: Update docs for new features
- **Commits**: Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

1. **Documentation**: Check the `/docs` endpoint for API documentation
2. **Issues**: Open an issue on GitHub for bugs or feature requests
3. **Discussions**: Use GitHub Discussions for questions and community support

### Common Issues

**Q: Application won't start**
A: Check that all required environment variables are set in `.env` and that Docker services are running.

**Q: Tasks not processing**
A: Verify Redis is running and accessible. Check Celery worker logs with `docker-compose logs celery-worker`.

**Q: AI responses are poor quality**
A: Ensure you're using a capable model (gpt-4 recommended) and that your OpenAI API key has sufficient credits.

**Q: High memory usage**
A: Adjust `CELERY_WORKER_CONCURRENCY` and `CELERY_WORKER_MAX_TASKS_PER_CHILD` based on your server capacity.

---

## 🎯 Roadmap

### Upcoming Features

- [ ] **Voice Integration**: Voice message processing and response
- [ ] **Advanced Analytics**: Machine learning-based conversation insights
- [ ] **Multi-language Support**: International conversation handling
- [ ] **Custom AI Models**: Fine-tuned models for specific industries
- [ ] **Real-time Notifications**: WebSocket-based live updates
- [ ] **Advanced Security**: OAuth2, rate limiting, DDoS protection

### Version History

- **v1.0.0** (2025-07-15): Initial release with core features
  - AI conversation manipulation
  - Async task processing
  - Multi-platform webhooks
  - Comprehensive monitoring
  - Docker deployment

---

**Built with ❤️ by the ManipulatorAI Team**

*Transforming customer conversations through intelligent AI manipulation and seamless platform integration.*
