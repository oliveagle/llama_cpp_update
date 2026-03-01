#!/bin/bash
# Test script for RyzenAI backend

set -e

echo "========================================"
echo "RyzenAI Backend Test Suite"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Test 1: Check build
test_build() {
    info "Testing build..."
    cd src/ryzenai

    if make clean && make; then
        pass "Build successful"
    else
        fail "Build failed"
        return 1
    fi

    cd ../..
}

# Test 2: Check dependencies
test_dependencies() {
    info "Checking dependencies..."

    # Check libcurl
    if pkg-config --exists libcurl 2>/dev/null || dpkg -l libcurl4-openssl-dev 2>/dev/null | grep -q "^ii"; then
        pass "libcurl found"
    else
        fail "libcurl not found, install: sudo apt install libcurl4-openssl-dev"
    fi

    # Check libzip
    if pkg-config --exists libzip 2>/dev/null || dpkg -l libzip-dev 2>/dev/null | grep -q "^ii"; then
        pass "libzip found"
    else
        fail "libzip not found, install: sudo apt install libzip-dev"
    fi
}

# Test 3: Check NPU hardware
test_npu_hardware() {
    info "Checking NPU hardware..."

    # Check amdxdna driver
    if lsmod | grep -q amdxdna; then
        pass "amdxdna driver loaded"
    else
        fail "amdxdna driver not loaded"
    fi

    # Check NPU device
    if lspci | grep -q "1022:17f0\|1022:1502"; then
        pass "AMD NPU detected"
    else
        info "AMD NPU not detected (may not be present on this system)"
    fi

    # Check sysfs
    if [ -d /sys/class/accel ]; then
        pass "/sys/class/accel exists"

        for entry in /sys/class/accel/*; do
            if [ -d "$entry/device/driver" ]; then
                driver=$(readlink "$entry/device/driver" 2>/dev/null | xargs basename 2>/dev/null)
                if [ "$driver" = "amdxdna" ]; then
                    pass "NPU using amdxdna driver"

                    # Read NPU info
                    if [ -f "$entry/device/vbnv" ]; then
                        vbnv=$(cat "$entry/device/vbnv" 2>/dev/null)
                        info "NPU: $vbnv"
                    fi
                fi
            fi
        done
    else
        info "/sys/class/accel not found"
    fi
}

# Test 4: Check kernel version
test_kernel_version() {
    info "Checking kernel version..."

    kernel=$(uname -r)
    info "Kernel: $kernel"

    # Extract major version
    major=$(echo "$kernel" | cut -d'.' -f1)
    minor=$(echo "$kernel" | cut -d'.' -f2)

    if [ "$major" -gt 7 ] || { [ "$major" -eq 6 ] && [ "$minor" -ge 8 ]; }; then
        pass "Kernel version meets RyzenAI requirements (≥6.8)"
    else
        fail "Kernel version too old for RyzenAI (need ≥6.8)"
    fi
}

# Test 5: Download ryzenai-server (optional)
test_download() {
    if [ "$1" = "--download" ]; then
        info "Testing ryzenai-server download..."

        # This would require the actual llama-server binary
        # Skip for now
        info "Download test skipped (requires full build)"
    fi
}

# Run tests
echo "Running tests..."
echo ""

test_dependencies
echo ""

test_build
echo ""

test_npu_hardware
echo ""

test_kernel_version
echo ""

test_download "$@"
echo ""

# Summary
echo "========================================"
echo "Test Summary"
echo "========================================"
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed${NC}"
    exit 1
fi
