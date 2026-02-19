#!/bin/bash
#
# llama.cpp Version Manager
# Manages multiple llama.cpp builds with backend and version tracking
#

set -e

LLAMA_BASE="/mnt/volume3/llama_cpp"
DOWNLOADS_DIR="$LLAMA_BASE/downloads"
VERSIONS_FILE="$LLAMA_BASE/config/versions.json"
CURRENT_LINK="$LLAMA_BASE/current"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure config directory exists
mkdir -p "$LLAMA_BASE/config"

# Initialize versions file if not exists
init_versions_file() {
    if [[ ! -f "$VERSIONS_FILE" ]]; then
        cat > "$VERSIONS_FILE" << 'EOF'
{
  "versions": {},
  "backends": {
    "vulkan": {
      "name": "Vulkan",
      "gpu": "AMD gfx1151",
      "description": "AMD Strix Halo GPU"
    },
    "cuda": {
      "name": "CUDA",
      "gpu": "NVIDIA V100",
      "description": "NVIDIA Tesla V100 32GB"
    },
    "cpu": {
      "name": "CPU",
      "gpu": "None",
      "description": "CPU-only inference"
    }
  },
  "active": {
    "vulkan": null,
    "cuda": null
  }
}
EOF
    fi
}

# Get version info from binary
get_version_info() {
    local binary_path="$1"
    if [[ ! -f "$binary_path" ]]; then
        echo "null"
        return
    fi

    local version_output
    version_output=$(cd "$(dirname "$binary_path")" && export LD_LIBRARY_PATH=. && ./llama-server --version 2>&1) || true

    local build_num=$(echo "$version_output" | grep -oP 'version: \K[0-9]+' || echo "unknown")
    local git_hash=$(echo "$version_output" | grep -oP 'version: [0-9]+ \(\K[0-9a-f]+' || echo "unknown")
    local compiler=$(echo "$version_output" | grep -oP 'built with \K[^$]+' || echo "unknown")

    # Detect backend from libraries
    local backend="cpu"
    if [[ -f "$(dirname "$binary_path")/libggml-vulkan.so" ]]; then
        backend="vulkan"
    elif [[ -f "$(dirname "$binary_path")/libggml-cuda.so" ]] || \
         [[ -f "$(dirname "$binary_path")/libggml-cuda12.so" ]]; then
        backend="cuda"
    fi

    cat << EOF
{
  "build_number": $build_num,
  "git_hash": "$git_hash",
  "backend": "$backend",
  "compiler": "$compiler",
  "path": "$binary_path"
}
EOF
}

# Scan downloads directory for versions
scan_versions() {
    echo "{"
    local first=true
    for dir in "$DOWNLOADS_DIR"/llama-b*/; do
        [[ -d "$dir" ]] || continue

        local dirname=$(basename "$dir")
        local build_num=${dirname#llama-b}

        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo ","
        fi

        echo "  \"$build_num\": {"
        echo "    \"directory\": \"$dir\","

        if [[ -f "$dir/llama-server" ]]; then
            local info=$(get_version_info "$dir/llama-server")
            echo "    \"binary\": \"native\","
            echo "    \"info\": $info"
        elif [[ -f "$dir/bin/llama-server" ]]; then
            local info=$(get_version_info "$dir/bin/llama-server")
            echo "    \"binary\": \"bin/\","
            echo "    \"info\": $info"
        else
            echo "    \"binary\": null,"
            echo "    \"info\": null"
        fi

        echo -n "  }"
    done
    echo ""
    echo "}"
}

# Update versions file
update_versions() {
    init_versions_file

    local scanned=$(scan_versions)

    # Merge with existing active assignments
    python3 << EOF
import json

with open("$VERSIONS_FILE", "r") as f:
    data = json.load(f)

scanned = json.loads('''$scanned''')

# Update versions
for build_num, info in scanned.items():
    if build_num not in data["versions"]:
        data["versions"][build_num] = info
    else:
        # Preserve active assignments
        data["versions"][build_num].update(info)

with open("$VERSIONS_FILE", "w") as f:
    json.dump(data, f, indent=2)

print("Updated versions file with", len(scanned), "versions")
EOF
}

# List all versions
list_versions() {
    init_versions_file

    echo -e "${BLUE}=== llama.cpp Versions ===${NC}"
    echo ""

    python3 << EOF
import json

with open("$VERSIONS_FILE", "r") as f:
    data = json.load(f)

print(f"{'Build':<8} {'Hash':<12} {'Backend':<8} {'Status':<10} {'Path'}")
print("-" * 80)

for build_num in sorted(data["versions"].keys(), key=int, reverse=True):
    v = data["versions"][build_num]
    info = v.get("info", {}) or {}

    build = build_num
    hash_str = info.get("git_hash", "unknown")[:10]
    backend = info.get("backend", "unknown")

    # Determine status
    status = ""
    for be, active in data.get("active", {}).items():
        if active == build_num:
            status = f"active ({be})"
            break

    if not status:
        status = "installed"

    path = v.get("directory", "N/A")
    path = path.replace("/mnt/volume3/llama_cpp/downloads/", ".../")

    print(f"{build:<8} {hash_str:<12} {backend:<8} {status:<10} {path}")
EOF
}

# Set active version for backend
set_active() {
    local backend="$1"
    local build_num="$2"

    init_versions_file

    # Validate backend
    python3 << EOF
import json
import sys

with open("$VERSIONS_FILE", "r") as f:
    data = json.load(f)

if "$backend" not in data.get("backends", {}):
    print(f"Error: Unknown backend '$backend'")
    print(f"Available: {', '.join(data.get('backends', {}).keys())}")
    sys.exit(1)

if "$build_num" not in data.get("versions", {}):
    print(f"Error: Version '$build_num' not found")
    print("Run 'scan' to update version list")
    sys.exit(1)

# Check backend compatibility
v = data["versions"]["$build_num"]
info = v.get("info", {}) or {}
if info.get("backend") != "$backend":
    print(f"Warning: Version '$build_num' was built for '{info.get('backend')}', not '$backend'")
    response = input("Continue anyway? [y/N] ")
    if response.lower() != 'y':
        sys.exit(1)

# Set active
data["active"]["$backend"] = "$build_num"

with open("$VERSIONS_FILE", "w") as f:
    json.dump(data, f, indent=2)

print(f"Set active $backend version to $build_num")
EOF
}

# Show current status
status() {
    init_versions_file

    echo -e "${BLUE}=== Current Status ===${NC}"
    echo ""

    python3 << EOF
import json
import os

with open("$VERSIONS_FILE", "r") as f:
    data = json.load(f)

current_link = os.readlink("/mnt/volume3/llama_cpp/current") if os.path.islink("/mnt/volume3/llama_cpp/current") else None

print(f"{'Backend':<10} {'Active Build':<12} {'Git Hash':<12} {'Symlink'}")
print("-" * 70)

for backend, info in data.get("backends", {}).items():
    active = data.get("active", {}).get(backend, "none")
    hash_str = "N/A"
    symlink = ""

    if active and active in data.get("versions", {}):
        v = data["versions"][active]
        vinfo = v.get("info", {}) or {}
        hash_str = vinfo.get("git_hash", "N/A")[:10]

        # Check if this is the current symlink target
        if current_link and active in current_link:
            symlink = "<- current"

    print(f"{backend:<10} {active or 'none':<12} {hash_str:<12} {symlink}")

print("")
print("Current symlink points to:")
if current_link:
    print(f"  {current_link}")
else:
    print("  (not set)")
EOF
}

# Update symlinks based on active versions
apply() {
    init_versions_file

    python3 << 'EOF'
import json
import os
import sys

with open("$VERSIONS_FILE", "r") as f:
    data = json.load(f)

# Determine which backend to use for 'current' symlink
# Priority: vulkan > cuda > cpu
active_build = None
for backend in ["vulkan", "cuda", "cpu"]:
    active = data.get("active", {}).get(backend)
    if active:
        active_build = active
        break

if not active_build:
    print("Error: No active version set for any backend")
    sys.exit(1)

v = data["versions"].get(active_build)
if not v:
    print(f"Error: Active build {active_build} not found in versions")
    sys.exit(1)

# Update symlink
target = v.get("directory")
current_link = "/mnt/volume3/llama_cpp/current"

if os.path.islink(current_link):
    os.unlink(current_link)
elif os.path.exists(current_link):
    print(f"Error: {current_link} exists and is not a symlink")
    sys.exit(1)

os.symlink(target, current_link)
print(f"Updated 'current' symlink to build {active_build}")
print(f"  Target: {target}")
EOF
}

# Show help
show_help() {
    cat << 'EOF'
Usage: llama-version-manager.sh <command> [args]

Commands:
  scan              Scan downloads directory and update version database
  list              List all available versions
  status            Show current status of all backends
  set <be> <ver>    Set active version for backend (be: vulkan|cuda|cpu)
  apply             Apply active version to 'current' symlink
  info <ver>        Show detailed info for a version
  help              Show this help message

Examples:
  llama-version-manager.sh scan
  llama-version-manager.sh list
  llama-version-manager.sh set vulkan 8069
  llama-version-manager.sh apply
  llama-version-manager.sh status

Backends:
  vulkan    AMD GPU (gfx1151) - llama-bXXXX-bin-ubuntu-vulkan-x64
  cuda      NVIDIA GPU (V100) - compiled from source
  cpu       CPU-only builds
EOF
}

# Main
case "${1:-help}" in
    scan|update)
        update_versions
        ;;
    list|ls)
        list_versions
        ;;
    status|st)
        status
        ;;
    set)
        if [[ $# -lt 3 ]]; then
            echo "Usage: $0 set <backend> <build_number>"
            echo "  backend: vulkan, cuda, or cpu"
            exit 1
        fi
        set_active "$2" "$3"
        ;;
    apply)
        apply
        ;;
    info)
        if [[ $# -lt 2 ]]; then
            echo "Usage: $0 info <build_number>"
            exit 1
        fi
        init_versions_file
        python3 << EOF
import json
with open("$VERSIONS_FILE") as f:
    data = json.load(f)
v = data["versions"].get("$2", {})
print(json.dumps(v, indent=2))
EOF
        ;;
    help|--help|-h|*)
        show_help
        ;;
esac
