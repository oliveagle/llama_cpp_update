#!/usr/bin/env python3
"""
Download LFM2.5-Audio-1.5B GGUF model from HuggingFace
"""

import os
import sys
import requests
from pathlib import Path

# Configuration
MODEL_REPO = "ggml-org/LFM2.5-Audio-1.5B-GGUF"
HF_ENDPOINT = os.environ.get("HF_ENDPOINT", "https://huggingface.co")
MODEL_DIR = Path("/mnt/volume3/llama_cpp/models/lfm2.5-audio")

def get_file_list(repo_id):
    """Get list of files in the repo using HF API"""
    api_url = f"https://huggingface.co/api/models/{repo_id}"
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("siblings", [])
    except Exception as e:
        print(f"Error fetching repo info: {e}")
        return []

def download_file(url, dest_path, chunk_size=8192):
    """Download a file with progress"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r  Downloading: {percent:.1f}% ({downloaded//1024//1024} MB / {total_size//1024//1024} MB)", end="")

        print(f"\r  Downloaded: {dest_path.name} ({downloaded//1024//1024} MB)")
        return True
    except Exception as e:
        print(f"\n  Error downloading {url}: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return False

def main():
    print("=" * 60)
    print("LFM2.5-Audio-1.5B GGUF 模型下载")
    print("=" * 60)

    # Create model directory
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n模型目录: {MODEL_DIR}")

    # Get file list
    print(f"\n正在获取仓库文件列表: {MODEL_REPO}")
    files = get_file_list(MODEL_REPO)

    if not files:
        print("无法获取文件列表，尝试下载已知文件...")
        # Fallback: try common filenames
        gguf_files = [
            "LFM2.5-Audio-1.5B-Q4_K_M.gguf",
            "LFM2.5-Audio-1.5B-Q8_0.gguf",
            "LFM2.5-Audio-1.5B-IQ4_XS.gguf",
        ]
        mmproj_files = []
    else:
        # Filter GGUF and mmproj files
        gguf_files = []
        mmproj_files = []
        for f in files:
            fname = f.get("rfilename", "")
            if fname.endswith(".gguf"):
                gguf_files.append(fname)
            elif fname.endswith(".mmproj") or fname.endswith(".safetensors"):
                mmproj_files.append(fname)
            elif fname != ".gitattributes" and not fname.startswith("."):
                # Also download other useful files
                mmproj_files.append(fname)

    print(f"\n发现 {len(gguf_files)} 个 GGUF 文件:")
    for f in gguf_files:
        print(f"  - {f}")

    if mmproj_files:
        print(f"\n发现 {len(mmproj_files)} 个附加文件:")
        for f in mmproj_files:
            print(f"  - {f}")

    # Ask user which quant to download (or download Q4_K_M by default)
    target_gguf = None
    for f in gguf_files:
        if "Q4_K_M" in f:
            target_gguf = f
            break

    if not target_gguf and gguf_files:
        target_gguf = gguf_files[0]  # take first one

    if not target_gguf:
        print("\n错误: 没有找到 GGUF 文件！")
        return 1

    print(f"\n将下载: {target_gguf}")

    # Download files
    downloaded = []
    failed = []

    # Download GGUF
    url = f"{HF_ENDPOINT}/{MODEL_REPO}/resolve/main/{target_gguf}"
    dest = MODEL_DIR / target_gguf
    print(f"\n下载 GGUF 模型...")
    if download_file(url, dest):
        downloaded.append(dest)
    else:
        failed.append(target_gguf)

    # Download additional files (mmproj, config, etc.)
    for fname in mmproj_files:
        url = f"{HF_ENDPOINT}/{MODEL_REPO}/resolve/main/{fname}"
        dest = MODEL_DIR / fname
        print(f"\n下载 {fname}...")
        if download_file(url, dest):
            downloaded.append(dest)
        else:
            failed.append(fname)

    # Summary
    print("\n" + "=" * 60)
    print("下载完成")
    print("=" * 60)
    print(f"\n成功: {len(downloaded)} 个文件")
    for f in downloaded:
        size_mb = f.stat().st_size // 1024 // 1024
        print(f"  ✓ {f.name} ({size_mb} MB)")

    if failed:
        print(f"\n失败: {len(failed)} 个文件")
        for f in failed:
            print(f"  ✗ {f}")

    # Verify directory
    print(f"\n模型目录内容:")
    for f in sorted(MODEL_DIR.iterdir()):
        if f.is_file():
            size_mb = f.stat().st_size // 1024 // 1024
            print(f"  {f.name:40s} {size_mb:6d} MB")

    return 0 if not failed else 1

if __name__ == "__main__":
    sys.exit(main())
