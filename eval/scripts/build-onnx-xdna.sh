#!/bin/bash
# ONNX Runtime with XDNA EP 编译脚本
# 在 AMD XDNA2 NPU 上编译 ONNX Runtime

set -e

# 配置
ORT_SRC="$HOME/build/onnxruntime-xdna"
BUILD_DIR="$HOME/build/onnxruntime-xdna-build"
INSTALL_DIR="$HOME/build/onnxruntime-xdna-install"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# 检查依赖
check_deps() {
    log_info "Checking dependencies..."

    # 检查 CMake
    if ! command -v cmake &> /dev/null; then
        log_error "CMake not found"
        log_info "Install with: sudo apt install cmake"
        return 1
    fi

    # 检查 Git
    if ! command -v git &> /dev/null; then
        log_error "Git not found"
        log_info "Install with: sudo apt install git"
        return 1
    fi

    # 检查 Python 3
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found"
        return 1
    fi

    # 检查 C++ 编译器
    if ! command -v g++ &> /dev/null; then
        log_error "g++ not found"
        log_info "Install with: sudo apt install g++"
        return 1
    fi

    log_success "Dependencies OK"
}

# 克隆源码
clone_source() {
    log_info "Checking ONNX Runtime source..."

    if [ ! -d "$ORT_SRC" ]; then
        log_info "Cloning ONNX Runtime from GitHub..."
        mkdir -p "$(dirname "$ORT_SRC")"
        git clone --recursive https://github.com/microsoft/onnxruntime.git "$ORT_SRC"
        log_success "Source cloned to $ORT_SRC"
    else
        log_info "Source already exists: $ORT_SRC"
        log_info "Updating submodules..."
        cd "$ORT_SRC"
        git submodule update --init --recursive
    fi
}

# 配置 CMake
configure_cmake() {
    log_info "Configuring CMake with XDNA EP..."

    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"

    # CMake 配置命令（使用绝对路径）
    cmake -G "Unix Makefiles" \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
        -Donnxruntime_USE_VITISAI=ON \
        -Donnxruntime_USE_OPENMP=ON \
        -Donnxruntime_ENABLE_PYTHON=ON \
        -DBUILD_SHARED_LIBS=ON \
        "$ORT_SRC" 2>&1 | tee "$BUILD_DIR/cmake-configure.log"

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "CMake configuration successful"
    else
        log_error "CMake configuration failed"
        log_info "Check log: $BUILD_DIR/cmake-configure.log"
        return 1
    fi
}

# 编译
build() {
    log_info "Building ONNX Runtime (this may take a while)..."

    cd "$BUILD_DIR"

    # 编译命令（使用所有 CPU 核心）
    NUM_CORES=$(nproc)
    log_info "Using $NUM_CORES parallel jobs"

    make -j$NUM_CORES 2>&1 | tee "$BUILD_DIR/build.log"

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Build successful"
    else
        log_error "Build failed"
        log_info "Check log: $BUILD_DIR/build.log"
        return 1
    fi
}

# 安装
install() {
    log_info "Installing ONNX Runtime..."

    cd "$BUILD_DIR"
    make install 2>&1 | tee "$BUILD_DIR/install.log"

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Installation successful"
        log_info "Installed to: $INSTALL_DIR"
    else
        log_error "Installation failed"
        return 1
    fi
}

# 验证安装
verify() {
    log_info "Verifying installation..."

    # 检查库文件
    if [ ! -f "$INSTALL_DIR/lib/libonnxruntime.so" ] && \
       [ ! -f "$INSTALL_DIR/lib64/libonnxruntime.so" ]; then
        log_error "libonnxruntime.so not found"
        return 1
    fi

    # 检查 Python 绑定
    PYTHON_LIB_DIR="$INSTALL_DIR/lib/python3.12/site-packages"
    if [ -d "$PYTHON_LIB_DIR" ]; then
        log_info "Python bindings found: $PYTHON_LIB_DIR"
        export PYTHONPATH="$PYTHON_LIB_DIR:$PYTHONPATH"
    else
        log_warning "Python bindings not found"
    fi

    log_success "Installation verified"
}

# 测试
test() {
    log_info "Testing ONNX Runtime..."

    python3 -c "
import sys
sys.path.insert(0, '$INSTALL_DIR/lib/python3.12/site-packages')
try:
    import onnxruntime as ort
    print('ONNX Runtime imported successfully')
    print(f'Version: {ort.__version__}')
    print(f'Available EPs: {ort.get_available_providers()}')
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"

    if [ $? -eq 0 ]; then
        log_success "Test passed"
    else
        log_error "Test failed"
        return 1
    fi
}

# 清理
clean() {
    log_info "Cleaning build directory..."
    rm -rf "$BUILD_DIR"
    rm -rf "$INSTALL_DIR"
    log_success "Clean complete"
}

# 显示帮助
usage() {
    cat << EOF
Usage: $0 <command> [options]

Commands:
  clone     Clone ONNX Runtime source
  config    Run CMake configuration
  build     Build ONNX Runtime
  install   Install ONNX Runtime
  verify    Verify installation
  test      Test installation
  clean     Clean build directory
  all       Run all steps (clone, config, build, install, verify, test)

Options:
  --clean    Clean before starting

Examples:
  # Complete build
  $0 all

  # Step by step
  $0 clone
  $0 config
  $0 build
  $0 install
  $0 verify
  $0 test

  # Clean and rebuild
  $0 clean
  $0 all

Configuration:
  Source:  $ORT_SRC
  Build:    $BUILD_DIR
  Install:  $INSTALL_DIR

EOF
}

# 主函数
main() {
    check_deps || exit 1

    case "${1:-}" in
        clone)
            clone_source
            ;;
        config)
            configure_cmake
            ;;
        build)
            build
            ;;
        install)
            install
            ;;
        verify)
            verify
            ;;
        test)
            test
            ;;
        clean)
            clean
            ;;
        all)
            clone_source
            configure_cmake || exit 1
            build || exit 1
            install || exit 1
            verify
            test
            log_success "Build complete!"
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            usage
            exit 1
            ;;
    esac
}

main "$@"
