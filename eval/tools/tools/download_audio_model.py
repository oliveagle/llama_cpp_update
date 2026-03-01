#!/usr/bin/env python3
"""
Simple download script using urllib (no external dependencies)
"""

import sys
import os
import urllib.request
import urllib.error
from pathlib import Path

# Configuration
MODEL_REPO = "ggml-org/LFM2.5-Audio-1.5B-GGUF"
HF_ENDPOINT = os.environ.get("HF_ENDPOINT", "https://hf-mirror.com")
MODEL_DIR = Path("/mnt/volume3/llama_cpp/models/lfm2.5-audio")

def download_file(url, dest_path):
    """Download a file with progress"""
    class DownloadProgress:
        def __init__(self):
            self.bytes_read = 0

        def __call__(self, block_num, block_size, total_size):
            self.bytes_read += block_size
            if total_size > 0:
                percent = (self.bytes_read / total_size) * 100
                mb_read = self.bytes_read // (1024 * 1024)
                mb_total = total_size // (1024 * 1024)
                sys.stdout.write(f"\r  {percent:5.1f}%  ({mb_read} MB / {mb_total} MB)")
                sys.stdout.flush()

    try:
        print(f"  URL: {url}")
        progress = DownloadProgress()
        urllib.request.urlretrieve(url, str(dest_path), reporthook=progress)
        sys.stdout.write("\n")

        if dest_path.exists():
            size_mb = dest_path.stat().st_size // (1024 * 1024)
            print(f"  ✓ Downloaded: {dest_path.name} ({size_mb} MB)")
            return True
        return False
    except Exception as e:
        sys.stdout.write("\n")
        print(f"  ✗ Error: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return False

def main():
    print("=" * 60)
    print("LFM2.5-Audio-1.5B GGUF 模型下载")
    print("=" * 60)

    # Create model directory
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nModel directory: {MODEL_DIR}")
    print(f"Using mirror: {HF_ENDPOINT}")

    # List of possible GGUF files (common quantizations)
    gguf_files = [
        "LFM2.5-Audio-1.5B-Q4_K_M.gguf",
        "LFM2.5-Audio-1.5B-Q8_0.gguf",
        "LFM2.5-Audio-1.5B-Q4_K_S.gguf",
        "LFM2.5-Audio-1.5B-Q5_K_M.gguf",
        "LFM2.5-Audio-1.5B-IQ4_XS.gguf",
        "LFM2.5-Audio-1.5B-Q2_K.gguf",
        "LFM2.5-Audio-1.5B-F16.gguf",
    ]

    other_files = [
        "README.md",
        "config.json",
        "tokenizer.json",
        "tokenizer.model",
        "tokenizer_config.json",
        "preprocessor_config.json",
        "generation_config.json",
    ]

    downloaded = []
    failed = []

    # Try to download Q4_K_M first (most popular)
    target_file = "LFM2.5-Audio-1.5B-Q4_K_M.gguf"
    print(f"\n[1/2] Downloading GGUF model...")
    print(f"  Target: {target_file}")

    url = f"{HF_ENDPOINT}/{MODEL_REPO}/resolve/main/{target_file}"
    dest = MODEL_DIR / target_file

    if download_file(url, dest):
        downloaded.append(target_file)
    else:
        failed.append(target_file)
        # Try other files
        print("\n  Trying other quantizations...")
        for fname in gguf_files:
            if fname == target_file:
                continue
            url = f"{HF_ENDPOINT}/{MODEL_REPO}/resolve/main/{fname}"
            dest = MODEL_DIR / fname
            print(f"\n  Trying: {fname}")
            if download_file(url, dest):
                downloaded.append(fname)
                break  # Got one
            else:
                failed.append(fname)

    # Download other useful files
    print(f"\n[2/2] Downloading config files...")
    for fname in other_files:
        url = f"{HF_ENDPOINT}/{MODEL_REPO}/resolve/main/{fname}"
        dest = MODEL_DIR / fname
        print(f"\n  Trying: {fname}")
        if download_file(url, dest):
            downloaded.append(fname)
        # Don't count as failed - these are optional

    # Summary
    print("\n" + "=" * 60)
    print("Download Summary")
    print("=" * 60)

    print(f"\nSuccessfully downloaded ({len(downloaded)}):")
    for fname in downloaded:
        fpath = MODEL_DIR / fname
        if fpath.exists():
            size_mb = fpath.stat().st_size // (1024 * 1024)
            print(f"  ✓ {fname:40s} {size_mb:6d} MB")

    # Show directory
    print(f"\nDirectory contents:")
    if MODEL_DIR.exists():
        for f in sorted(MODEL_DIR.iterdir()):
            if f.is_file():
                size_mb = f.stat().st_size // (1024 * 1024)
                print(f"  {f.name:40s} {size_mb:6d} MB")

    # Check if we have at least one GGUF
    has_gguf = False
    for f in MODEL_DIR.glob("*.gguf"):
        if f.is_file():
            has_gguf = True
            break

    if has_gguf:
        print(f"\n✓ Success! Model downloaded to: {MODEL_DIR}")
        return 0
    else:
        print(f"\n✗ Failed to download GGUF model")
        return 1

if __name__ == "__main__":
    sys.exit(main())
