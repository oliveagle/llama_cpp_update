import os
import sys

# 配置库路径
ryzenai_lib = "/tmp/RyzenAI-SW/Ryzen-AI-CVML-Library/linux/onnx/ryzen14"
os.environ['LD_LIBRARY_PATH'] = ryzenai_lib
os.environ['ORT_STRATEGY'] = 'ONNX'  # ONNX 策略

# 测试导入 onnxruntime
try:
    import onnxruntime as rt
    print("ONNX Runtime imported successfully")
    print("Version:", rt.__version__)
    print("Available EPs:", rt.get_available_providers())
except Exception as e:
    print(f"Error importing onnxruntime: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 检查 VitisAI EP
print("\n" + "="*60)
print("Checking for VitisAI EP...")
if "VitisAIEP" in rt.get_available_providers():
    print("✓ VitisAIEP is available!")
else:
    print("✗ VitisAIEP is not available")
    print("Attempting to force register...")
    try:
        so = rt.SessionOptions()
        lib_path = os.path.join(ryzenai_lib, "libonnxruntime_vitisai_ep.so")
        print(f"Loading custom ops from: {lib_path}")
        so.register_custom_ops_library(lib_path)
        print("✓ Custom ops registered!")
        print("Available EPs after registration:", rt.get_available_providers())
    except Exception as e2:
        print(f"✗ Error registering custom ops: {e2}")
        import traceback
        traceback.print_exc()
