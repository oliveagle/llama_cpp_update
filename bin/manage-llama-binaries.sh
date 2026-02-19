#!/bin/bash
# llama.cpp Binary Management System
# Manages different backend builds with version tracking

LLAMA_BASE="${HOME}/opt/llama.cpp"
VERSIONS_FILE="${LLAMA_BASE}/.versions"

# Get git commit hash for version
get_version() {
    cd "${LLAMA_BASE}" && git rev-parse --short HEAD 2>/dev/null || echo "unknown"
}

# List available binaries
list_binaries() {
    echo "Available llama-server binaries:"
    echo "================================"
    for binary in "${LLAMA_BASE}"/build*/bin/llama-server; do
        if [ -f "$binary" ]; then
            backend=$(echo "$binary" | grep -oE 'build-[^/]+' | sed 's/build-//' || echo "default")
            version=$($binary --version 2>&1 | grep "version" | head -1 | awk '{print $3}' || echo "unknown")
            cuda_support=$($binary --help 2>&1 | grep -i cuda >/dev/null && echo "✓ CUDA" || echo "✗ CUDA")
            vulkan_support=$($binary --help 2>&1 | grep -i vulkan >/dev/null && echo "✓ Vulkan" || echo "✗ Vulkan")
            printf "  %-15s | %-8s | %-8s | %s\n" "$backend" "$version" "$cuda_support" "$vulkan_support"
        fi
    done
}

# Create symlink for active binary
set_active() {
    local backend=$1
    local binary_path="${LLAMA_BASE}/build${backend:+-${backend}}/bin/llama-server"
    
    if [ ! -f "$binary_path" ]; then
        echo "Error: Binary not found: $binary_path"
        echo "Available backends:"
        ls -1 "${LLAMA_BASE}"/build*/bin/llama-server 2>/dev/null | grep -oE 'build-[^/]+' | sed 's/build-//' || echo "  (none)"
        return 1
    fi
    
    ln -sf "$binary_path" "${LLAMA_BASE}/bin/llama-server-active"
    echo "Active binary set to: $backend ($(get_version))"
    echo "$backend:$(get_version):$(date +%Y-%m-%d_%H%M%S)" >> "$VERSIONS_FILE"
}

# Get active binary info
get_active() {
    if [ -L "${LLAMA_BASE}/bin/llama-server-active" ]; then
        readlink -f "${LLAMA_BASE}/bin/llama-server-active"
    else
        echo "No active binary set"
        return 1
    fi
}

# Show help
show_help() {
    cat << EOF
Usage: manage-llama-binaries.sh [command] [args]

Commands:
  list              List all available binaries
  use <backend>    Set active binary (cuda, vulkan, hip, or default)
  active            Show currently active binary
  version           Show version history
  help              Show this help

Backends:
  cuda     - CUDA backend (for NVIDIA GPUs)
  vulkan   - Vulkan backend (cross-platform)
  hip      - ROCm/HIP backend (for AMD GPUs)
  default  - CPU-only or auto-detected backend

Examples:
  manage-llama-binaries.sh list
  manage-llama-binaries.sh use cuda
  manage-llama-binaries.sh active
EOF
}

# Main
case "${1:-help}" in
    list)
        list_binaries
        ;;
    use)
        set_active "$2"
        ;;
    active)
        get_active
        ;;
    version)
        if [ -f "$VERSIONS_FILE" ]; then
            echo "Version history:"
            tail -20 "$VERSIONS_FILE"
        else
            echo "No version history"
        fi
        ;;
    help|*)
        show_help
        ;;
esac
