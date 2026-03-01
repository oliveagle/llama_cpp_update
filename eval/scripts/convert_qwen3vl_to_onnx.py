#!/usr/bin/env python3
"""
Qwen3-VL-4B ONNX 转换脚本
用于 AMD Ryzen AI NPU 部署

注意：此脚本需要从原始 PyTorch 模型转换，GGUF 格式无法转换为 ONNX

用法:
1. 下载原始 Qwen3-VL-4B 模型 (Safetensors 格式)
   export HF_ENDPOINT=https://hf-mirror.com
   huggingface-cli download Qwen/Qwen3-VL-4B-Instruct --local-dir ~/models/Qwen3-VL-4B-Instruct

2. 运行转换脚本
   python convert_qwen3vl_to_onnx.py ~/models/Qwen3-VL-4B-Instruct ./qwen3vl-onnx

3. 使用 RyzenAI-Server 测试
   export LLAMA_NPU_MODEL=./qwen3vl-onnx/model.onnx
   ./src/ryzenai/llama-npu-server --model ./qwen3vl-onnx/model.onnx --port 8404

依赖:
    pip install torch transformers optimum onnx onnxruntime-genai
"""

import sys
import os
import argparse
from pathlib import Path

def check_dependencies():
    """检查必要的依赖"""
    missing = []

    try:
        import torch
    except ImportError:
        missing.append("torch")

    try:
        import transformers
    except ImportError:
        missing.append("transformers")

    try:
        from optimum.exporters.onnx import main_export
    except ImportError:
        missing.append("optimum[exporters]")

    try:
        import onnx
    except ImportError:
        missing.append("onnx")

    if missing:
        print("❌ 缺少依赖:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n请运行以下命令安装:")
        print(f"   pip install {' '.join(missing)}")
        sys.exit(1)

    print("✓ 依赖检查通过")


def convert_to_onnx(model_path: str, output_path: str, opset: int = 17):
    """
    使用 Optimum 导出 Qwen3-VL 到 ONNX

    Args:
        model_path: 原始模型路径 (Safetensors 或 HF 模型 ID)
        output_path: ONNX 输出目录
        opset: ONNX opset 版本
    """
    from optimum.exporters.onnx import main_export
    from transformers import AutoTokenizer

    print(f"加载模型：{model_path}")

    # 创建输出目录
    os.makedirs(output_path, exist_ok=True)

    # 导出模型
    print("开始导出 ONNX...")
    print(f"  模型：{model_path}")
    print(f"  输出：{output_path}")
    print(f"  Opset: {opset}")

    try:
        main_export(
            model_name_or_path=model_path,
            output=output_path,
            task="text-generation-with-past",  # 支持 KV cache
            opset=opset,
            device="cpu",
            trust_remote_code=True,
        )
        print("✓ ONNX 导出完成")
    except Exception as e:
        print(f"❌ 导出失败：{e}")
        print("\n注意：Qwen3-VL 是视觉语言模型，可能需要特殊处理")
        print("尝试使用 --visual-only 或 --text-only 选项")
        raise

    # 验证导出的模型
    print("\n验证导出的模型...")
    import onnx
    model_file = Path(output_path) / "model.onnx"
    if model_file.exists():
        onnx_model = onnx.load(str(model_file))
        onnx.checker.check_model(onnx_model)
        print(f"✓ ONNX 模型验证通过")
        print(f"  文件大小：{model_file.stat().st_size / 1024 / 1024:.2f} MB")
    else:
        print(f"⚠ 警告：未找到 model.onnx，检查输出目录")


def convert_simple(model_path: str, output_path: str):
    """
    简化版转换（不依赖 optimum）
    使用 PyTorch 原生 ONNX 导出
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"加载模型：{model_path}")

    # 加载 tokenizer 和模型
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float32,
        trust_remote_code=True,
        device_map="cpu"
    )

    model.eval()

    # 准备示例输入
    text = "Hello, I am a test input."
    inputs = tokenizer(text, return_tensors="pt")

    # 导出
    print("导出 ONNX...")

    torch.onnx.export(
        model,
        (inputs["input_ids"], inputs["attention_mask"]),
        output_path,
        opset_version=17,
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size", 1: "sequence_length"}
        }
    )

    print(f"✓ ONNX 导出完成：{output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Qwen3-VL-4B ONNX 转换工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从本地模型转换
  python convert_qwen3vl_to_onnx.py ~/models/Qwen3-VL-4B ./output-onnx

  # 从 HuggingFace 直接下载并转换
  python convert_qwen3vl_to_onnx.py Qwen/Qwen3-VL-4B-Instruct ./output-onnx

  # 使用镜像站点
  export HF_ENDPOINT=https://hf-mirror.com
  python convert_qwen3vl_to_onnx.py Qwen/Qwen3-VL-4B-Instruct ./output-onnx
        """
    )

    parser.add_argument(
        "model_path",
        help="模型路径 (本地目录或 HuggingFace 模型 ID)"
    )
    parser.add_argument(
        "output_path",
        help="ONNX 输出路径"
    )
    parser.add_argument(
        "--opset",
        type=int,
        default=17,
        help="ONNX opset 版本 (默认：17)"
    )
    parser.add_argument(
        "--simple",
        action="store_true",
        help="使用简化转换模式 (PyTorch 原生)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Qwen3-VL-4B ONNX 转换工具")
    print("=" * 60)

    # 检查依赖
    check_dependencies()

    # 检查模型路径
    if not os.path.exists(args.model_path):
        print(f"⚠ 本地路径不存在，尝试从 HuggingFace 下载：{args.model_path}")

    # 转换
    if args.simple:
        convert_simple(args.model_path, args.output_path)
    else:
        convert_to_onnx(args.model_path, args.output_path, args.opset)

    print("\n" + "=" * 60)
    print("转换完成!")
    print("=" * 60)
    print(f"\n输出目录：{args.output_path}")
    print("\n使用方法:")
    print(f"  export LLAMA_NPU_MODEL={os.path.abspath(args.output_path)}/model.onnx")
    print("  ./src/ryzenai/llama-npu-server --model $LLAMA_NPU_MODEL --port 8404")


if __name__ == "__main__":
    main()
