import os
import sys

# 配置库路径
ryzenai_lib = "/tmp/RyzenAI-SW/Ryzen-AI-CVML-Library/linux/onnx/ryzen14"
os.environ['LD_LIBRARY_PATH'] = ryzenai_lib

# 测试导入 onnxruntime
try:
    import onnxruntime as rt
    print("ONNX Runtime imported successfully")
    print("Available EPs:", rt.get_available_providers())
except Exception as e:
    print(f"Error importing onnxruntime: {e}")
    sys.exit(1)

# 检查 VitisAI EP
print("\nChecking for VitisAI EP...")
if "VitisAIEP" in rt.get_available_providers():
    print("✓ VitisAIEP is available!")
else:
    print("✗ VitisAIEP is not available")
    print("Attempting to force register...")
    try:
        so = rt.SessionOptions()
        so.register_custom_ops_library(os.path.join(ryzenai_lib, "libonnxruntime_vitisai_ep.so"))
        print("Custom ops registered")
        print("Available EPs after registration:", rt.get_available_providers())
    except Exception as e2:
        print(f"Error registering custom ops: {e2}")
