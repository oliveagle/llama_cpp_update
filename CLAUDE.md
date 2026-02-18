# llama.cpp 双实例部署计划

## 目标
同时运行两个 llama.cpp 实例：
1. **Vulkan 版本** (gfx1151/AMD) → 端口 8400
2. **CUDA 版本** (V100) → 端口 8401

支持多模型加载和自动切换。

## 现有资源

### Vulkan 版本
- 位置: `/mnt/volume3/llama_cpp/downloads/llama-b7952/`
- 当前 `current` 符号链接指向: `llama-b8040` (但没有 Vulkan 库)
- 有 Vulkan 库的版本: `llama-b7825`, `llama-b7947`, `llama-b7951`, `llama-b7952`

### CUDA 版本
- 位置: `~/opt/llama.cpp/build/bin/llama-server`
- 已编译支持: CUDA 12.5, sm_70 (V100)
- 更新方式: 源码自动编译（Linux 无预编译包）

### 模型配置
- Presets 文件: `config/presets/mypresets.ini`
- 包含 13 个 GGUF 模型配置

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
├── bin/                         # 可执行脚本
│   ├── llama-server-*.sh        # 服务器管理脚本
│   └── update*.sh               # 更新脚本
├── config/                      # 配置文件
│   ├── presets/                 # 模型预设配置
│   └── nginx.conf               # nginx配置
├── docs/                        # 文档目录
│   ├── guides/                  # 使用指南
│   ├── reports/                 # 技术报告
│   ├── analysis/                # 分析报告
│   └── benchmarks/              # 性能测试报告
├── eval/                        # 评测框架
├── eval_results/                # 评测结果
│   ├── stage1/                  # Stage 1测试结果
│   ├── stage2/                  # Stage 2测试结果
│   ├── stage3/                  # Stage 3测试结果
│   └── raw_data/                # 原始数据
├── scripts/                     # 工具脚本
├── tests/                       # 测试脚本
├── web/                         # Web报告
├── current -> downloads/...     # Vulkan 当前版本
├── downloads/                   # 下载的 llama.cpp 版本
└── logs/                        # 日志目录
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
./bin/llama-server-vulkan.sh start   # 启动
./bin/llama-server-vulkan.sh stop    # 停止
./bin/llama-server-vulkan.sh restart # 重启
./bin/llama-server-vulkan.sh status  # 查看状态
./bin/llama-server-vulkan.sh logs    # 查看实时日志
```

### CUDA 服务器 (V100 - 8401)
```bash
./bin/llama-server-cuda.sh start     # 启动
./bin/llama-server-cuda.sh stop      # 停止
./bin/llama-server-cuda.sh restart   # 重启
./bin/llama-server-cuda.sh status    # 查看状态
./bin/llama-server-cuda.sh logs      # 查看实时日志
```

### Embedding 服务器 (端口 13232)
```bash
./bin/llama-server-embedding.sh start   # 启动
./bin/llama-server-embedding.sh stop    # 停止
./bin/llama-server-embedding.sh status  # 查看状态
```

### 统一更新脚本
```bash
# 查看状态
./bin/update-llama-cpp.sh status

# Vulkan 更新（自动下载预编译包）
./bin/update-llama-cpp.sh vulkan           # 更新到最新
./bin/update-llama-cpp.sh vulkan list      # 列出可用版本
./bin/update-llama-cpp.sh vulkan 8069      # 指定版本

# CUDA 更新（自动源码编译）
./bin/update-llama-cpp.sh cuda             # 编译最新版本
./bin/update-llama-cpp.sh cuda 8069        # 编译指定版本
```

## 测试命令
```bash
# Vulkan 实例 (端口 8400)
curl http://localhost:8400/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "MiniCPM-o-4_5-Q4_K_M", "messages": [{"role": "user", "content": "你好"}]}'

# CUDA 实例 (端口 8401)
curl http://localhost:8401/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "MiniCPM-o-4_5-Q4_K_M", "messages": [{"role": "user", "content": "你好"}]}'
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
- [x] 创建统一更新脚本 update-llama-cpp.sh
  - [x] Vulkan 自动下载预编译包
  - [x] CUDA 自动源码编译
- [x] systemd 服务 (系统级，开机自启)
  - [x] llama-server-8400.service (Vulkan)
  - [x] llama-server-8401.service (CUDA)
- [x] 多模型配置
  - [x] Vulkan: 13 个模型 (mypresets.ini)
  - [x] CUDA: 7 个模型 (mypresets-cuda.ini)
- [x] 测试双实例运行
- [x] 验证模型切换功能
- [x] 目录结构整理 (2026-02-18)
  - [x] bin/ - 可执行脚本 (服务器管理、更新)
  - [x] config/ - 配置文件 (presets, nginx)
  - [x] tests/ - 测试脚本
  - [x] web/ - Web 报告
  - [x] docs/benchmarks/ - 性能测试报告
  - [x] eval_results/ - 按阶段/后端重组
  - [x] PROJECT_STRUCTURE.md 目录结构文档

## 最后更新
2026-02-18
