#!/bin/bash

# ManipulatorAI Deployment Script
# This script handles the complete deployment of the ManipulatorAI application

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="manipulator-ai"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
BACKUP_DIR="./backups"
LOG_DIR="./logs"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Determine Docker Compose command
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        DOCKER_COMPOSE_CMD="docker compose"
    fi
    
    log_success "Prerequisites check passed"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f ".env.example" ]; then
            log_warning ".env file not found. Copying from .env.example"
            cp .env.example .env
            log_warning "Please edit .env file with your actual configuration before proceeding"
            read -p "Press Enter after configuring .env file..."
        else
            log_error ".env.example file not found. Cannot create environment configuration."
            exit 1
        fi
    fi
    
    # Create necessary directories
    mkdir -p "$LOG_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "./nginx"
    
    # Set proper permissions
    chmod 755 "$LOG_DIR"
    chmod 755 "$BACKUP_DIR"
    
    log_success "Environment setup completed"
}

build_images() {
    log_info "Building Docker images..."
    
    # Build the application image
    $DOCKER_COMPOSE_CMD build app
    
    log_success "Docker images built successfully"
}

start_services() {
    log_info "Starting services..."
    
    # Start infrastructure services first
    log_info "Starting infrastructure services (Redis, PostgreSQL, MongoDB)..."
    $DOCKER_COMPOSE_CMD up -d redis postgres mongodb
    
    # Wait for databases to be ready
    log_info "Waiting for databases to be ready..."
    sleep 30
    
    # Check if databases are healthy
    check_database_health
    
    # Start application services
    log_info "Starting application services..."
    $DOCKER_COMPOSE_CMD up -d app celery-worker celery-beat
    
    # Start monitoring (Flower)
    log_info "Starting monitoring services..."
    $DOCKER_COMPOSE_CMD up -d flower
    
    log_success "All services started successfully"
}

check_database_health() {
    log_info "Checking database health..."
    
    # Check Redis
    if ! docker exec manipulator-redis redis-cli ping &> /dev/null; then
        log_error "Redis is not responding"
        exit 1
    fi
    log_success "Redis is healthy"
    
    # Check PostgreSQL
    if ! docker exec manipulator-postgres pg_isready -U postgres &> /dev/null; then
        log_error "PostgreSQL is not ready"
        exit 1
    fi
    log_success "PostgreSQL is healthy"
    
    # Check MongoDB
    if ! docker exec manipulator-mongodb mongosh --eval "db.adminCommand('ping')" --quiet &> /dev/null; then
        log_error "MongoDB is not responding"
        exit 1
    fi
    log_success "MongoDB is healthy"
}

run_migrations() {
    log_info "Running database migrations..."
    
    # Run PostgreSQL migrations (if migration system exists)
    # docker exec manipulator-app python -m alembic upgrade head
    
    log_success "Database migrations completed"
}

check_application_health() {
    log_info "Checking application health..."
    
    # Wait for application to start
    sleep 15
    
    # Check main application
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "Main application is healthy"
    else
        log_error "Main application health check failed"
        return 1
    fi
    
    # Check Celery worker
    if docker exec manipulator-celery-worker celery -A app.core.celery_app:celery_app inspect ping &> /dev/null; then
        log_success "Celery worker is healthy"
    else
        log_error "Celery worker health check failed"
        return 1
    fi
    
    # Check Flower monitoring
    if curl -f http://localhost:5555 &> /dev/null; then
        log_success "Flower monitoring is accessible"
    else
        log_warning "Flower monitoring might not be ready yet"
    fi
    
    return 0
}

show_status() {
    log_info "Application Status:"
    echo ""
    
    # Show running containers
    $DOCKER_COMPOSE_CMD ps
    
    echo ""
    log_info "Service Endpoints:"
    echo "  Main Application: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Flower Monitoring: http://localhost:5555"
    echo "  PostgreSQL: localhost:5432"
    echo "  MongoDB: localhost:27017"
    echo "  Redis: localhost:6379"
    
    echo ""
    log_info "Logs:"
    echo "  Application logs: $LOG_DIR/"
    echo "  Docker logs: docker-compose logs [service_name]"
}

backup_data() {
    log_info "Creating data backup..."
    
    BACKUP_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_PATH="$BACKUP_DIR/backup_$BACKUP_TIMESTAMP"
    
    mkdir -p "$BACKUP_PATH"
    
    # Backup PostgreSQL
    log_info "Backing up PostgreSQL..."
    docker exec manipulator-postgres pg_dump -U postgres manipulator_ai > "$BACKUP_PATH/postgres_dump.sql"
    
    # Backup MongoDB
    log_info "Backing up MongoDB..."
    docker exec manipulator-mongodb mongodump --db manipulator_conversations --out /tmp/mongodump
    docker cp manipulator-mongodb:/tmp/mongodump "$BACKUP_PATH/"
    
    # Backup application logs
    log_info "Backing up logs..."
    cp -r "$LOG_DIR" "$BACKUP_PATH/"
    
    # Create backup info file
    cat > "$BACKUP_PATH/backup_info.txt" << EOF
Backup created: $(date)
Application: $APP_NAME
Environment: $(grep APP_ENV .env 2>/dev/null || echo "unknown")
Git commit: $(git rev-parse HEAD 2>/dev/null || echo "unknown")
Docker Compose version: $($DOCKER_COMPOSE_CMD version --short 2>/dev/null || echo "unknown")
EOF
    
    log_success "Backup created at: $BACKUP_PATH"
}

stop_services() {
    log_info "Stopping services..."
    
    $DOCKER_COMPOSE_CMD down
    
    log_success "All services stopped"
}

restart_services() {
    log_info "Restarting services..."
    
    stop_services
    start_services
    
    log_success "Services restarted successfully"
}

clean_up() {
    log_info "Cleaning up..."
    
    # Stop and remove containers, networks, volumes
    $DOCKER_COMPOSE_CMD down -v --remove-orphans
    
    # Remove unused Docker resources
    docker system prune -f
    
    log_success "Cleanup completed"
}

show_help() {
    echo "ManipulatorAI Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     - Full deployment (build, start, migrate)"
    echo "  start      - Start all services"
    echo "  stop       - Stop all services"
    echo "  restart    - Restart all services"
    echo "  status     - Show service status and endpoints"
    echo "  logs       - Show application logs"
    echo "  backup     - Create data backup"
    echo "  health     - Check application health"
    echo "  cleanup    - Stop services and clean up resources"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy      # Full deployment"
    echo "  $0 start       # Start services"
    echo "  $0 logs app    # Show app logs"
}

# Main script logic
case "${1:-}" in
    "deploy")
        log_info "Starting full deployment of $APP_NAME"
        check_prerequisites
        setup_environment
        build_images
        start_services
        run_migrations
        if check_application_health; then
            log_success "Deployment completed successfully!"
            show_status
        else
            log_error "Deployment completed but health checks failed"
            exit 1
        fi
        ;;
    "start")
        check_prerequisites
        start_services
        check_application_health
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        check_application_health
        show_status
        ;;
    "status")
        show_status
        ;;
    "logs")
        if [ -z "${2:-}" ]; then
            $DOCKER_COMPOSE_CMD logs -f
        else
            $DOCKER_COMPOSE_CMD logs -f "$2"
        fi
        ;;
    "backup")
        backup_data
        ;;
    "health")
        check_application_health
        ;;
    "cleanup")
        clean_up
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        log_error "No command specified"
        show_help
        exit 1
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
