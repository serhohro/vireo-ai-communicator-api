#!/bin/bash
# ============================================================
# Vireo Docker Deployment Script
# ============================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="vireo"
REGISTRY="${DOCKER_REGISTRY:-}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
COMPOSE_FILE="docker/docker-compose.yml"

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

# Show help
show_help() {
    cat << EOF
Vireo Docker Deployment Script

Usage: ./deploy_docker.sh [COMMAND] [OPTIONS]

Commands:
    build       Build Docker images
    push        Push images to registry
    start       Start services
    stop        Stop services
    restart     Restart services
    status      Show service status
    logs        Show logs
    clean       Clean containers, images, and volumes
    shell       Open shell in a container
    test        Run tests in containers
    all         Build, push, and deploy

Options:
    -e, --env ENV          Set environment (dev, staging, production)
    -t, --tag TAG          Set image tag (default: latest)
    -r, --registry URL     Set registry URL
    -s, --service SERVICE  Target specific service
    -h, --help             Show this help

Examples:
    ./deploy_docker.sh build -t v3.0.0
    ./deploy_docker.sh start -e production
    ./deploy_docker.sh logs -s vireo-api
EOF
}

# Parse arguments
ENVIRONMENT="development"
SERVICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        build|push|start|stop|restart|status|logs|clean|shell|test|all)
            COMMAND=$1
            shift
            ;;
        -e|--env)
            ENVIRONMENT=$2
            shift 2
            ;;
        -t|--tag)
            IMAGE_TAG=$2
            shift 2
            ;;
        -r|--registry)
            REGISTRY=$2
            shift 2
            ;;
        -s|--service)
            SERVICE=$2
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate environment
case $ENVIRONMENT in
    development|dev)
        ENV_FILE=".env.dev"
        COMPOSE_FLAGS=""
        ;;
    staging|stage)
        ENV_FILE=".env.staging"
        COMPOSE_FLAGS="-f docker/docker-compose.yml -f docker/docker-compose.staging.yml"
        ;;
    production|prod)
        ENV_FILE=".env.production"
        COMPOSE_FLAGS="-f docker/docker-compose.yml -f docker/docker-compose.prod.yml"
        ;;
    *)
        log_error "Invalid environment: $ENVIRONMENT"
        exit 1
        ;;
esac

# Set compose command
COMPOSE_CMD="docker-compose --project-name ${PROJECT_NAME} --env-file ${ENV_FILE} ${COMPOSE_FLAGS}"

# Build function
build_images() {
    log_info "Building Docker images..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Tag: $IMAGE_TAG"
    
    # Build API image
    log_info "Building Python API image..."
    docker build \
        -f docker/Dockerfile.python \
        -t "${REGISTRY}${PROJECT_NAME}-api:${IMAGE_TAG}" \
        -t "${REGISTRY}${PROJECT_NAME}-api:latest" \
        .
    
    # Build Rust image
    log_info "Building Rust image..."
    docker build \
        -f docker/Dockerfile.rust \
        -t "${REGISTRY}${PROJECT_NAME}-rust:${IMAGE_TAG}" \
        -t "${REGISTRY}${PROJECT_NAME}-rust:latest" \
        .
    
    # Build WASM image
    log_info "Building WASM image..."
    docker build \
        -f docker/Dockerfile.wasm \
        -t "${REGISTRY}${PROJECT_NAME}-wasm:${IMAGE_TAG}" \
        -t "${REGISTRY}${PROJECT_NAME}-wasm:latest" \
        .
    
    log_success "All images built successfully"
}

# Push function
push_images() {
    if [[ -z "$REGISTRY" ]]; then
        log_warning "No registry specified, skipping push"
        return
    fi
    
    log_info "Pushing images to registry: $REGISTRY"
    
    docker push "${REGISTRY}${PROJECT_NAME}-api:${IMAGE_TAG}"
    docker push "${REGISTRY}${PROJECT_NAME}-api:latest"
    docker push "${REGISTRY}${PROJECT_NAME}-rust:${IMAGE_TAG}"
    docker push "${REGISTRY}${PROJECT_NAME}-rust:latest"
    docker push "${REGISTRY}${PROJECT_NAME}-wasm:${IMAGE_TAG}"
    docker push "${REGISTRY}${PROJECT_NAME}-wasm:latest"
    
    log_success "All images pushed successfully"
}

# Start function
start_services() {
    log_info "Starting services..."
    log_info "Environment: $ENVIRONMENT"
    
    # Check if .env file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_warning "Environment file $ENV_FILE not found, creating from template"
        cp .env.example "$ENV_FILE"
    fi
    
    # Start services
    if [[ -n "$SERVICE" ]]; then
        $COMPOSE_CMD up -d "$SERVICE"
    else
        $COMPOSE_CMD up -d
    fi
    
    # Check status
    sleep 3
    $COMPOSE_CMD ps
    
    log_success "Services started successfully"
}

# Stop function
stop_services() {
    log_info "Stopping services..."
    
    if [[ -n "$SERVICE" ]]; then
        $COMPOSE_CMD stop "$SERVICE"
    else
        $COMPOSE_CMD stop
    fi
    
    log_success "Services stopped"
}

# Restart function
restart_services() {
    log_info "Restarting services..."
    stop_services
    start_services
}

# Status function
show_status() {
    log_info "Service status:"
    $COMPOSE_CMD ps
}

# Logs function
show_logs() {
    if [[ -n "$SERVICE" ]]; then
        $COMPOSE_CMD logs -f "$SERVICE"
    else
        $COMPOSE_CMD logs -f
    fi
}

# Clean function
clean_all() {
    log_warning "This will remove containers, images, and volumes"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Clean cancelled"
        return
    fi
    
    log_info "Cleaning up..."
    $COMPOSE_CMD down -v --rmi all
    docker system prune -f
    
    log_success "Clean complete"
}

# Shell function
open_shell() {
    local service="${SERVICE:-vireo-api}"
    log_info "Opening shell in $service"
    $COMPOSE_CMD exec "$service" /bin/sh
}

# Test function
run_tests() {
    log_info "Running tests in containers..."
    
    # Run Python tests
    log_info "Running Python tests..."
    $COMPOSE_CMD run --rm vireo-api pytest tests/ -v
    
    # Run Rust tests
    log_info "Running Rust tests..."
    $COMPOSE_CMD run --rm vireo-rust cargo test
    
    # Run TypeScript tests
    log_info "Running TypeScript tests..."
    $COMPOSE_CMD run --rm vireo-wasm npm test
    
    log_success "All tests passed"
}

# All function (build, push, deploy)
do_all() {
    build_images
    push_images
    start_services
    show_status
}

# Main command dispatcher
case $COMMAND in
    build)
        build_images
        ;;
    push)
        push_images
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    clean)
        clean_all
        ;;
    shell)
        open_shell
        ;;
    test)
        run_tests
        ;;
    all)
        do_all
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac

log_success "Deployment script completed successfully"