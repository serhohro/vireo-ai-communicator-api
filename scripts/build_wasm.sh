#!/bin/bash
# ============================================================
# Vireo WASM Build Script
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
WASM_TARGET="${WASM_TARGET:-wasm32-wasi}"
WASM_OPTIMIZE="${WASM_OPTIMIZE:-3}"
OUTPUT_DIR="target/wasm"
SOURCE_DIR="sdk/rust"

# Help
show_help() {
    cat << EOF
Vireo WASM Build Script

Usage: ./build_wasm.sh [COMMAND] [OPTIONS]

Commands:
    build       Build WASM module
    optimize    Optimize WASM module
    test        Run WASM tests
    clean       Clean build artifacts
    serve       Serve WASM for testing
    all         Build, test, and optimize

Options:
    -t, --target TARGET    Set WASM target (wasm32-wasi, wasm32-unknown-unknown)
    -o, --optimize LEVEL   Set optimization level (0-3)
    -r, --release          Build in release mode
    -h, --help            Show this help

Examples:
    ./build_wasm.sh build --release
    ./build_wasm.sh serve
EOF
}

# Parse arguments
COMMAND="build"
RELEASE=false
WASM_TARGET="wasm32-wasi"
OPT_LEVEL=3

while [[ $# -gt 0 ]]; do
    case $1 in
        build|optimize|test|clean|serve|all)
            COMMAND=$1
            shift
            ;;
        -t|--target)
            WASM_TARGET=$2
            shift 2
            ;;
        -o|--optimize)
            OPT_LEVEL=$2
            shift 2
            ;;
        -r|--release)
            RELEASE=true
            shift
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
    
    # Check Rust
    if ! command -v rustc &> /dev/null; then
        log_error "Rust not found. Please install Rust: https://rustup.rs/"
        exit 1
    fi
    
    # Check wasm target
    if ! rustup target list | grep -q "$WASM_TARGET (installed)"; then
        log_info "Installing WASM target: $WASM_TARGET"
        rustup target add "$WASM_TARGET"
    fi
    
    # Check wasm-pack
    if ! command -v wasm-pack &> /dev/null; then
        log_info "Installing wasm-pack..."
        cargo install wasm-pack
    fi
    
    # Check wasm-bindgen
    if ! command -v wasm-bindgen &> /dev/null; then
        log_info "Installing wasm-bindgen..."
        cargo install wasm-bindgen-cli
    fi
    
    # Check wasm-opt (binaryen)
    if ! command -v wasm-opt &> /dev/null; then
        log_warning "wasm-opt not found. Install binaryen for optimization."
        log_info "  brew install binaryen (macOS)"
        log_info "  apt-get install binaryen (Ubuntu)"
        log_info "  or install from: https://github.com/WebAssembly/binaryen"
    fi
    
    log_success "Prerequisites satisfied"
}

# Build WASM
build_wasm() {
    log_info "Building WASM module..."
    log_info "Target: $WASM_TARGET"
    log_info "Release: $RELEASE"
    
    mkdir -p "$OUTPUT_DIR"
    
    # Build using wasm-pack
    if [ "$RELEASE" = true ]; then
        BUILD_FLAG="--release"
        TARGET_DIR="target/wasm32-wasi/release"
    else
        BUILD_FLAG=""
        TARGET_DIR="target/wasm32-wasi/debug"
    fi
    
    cd "$SOURCE_DIR"
    
    wasm-pack build \
        --target web \
        --out-dir "../../$OUTPUT_DIR" \
        --out-name vireo_wasm \
        $BUILD_FLAG
    
    cd ../..
    
    # Copy additional files
    cp "$OUTPUT_DIR/vireo_wasm_bg.wasm" "$OUTPUT_DIR/vireo.wasm"
    cp "$OUTPUT_DIR/vireo_wasm.js" "$OUTPUT_DIR/vireo.js"
    cp "$OUTPUT_DIR/vireo_wasm.d.ts" "$OUTPUT_DIR/vireo.d.ts"
    
    # Get file size
    WASM_SIZE=$(du -h "$OUTPUT_DIR/vireo.wasm" | cut -f1)
    
    log_success "WASM build complete"
    log_info "  Size: $WASM_SIZE"
    log_info "  Output: $OUTPUT_DIR/"
}

# Optimize WASM
optimize_wasm() {
    log_info "Optimizing WASM module..."
    
    if ! command -v wasm-opt &> /dev/null; then
        log_warning "wasm-opt not found, skipping optimization"
        return
    fi
    
    INPUT="$OUTPUT_DIR/vireo.wasm"
    OUTPUT="$OUTPUT_DIR/vireo.opt.wasm"
    
    wasm-opt "$INPUT" \
        -O$OPT_LEVEL \
        --enable-bulk-memory \
        --enable-simd \
        --enable-threads \
        -o "$OUTPUT"
    
    # Replace with optimized version
    mv "$OUTPUT" "$INPUT"
    
    # Get new size
    WASM_SIZE=$(du -h "$INPUT" | cut -f1)
    
    log_success "Optimization complete"
    log_info "  Optimized size: $WASM_SIZE"
}

# Run tests
test_wasm() {
    log_info "Running WASM tests..."
    
    cd "$SOURCE_DIR"
    
    # Run Rust tests
    cargo test --target "$WASM_TARGET"
    
    # Run wasm-pack tests
    wasm-pack test --node
    
    cd ../..
    
    log_success "All tests passed"
}

# Clean artifacts
clean_wasm() {
    log_info "Cleaning WASM build artifacts..."
    
    rm -rf "$OUTPUT_DIR"
    cd "$SOURCE_DIR"
    cargo clean
    cd ../..
    
    log_success "Clean complete"
}

# Serve for testing
serve_wasm() {
    log_info "Starting WASM test server..."
    
    # Check if we have a web server
    if command -v python3 &> /dev/null; then
        log_info "Starting Python HTTP server..."
        cd "$OUTPUT_DIR"
        python3 -m http.server 8080
    elif command -v node &> /dev/null; then
        log_info "Starting Node.js http-server..."
        npx -y http-server "$OUTPUT_DIR" -p 8080
    else
        log_error "No web server found. Install Python or Node.js."
        exit 1
    fi
}

# Do everything
do_all() {
    check_prerequisites
    clean_wasm
    build_wasm
    test_wasm
    optimize_wasm
    log_success "WASM build complete! 🚀"
}

# Main dispatch
case $COMMAND in
    build)
        check_prerequisites
        build_wasm
        ;;
    optimize)
        optimize_wasm
        ;;
    test)
        check_prerequisites
        test_wasm
        ;;
    clean)
        clean_wasm
        ;;
    serve)
        serve_wasm
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