print("Hello from Python!")
import sys
print("Python version:", sys.version)
import os
print("Current dir:", os.getcwd())

# Try to create a directory
model_dir = "/mnt/volume3/llama_cpp/models/lfm2.5-audio"
os.makedirs(model_dir, exist_ok=True)
print("Directory created:", model_dir)

# Try to write a file
test_file = os.path.join(model_dir, "test.txt")
with open(test_file, "w") as f:
    f.write("test content\n")
print("Test file written:", test_file)

# Verify
with open(test_file, "r") as f:
    print("Content:", repr(f.read()))

# Clean up
import os
try:
    os.unlink(test_file)
    print("Test file removed")
except:
    pass

print("\nAll tests OK!")
