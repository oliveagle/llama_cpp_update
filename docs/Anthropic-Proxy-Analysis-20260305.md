# Anthropic 代理请求分析报告

> **分析时间**: 2026-03-05
> **分析对象**: Claude Code 发送给 Anthropic 代理的请求
> **代理实现**: Go 版本 (core/go-proxy/main.go)

---

## 一、问题概述

### 原始现象
Claude Code 发送 "hi" 消息时，llama.cpp 返回错误：
```
request (35501 tokens) exceeds the available context size (12288 tokens)
```

### 初步分析
- 请求本身只有 842 字节
- 但包含大量历史上下文
- llama.cpp 原始配置 `ctx-size=12288` 不足

---

## 二、请求结构分析

### 完整请求概览

| 字段 | 值 |
|------|-----|
| `model` | `claude-3-5-sonnet-20241022` |
| `max_tokens` | `8192` |
| `messages` | **3 条消息** |

### 消息详情

| 序号 | 角色 | 内容块数 | 说明 |
|------|------|-----------|------|
| 1 | `user` | **12 个 text blocks** | ⚠️ 包含大量系统上下文 |
| 2 | `assistant` | 1 个 text block | 之前的回复 |
| 3 | `user` | 1 个 text block | 用户输入 "hi" |

---

## 三、详细消息分析

### Message 1 (user) - 12 个 content blocks

| Block | 类型 | 大小 | 内容 |
|-------|------|------|------|
| 1 | `text` | 362 B | todo list reminder |
| **2** | `text` | **33,185 B** | **⚠️ claudeMd (Agent 配置中心)** |
| 3 | `text` | 2 B | "hi" |
| 4 | `text` | 2 B | "hi" |
| 5 | `text` | 2 B | "hi" |
| 6 | `text` | 2 B | "hi" |
| 7 | `text` | 2 B | "hi" |
| 8 | `text` | 2 B | "hi" |
| 9 | `text` | 2 B | "hi" |
| 10 | `text` | 481 B | TodoWrite tool reminder |
| 11 | `text` | 2 B | "hi" |
| 12 | `text` | 2 B | "hi" |

**总计**: ~35,000 tokens

---

### Block 2 详细内容 (33,185 bytes)

这是核心的系统上下文，来自 `~/.claude/CLAUDE.md` (Agent 配置中心)：

#### 包含的配置项：

1. **用户偏好**
   - 语言：中文
   - Context7：代码生成/配置时自动使用
   - 删除文件：`mv` 到同磁盘 `tmp/2del/`
   - HuggingFace：使用镜像
   - JSON 文件规范：禁止 `.json`，使用 `.jsonc` / `.jsonl`
   - 配置文件规范：禁止 YAML，统一使用 `.jsonc`
   - 文件名版本规范：`v1`/`v2`/`v3` 递增

2. **Git 用户配置规范**
   - 个人项目 git 配置 (oliveagle@gmail.com)
   - 配置范围说明
   - 配置检查命令

3. **核心工具链**
   - 构建：just
   - 容器：podman
   - 终端：zellij
   - Git：标准 git

4. **存储目录**
   - `/mnt/home_share` 结构
   - Podman 镜像规范

5. **NPU 开发环境 (AMD Ryzen AI)**
   - mlir-aie 开发环境配置
   - 激活环境脚本
   - 关键变量说明
   - 关键工具列表
   - 编译示例
   - 开发项目模板

6. **Python 虚拟环境规范**
   - 统一管理原则
   - 创建命令
   - 环境列表 (10+ 个虚拟环境)
   - CLI 工具链接

7. **...以及更多配置...**
   - AMD Ryzen AI NPU 开发 (Strix Halo)
   - 多机器配置策略
   - 多 Agent 协作规范
   - ...等等 (共 1715 行)

---

## 四、解决方案

### 方案 1：增加 llama.cpp ctx-size (已实施 ✅)

**修改文件**: `core/config/presets/mypresets-cuda.ini`

**变更**:
```ini
# 之前
ctx-size = 12288

# 现在
ctx-size = 512000  # 500K tokens
```

**应用**:
- 重启 `llama-server-8401.service`
- 模型重新加载后生效

**优点**:
- 一次性配置，永久生效
- 支持 Claude Code 的完整上下文

**缺点**:
- 需要更多显存 (KV cache 更大)
- 推理速度可能稍慢

---

### 方案 2：优化 Claude Code 配置 (可选)

可以在 Claude Code 配置中减少发送的上下文量，但这需要用户手动配置。

---

## 五、代理实现改进

### JSONL 日志记录 (已添加 ✅)

为了便于分析和调试，添加了 JSONL 格式的请求/响应日志：

**日志位置**: `core/logs/anthropic-proxy-requests.jsonl`

**日志格式**:
```json
{
  "timestamp": "2026-03-05T01:00:40.716418+08:00",
  "type": "request",
  "request_id": "req_1772643640716335443...",
  "request": { /* 原始 Anthropic 请求 */ }
}
```

```json
{
  "timestamp": "2026-03-05T01:00:41.139835+08:00",
  "type": "response",
  "request_id": "req_1772643640716335443...",
  "llama_status": 200,
  "llama_response": { /* llama.cpp 响应 */ },
  "anthropic_response": { /* 转换后的 Anthropic 响应 */ }
}
```

---

### Go 代理特性

| 特性 | 状态 |
|------|------|
| 基本消息对话 | ✅ |
| System prompt 支持 (string/array) | ✅ |
| 多轮对话 | ✅ |
| Tool/Function Calling | ✅ |
| JSONL 请求/响应日志 | ✅ |
| 监听 0.0.0.0:8402 | ✅ |
| Prometheus metrics endpoint | ✅ |
| Metrics 缓存 (30秒) | ✅ |
| 管理脚本集成 | ✅ |

---

## 六、文件结构

```
llama_cpp/
├── core/
│   ├── go-proxy/
│   │   ├── main.go              # Go 代理源代码
│   │   ├── go.mod               # Go 模块
│   │   └── anthropic-proxy      # 编译后二进制
│   ├── scripts/
│   │   └── anthropic-proxy-go.sh # 管理脚本
│   ├── systemd/
│   │   └── anthropic-proxy-go.service
│   ├── config/
│   │   └── presets/
│   │       └── mypresets-cuda.ini  # ctx-size=512000
│   └── logs/
│       ├── anthropic-proxy-go.log      # 普通日志
│       └── anthropic-proxy-requests.jsonl  # JSONL 请求日志 ⭐
└── docs/
    └── Anthropic-Proxy.md           # 使用文档
```

---

## 七、当前状态

| 项目 | 状态 |
|------|------|
| Go 代理 | ✅ 运行中 (PID: ...) |
| llama.cpp ctx-size | ✅ 512000 (500K) |
| JSONL 日志 | ✅ 已启用 |
| Prometheus metrics | ✅ 已启用 |
| Python 版本 | ⛔ 已删除 |

---

## 八、测试建议

### 基准测试

可以运行以下测试验证代理功能：

```bash
# 完整功能测试
python3 core/scripts/test-proxy-tools.py

# 性能对比测试
python3 core/scripts/test-proxy-benchmark.py
```

### 查看 JSONL 日志

```bash
# 查看最新请求
tail -f core/logs/anthropic-proxy-requests.jsonl

# 解析分析
python3 -c "
import json
with open('core/logs/anthropic-proxy-requests.jsonl') as f:
    for line in f:
        entry = json.loads(line)
        print(entry['type'], entry.get('request_id', '')[:30])
"
```

---

## 九、Prometheus 指标支持 (已添加 ✅)

### 新增 /metrics Endpoint

在 Go 代理中添加了内置的 Prometheus metrics endpoint：

**地址**: `http://localhost:8402/metrics`

**特性**:
- 从 JSONL 日志文件解析指标
- 30 秒缓存，避免频繁读取大文件
- 4MB 缓冲区，支持大 JSONL 条目
- 线程安全，使用 RWMutex

**指标**:

| 指标名称 | 类型 | 说明 |
|----------|------|------|
| `anthropic_proxy_requests_total` | counter | 总请求数 |
| `anthropic_proxy_responses_total` | counter | 总响应数 |
| `anthropic_proxy_errors_total` | counter | 总错误数 |
| `anthropic_proxy_log_file_size` | gauge | JSONL 日志文件大小 (字节) |
| `anthropic_proxy_success_rate` | gauge | 成功率 (百分比) |
| `anthropic_proxy_error_rate` | gauge | 错误率 (百分比) |
| `anthropic_proxy_last_update_time` | gauge | 最后更新时间 (Unix 时间戳) |

### 使用方式

```bash
# 通过 curl 获取
curl http://localhost:8402/metrics

# 或通过管理脚本
./core/scripts/anthropic-proxy-go.sh metrics
./core/scripts/anthropic-proxy-go.sh export-prometheus
```

### Prometheus 配置示例

```yaml
scrape_configs:
  - job_name: 'anthropic_proxy'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:8402']
```

---

## 十、总结

### 问题根源
Claude Code 会在每个请求中附带完整的系统上下文（~/.claude/CLAUDE.md），总计约 35,000 tokens，超过了 llama.cpp 默认的 12,288 tokens 限制。

### 解决方案
1. ✅ **将 llama.cpp 的 `ctx-size` 从 12288 增加到 512000**
2. ✅ **添加 JSONL 格式的请求/响应日志，便于分析**
3. ✅ **添加内置 Prometheus metrics endpoint (`/metrics`)**

### 经验教训
- Claude Code 的上下文量比预期的大得多
- 需要为本地模型配置足够大的 context window
- 完整的请求/响应日志对问题诊断至关重要
- Prometheus metrics 对长期监控非常重要

---

*报告生成时间: 2026-03-05*
