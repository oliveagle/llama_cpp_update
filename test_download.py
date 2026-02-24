#!/usr/bin/env python3
import sys
import os

# Add current directory to path
sys.path.insert(0, '/mnt/volume3/llama_cpp')

print("Python path:", sys.path)
print("Current dir:", os.getcwd())

try:
    import requests
    print("Requests available:", requests.__version__)
except ImportError:
    print("Requests not available")

try:
    from pathlib import Path
    print("Pathlib available")
except ImportError:
    print("Pathlib not available")

# Test creating a directory
model_dir = Path("/mnt/volume3/llama_cpp/models/lfm2.5-audio")
model_dir.mkdir(parents=True, exist_ok=True)
print(f"Directory created: {model_dir}")

# Test writing a file
test_file = model_dir / "test.txt"
test_file.write_text("Test download script")
print(f"Test file written: {test_file}")
print(f"File content: {test_file.read_text()}")

# Clean up test file
test_file.unlink()

print("\nAll tests passed!")
