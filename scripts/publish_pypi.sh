#!/bin/bash
# ============================================================
# Vireo PyPI Publishing Script
# ============================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✅${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}❌${NC} $1"; }

# Configuration
PACKAGE_NAME="vireo-ai"
PYPI_REPO="${PYPI_REPO:-pypi}"  # pypi or testpypi
VERSION=""
BUILD_DIR="dist"
WHEEL_DIR="wheelhouse"

# Help
show_help() {
    cat << EOF
Vireo PyPI Publishing Script

Usage: ./publish_pypi.sh [COMMAND] [OPTIONS]

Commands:
    build       Build distribution packages
    test        Test build (upload to test.pypi.org)
    publish     Publish to PyPI
    all         Build, test, and publish
    version     Show current version
    clean       Clean build artifacts

Options:
    -v, --version VERSION   Set package version
    -r, --repo REPO         Set PyPI repo (pypi, testpypi)
    -h, --help             Show this help

Examples:
    ./publish_pypi.sh build --version 3.0.0
    ./publish_pypi.sh test
    ./publish_pypi.sh publish
EOF
}

# Parse arguments
COMMAND=""

while [[ $# -gt 0 ]]; do
    case $1 in
        build|test|publish|all|version|clean)
            COMMAND=$1
            shift
            ;;
        -v|--version)
            VERSION=$2
            shift 2
            ;;
        -r|--repo)
            PYPI_REPO=$2
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 not found"
        exit 1
    fi
    
    # Check build tools
    if ! python3 -c "import build" &> /dev/null; then
        log_info "Installing build tools..."
        pip3 install build twine wheel
    fi
    
    # Check twine
    if ! command -v twine &> /dev/null; then
        log_info "Installing twine..."
        pip3 install twine
    fi
    
    log_success "Prerequisites satisfied"
}

# Get current version
get_version() {
    if [[ -f "pyproject.toml" ]]; then
        VERSION=$(grep -oP 'version\s*=\s*"\K[^"]+' pyproject.toml | head -1)
    elif [[ -f "setup.py" ]]; then
        VERSION=$(grep -oP 'version\s*=\s*["\']\K[^"\']+' setup.py | head -1)
    else
        VERSION="unknown"
    fi
    echo "$VERSION"
}

# Update version
update_version() {
    local new_version="$1"
    if [[ -z "$new_version" ]]; then
        return
    fi
    
    log_info "Updating version to $new_version"
    
    # Update pyproject.toml
    if [[ -f "pyproject.toml" ]]; then
        sed -i.bak "s/version = \".*\"/version = \"$new_version\"/" pyproject.toml
        rm -f pyproject.toml.bak
    fi
    
    # Update setup.py
    if [[ -f "setup.py" ]]; then
        sed -i.bak "s/version='.*'/version='$new_version'/" setup.py
        rm -f setup.py.bak
    fi
    
    # Update __init__.py
    if [[ -f "core/__init__.py" ]]; then
        sed -i.bak "s/__version__ = \".*\"/__version__ = \"$new_version\"/" core/__init__.py
        rm -f core/__init__.py.bak
    fi
    
    # Update api/__init__.py
    if [[ -f "api/__init__.py" ]]; then
        sed -i.bak "s/__version__ = \".*\"/__version__ = \"$new_version\"/" api/__init__.py
        rm -f api/__init__.py.bak
    fi
    
    log_success "Version updated to $new_version"
}

# Build packages
build_packages() {
    log_info "Building distribution packages..."
    
    # Clean previous builds
    clean_artifacts
    
    # Update version if specified
    if [[ -n "$VERSION" ]]; then
        update_version "$VERSION"
    fi
    
    # Build using build
    python3 -m build
    
    log_success "Build complete"
    log_info "  Source distribution: $(ls $BUILD_DIR/*.tar.gz 2>/dev/null)"
    log_info "  Wheel: $(ls $BUILD_DIR/*.whl 2>/dev/null)"
}

# Test build (upload to testpypi)
test_publish() {
    log_info "Testing package on test.pypi.org..."
    
    # Check if packages exist
    if [[ -z "$(ls -A $BUILD_DIR/*.tar.gz 2>/dev/null)" ]]; then
        log_error "No packages found. Run 'build' first."
        exit 1
    fi
    
    # Upload to test.pypi.org
    twine upload --repository testpypi "$BUILD_DIR"/*
    
    log_success "Test upload complete"
    log_info "  Check at: https://test.pypi.org/project/$PACKAGE_NAME/"
    log_warning "  To install: pip install --index-url https://test.pypi.org/simple/ $PACKAGE_NAME"
}

# Publish to PyPI
publish_pypi() {
    log_info "Publishing to PyPI..."
    
    # Check if packages exist
    if [[ -z "$(ls -A $BUILD_DIR/*.tar.gz 2>/dev/null)" ]]; then
        log_error "No packages found. Run 'build' first."
        exit 1
    fi
    
    # Check for API key
    if [[ -z "$PYPI_API_KEY" ]]; then
        log_warning "PYPI_API_KEY environment variable not set"
        log_info "Using interactive login..."
    fi
    
    # Upload to PyPI
    if [[ -n "$PYPI_API_KEY" ]]; then
        twine upload --repository "$PYPI_REPO" "$BUILD_DIR"/* --password "$PYPI_API_KEY"
    else
        twine upload --repository "$PYPI_REPO" "$BUILD_DIR"/*
    fi
    
    log_success "Published to PyPI successfully!"
    log_info "  Package: $PACKAGE_NAME"
    log_info "  Version: $(get_version)"
    log_info "  PyPI: https://pypi.org/project/$PACKAGE_NAME/"
}

# Clean artifacts
clean_artifacts() {
    log_info "Cleaning build artifacts..."
    
    rm -rf "$BUILD_DIR"
    rm -rf "$WHEEL_DIR"
    rm -rf *.egg-info
    rm -rf .pytest_cache
    rm -rf .coverage
    rm -rf htmlcov
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    log_success "Clean complete"
}

# Show version
show_version() {
    local ver=$(get_version)
    log_info "Current version: $ver"
}

# Do everything
do_all() {
    check_prerequisites
    build_packages
    test_publish
    read -p "Continue with production publish? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        publish_pypi
    else
        log_info "Publish cancelled"
    fi
}

# Main dispatch
case $COMMAND in
    build)
        check_prerequisites
        build_packages
        ;;
    test)
        check_prerequisites
        test_publish
        ;;
    publish)
        check_prerequisites
        publish_pypi
        ;;
    all)
        do_all
        ;;
    version)
        show_version
        ;;
    clean)
        clean_artifacts
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac