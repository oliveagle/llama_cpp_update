# llama.cpp Version Manager

A bash-based version management system for tracking and switching between multiple llama.cpp builds with different backends (Vulkan, CUDA, CPU).

## Features

- **Automatic version detection**: Scans downloads directory and extracts version info
- **Backend tracking**: Manages Vulkan (AMD), CUDA (NVIDIA), and CPU builds
- **Git hash tracking**: Records commit hash for each build
- **Symlink management**: Easy switching between versions
- **JSON-based database**: Stores version metadata in `config/versions.json`

## Quick Start

```bash
# Scan for available versions
./bin/llama-version-manager.sh scan

# List all versions
./bin/llama-version-manager.sh list

# Show current status
./bin/llama-version-manager.sh status

# Set active version for backend
./bin/llama-version-manager.sh set vulkan 8069
./bin/llama-version-manager.sh set cuda 8069

# Apply active version to 'current' symlink
./bin/llama-version-manager.sh apply
```

## Commands

| Command | Description |
|---------|-------------|
| `scan` | Scan downloads directory and update version database |
| `list` | List all available versions with status |
| `status` | Show current status of all backends |
| `set <backend> <build>` | Set active version for a backend |
| `apply` | Apply active version to 'current' symlink |
| `info <build>` | Show detailed info for a version |
| `help` | Show help message |

## Backends

| Backend | GPU | Description |
|---------|-----|-------------|
| `vulkan` | AMD gfx1151 | AMD Strix Halo GPU |
| `cuda` | NVIDIA V100 | NVIDIA Tesla V100 32GB |
| `cpu` | None | CPU-only inference |

## Version Database

Stored in `config/versions.json`:

```json
{
  "versions": {
    "8069": {
      "directory": "/mnt/volume3/llama_cpp/downloads/llama-b8069/",
      "binary": "native",
      "info": {
        "build_number": 8069,
        "git_hash": "d5dfc3302",
        "backend": "vulkan",
        "compiler": "GNU 11.4.0 for Linux x86_64"
      }
    }
  },
  "backends": { ... },
  "active": {
    "vulkan": "8069",
    "cuda": null,
    "cpu": null
  }
}
```

## Example Output

```
$ ./bin/llama-version-manager.sh list

=== llama.cpp Versions ===

Build    Hash         Backend  Status           Path
--------------------------------------------------------------------------------
8069     d5dfc3302    vulkan   active (vulkan)  .../llama-b8069/
8040     0ccbfdef3    cpu      installed        .../llama-b8040/
7952     3e2164766    vulkan   installed        .../llama-b7952/
7951     22cae8321    vulkan   installed        .../llama-b7951/
7947     a4ea7a188    vulkan   installed        .../llama-b7947/

$ ./bin/llama-version-manager.sh status

=== Current Status ===

Backend    Active Build Git Hash     Symlink
----------------------------------------------------------------------
vulkan     8069         d5dfc3302    <- current
cuda       none         N/A
cpu        none         N/A

Current symlink points to:
  /mnt/volume3/llama_cpp/downloads/llama-b8069
```

## File Locations

- **Manager script**: `bin/llama-version-manager.sh`
- **Version database**: `config/versions.json`
- **Downloaded builds**: `downloads/llama-bXXXX/`
- **Current symlink**: `current -> downloads/llama-bXXXX`

## Integration with Server Scripts

Server management scripts should use the `current` symlink:

```bash
# In server scripts
LLAMA_BIN="./current/llama-server"
# or
LLAMA_BIN="./current/bin/llama-server"
```

This allows seamless version switching without changing server scripts.

## Adding New Versions

1. Download new build to `downloads/llama-bXXXX/`
2. Run `./bin/llama-version-manager.sh scan`
3. Set as active: `./bin/llama-version-manager.sh set vulkan XXXX`
4. Apply: `./bin/llama-version-manager.sh apply`

## Notes

- Build numbers correspond to llama.cpp build numbers (e.g., b8069)
- Git hashes are extracted from binary version output
- Backend is auto-detected from available libraries (libggml-vulkan.so, libggml-cuda.so)
- Multiple backends can have different active versions simultaneously
