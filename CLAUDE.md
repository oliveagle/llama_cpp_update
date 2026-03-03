# llama.cpp 双实例部署计划

## 目标
同时运行两个 llama.cpp 实例：
1. **Vulkan 版本** (gfx1151/AMD) → 端口 8400
2. **CUDA 版本** (V100) → 端口 8401

支持多模型加载和自动切换。

## 现有资源

### Vulkan 版本
- 位置: `/mnt/volume3/llama_cpp/core/downloads/llama-b8183/`
- 当前 `current` 符号链接指向: `llama-b8183`
- 已编译支持: Vulkan, AMD gfx1151

### CUDA 版本
- 位置: `/home/oliveagle/opt/llama.cpp/build/bin/llama-server`
- 已编译支持: CUDA 12.5, sm_70 (V100)
- 版本: 8134 (df1764dc5)
- 更新方式: 源码自动编译（Linux 无预编译包）

### ROCm 版本 (待完成)
- 位置: `/mnt/volume3/llama_cpp/core/downloads/llama-b8183-rocm/`
- 正在下载和配置中

### 模型配置
- Presets 文件: `core/config/presets/mypresets.ini` (13个模型)
- CUDA Presets: `core/config/presets/mypresets-cuda.ini` (11个模型)

## 需要完成的工作

### 1. 独立的服务器管理脚本
创建两个独立的管理脚本:

**`llama-server-cuda.sh`** - 管理 V100/CUDA 实例 (端口 8401)
- 支持 start/stop/restart/status/logs 命令
- 优先使用 systemd 服务 (llama-server-8401.service)
- 失败时回退到直接启动

**`llama-server-vulkan.sh`** - 管理 AMD/Vulkan 实例 (端口 8400)
- 支持 start/stop/restart/status/logs 命令
- 自动查找有 Vulkan 库的版本
- 设置 AMD ICD 环境

### 2. 统一更新脚本
**`update-llama-cpp.sh`** - 统一更新脚本:
- Vulkan: 自动下载预编译包 (ubuntu-vulkan-x64)
- CUDA: 自动源码编译（Linux 无预编译包）
- 自动重启 systemd 服务
- 自动清理旧版本

### 3. Systemd 服务
系统级 systemd 服务（开机自动启动）:
- `llama-server-8400.service` - Vulkan 服务 (AMD gfx1151)
- `llama-server-8401.service` - CUDA 服务 (V100)

### 4. 模型切换机制
利用 llama.cpp 的 `--models-max` 和 `--models-preset` 参数:
- 同时加载多个模型
- 通过 API 切换当前使用的模型

## 文件结构

> **详细说明**: 参见 [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)

```
llama_cpp/
├── CLAUDE.md                    # 本文件 (项目配置)
├── AGENTS.md -> CLAUDE.md       # 软链接
├── PROJECT_STRUCTURE.md         # 目录结构说明
├── core/                        # [模块 1] llama.cpp 核心管理
│   ├── bin/                     # 可执行脚本
│   ├── config/                  # 配置文件 (presets, nginx, versions.json)
│   ├── systemd/                 # systemd 服务
│   ├── scripts/                 # 服务器启动脚本
│   ├── downloads/               # 下载的 llama.cpp 版本
│   └── logs/                    # 服务日志
├── dev/                         # [模块 2] llama.cpp 功能开发
│   ├── src/                     # 源代码 (NPU, ONNX Runtime, RyzenAI)
│   ├── nanoquant/               # NanoQuant 量化工具
│   ├── ryzenai/                 # RyzenAI NPU 工具
│   ├── build/                   # 构建输出
│   └── experimental/            # 实验性功能
├── eval/                        # [模块 3] 大模型本地化评估
│   ├── frameworks/              # 评测框架 (LiveCodeBench, 等)
│   ├── tests/                   # 评测测试 (stage1/stage2/stage3/stage4)
│   ├── scripts/                 # 评测脚本
│   ├── tools/                   # 评测工具 (benchmark, test, utils)
│   ├── web/                     # Web 报告
│   ├── results/                 # 评测结果
│   └── reports/                 # 评测报告
├── docs/                        # 文档目录
│   ├── guides/                  # 使用指南
│   ├── reports/                 # 技术报告
│   ├── analysis/                # 分析报告
│   └── benchmarks/              # 性能测试报告
├── models/                      # 模型相关
├── tmp/                         # 临时文件
└── current -> core/downloads/llama-b8183  # 当前 Vulkan 版本链接
```

## 端口分配（最终方案）

| 服务 | 端口 | GPU | 说明 |
|------|------|-----|------|
| llama.cpp Vulkan | 8400 | AMD gfx1151 | Strix Halo |
| llama.cpp CUDA | 8401 | NVIDIA V100 | Tesla V100 |
| llama.cpp Embedding | 13232 | AMD gfx1151 | Qwen3 Embedding |
| vLLM V100 | 8403 | NVIDIA V100 | 预留 |
| vLLM ROCm 7.12 | 8405 | AMD gfx1151 | 预留 |

## 使用命令

### Vulkan 服务器 (gfx1151 - 8400)
```bash
# 使用 systemd 服务（推荐）
sudo systemctl start llama-server-8400.service
sudo systemctl status llama-server-8400.service
sudo systemctl stop llama-server-8400.service

# 或使用脚本（core/scripts/）
cd /mnt/volume3/llama_cpp
./core/scripts/llama-server-vulkan.sh start   # 启动
./core/scripts/llama-server-vulkan.sh stop    # 停止
./core/scripts/llama-server-vulkan.sh restart # 重启
./core/scripts/llama-server-vulkan.sh status  # 查看状态
```

### CUDA 服务器 (V100 - 8401)
```bash
# 使用 systemd 服务（推荐）
sudo systemctl start llama-server-8401.service
sudo systemctl status llama-server-8401.service
sudo systemctl stop llama-server-8401.service

# 或使用脚本（core/scripts/）
cd /mnt/volume3/llama_cpp
./core/scripts/llama-server-cuda.sh start     # 启动
./core/scripts/llama-server-cuda.sh stop      # 停止
./core/scripts/llama-server-cuda.sh restart   # 重启
./core/scripts/llama-server-cuda.sh status    # 查看状态
```

### Embedding 服务器 (端口 13232)
```bash
# 使用 systemd 服务
sudo systemctl start llama-server-13232.service

# 或使用脚本
cd /mnt/volume3/llama_cpp
./core/scripts/llama-server-embedding.sh start   # 启动
./core/scripts/llama-server-embedding.sh stop    # 停止
./core/scripts/llama-server-embedding.sh status  # 查看状态
```

### 统一更新脚本 (v2)
```bash
cd /mnt/volume3/llama_cpp

# 查看状态
./update-llama-cpp-v2.sh status

# Vulkan 更新（自动下载预编译包）
./update-llama-cpp-v2.sh vulkan           # 更新到最新
./update-llama-cpp-v2.sh vulkan list      # 列出可用版本
./update-llama-cpp-v2.sh vulkan 8183      # 指定版本

# CUDA 更新（自动源码编译）
./update-llama-cpp-v2.sh cuda             # 编译最新版本
./update-llama-cpp-v2.sh cuda 8183        # 编译指定版本

# ROCm 更新（自动下载预编译包）
./update-llama-cpp-v2.sh rocm             # 更新到最新
./update-llama-cpp-v2.sh rocm list        # 列出可用版本

# 更新所有版本
./update-llama-cpp-v2.sh all
```

## 测试命令
```bash
# Vulkan 实例 (端口 8400) - Qwen3 测试
curl http://localhost:8400/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "Qwen3-0.6B-Q4_0", "messages": [{"role": "user", "content": "你好"}]}'

# CUDA 实例 (端口 8401) - Qwen3 测试
curl http://localhost:8401/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "Qwen3-0.6B-Q4_0", "messages": [{"role": "user", "content": "你好"}]}'
```

## 注意事项

1. **端口冲突**: 确保 8400 和 8401 未被占用
2. **GPU 选择**: CUDA 使用 `CUDA_VISIBLE_DEVICES=0`, Vulkan 使用 AMD ICD
3. **模型缓存**: 两个实例会分别缓存模型到各自的内存中
4. **显存管理**: V100 32GB + gfx1151 32GB，注意模型大小不要超过显存

## 状态
- [x] 分析现有代码结构
- [x] 创建 llama-server-cuda.sh (V100/8401)
- [x] 创建 llama-server-vulkan.sh (gfx1151/8400)
- [x] 创建 llama-server-embedding.sh (13232)
- [x] 创建统一更新脚本 update-llama-cpp-v2.sh
  - [x] Vulkan 自动下载预编译包 (ubuntu-vulkan-x64)
  - [x] CUDA 自动源码编译（Linux 无预编译包）
  - [x] ROCm 自动下载预编译包 (ubuntu-rocm-7.2-x64)
- [x] systemd 服务 (系统级，开机自启)
  - [x] llama-server-8400.service (Vulkan)
  - [x] llama-server-8401.service (CUDA)
- [x] 多模型配置
  - [x] Vulkan: 13 个模型 (mypresets.ini)
  - [x] CUDA: 11 个模型 (mypresets-cuda.ini)
- [x] 测试双实例运行
- [x] 验证模型切换功能
- [x] 目录结构整理 (2026-02-18)
  - [x] core/ - llama.cpp 核心管理
  - [x] dev/ - 功能开发
  - [x] eval/ - 大模型评测
  - [x] docs/benchmarks/ - 性能测试报告
  - [x] PROJECT_STRUCTURE.md 目录结构文档

## 最后更新
2026-03-04

## 最近变更 (2026-03-04)

**Qwen3.5-4B 测试完成**:
- ✅ Stage 1 性能测试: 提示处理 2191 tokens/s, 生成 44.9 tokens/s, 内存 4.2GB, 显存 3.8GB
- ✅ Stage 2 综合能力测试: 94/100 (94.0%) 优秀
- ✅ Stage 3 深度能力测试: 903/1000 (90.3%) 优秀
- ✅ 与 Qwen3.5-9B 对比: 在代码生成、知识问答、多轮对话等方面优于 9B 模型
- ✅ 资源消耗显著降低: 内存 -50%, 显存 -38%, 性价比更高

**能力评测输出目录调整**:
- ✅ knowledge/ → eval/results/capabilities/knowledge/
- ✅ multiturn/ → eval/results/capabilities/multiturn/
- ✅ reasoning/ → eval/results/capabilities/reasoning/
- ✅ safety/ → eval/results/capabilities/safety/ (含 stage3_2026-03-03.jsonl)

**文件结构整理**:
- ✅ 将所有 `test_*.py` 文件从根目录移至 `eval/tests/`
- ✅ 将根目录 `downloads/` 目录合并至 `core/downloads/`
- ✅ 更新 `current` 符号链接指向 `core/downloads/llama-b8183`
- ✅ 创建 `current-rocm` 符号链接指向 `core/downloads/current-rocm`
- ✅ 将日志文件移至 `eval/logs/`
