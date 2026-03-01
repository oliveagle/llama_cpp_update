# RuvLTRA Agent 路由模型使用指南

## 概述

[RuvLTRA](https://www.modelscope.cn/models/hf/ruv-ruvltra) 是一个专门为 **Claude Code Agent 调度**设计的模型，能达到 **100% 路由准确率** 和 **<1ms 推理延迟**。

### 核心特性

| 特性 | 说明 |
|------|------|
| **用途** | 智能路由任务到最合适的 Agent |
| **准确率** | 混合路由 (关键词 + 嵌入) 100% |
| **速度** | <1ms 推理延迟 |
| **大小** | 0.5B 版本仅 400MB (Q4_K_M) |
| **架构** | 基于 Qwen2.5 微调 |
| **支持 Agents** | 60+ 预定义 Agent 类型 |

### 模型文件

```
models/ruvltra/
├── ruvltra-claude-code-0.5b-q4_k_m.gguf  ← 推荐用于路由 (400MB)
├── ruvltra-small-0.5b-q4_k_m.gguf        ← 通用嵌入 (400MB)
└── ruvltra-medium-1.1b-q4_k_m.gguf       ← 完整 LLM 推理 (1GB)
```

---

## 快速开始

### 1. 启动服务

```bash
cd /mnt/volume3/llama_cpp
./bin/llama-server-ruvltra.sh start
```

### 2. 测试服务

```bash
# 测试 API
curl http://localhost:8402/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Route: implement user authentication"}],
    "max_tokens": 256
  }'
```

### 3. 使用 Python 脚本路由

```bash
# 测试路由
python3 scripts/ruvltra_router.py "实现用户认证"
python3 scripts/ruvltra_router.py "修复内存泄漏"
python3 scripts/ruvltra_router.py "添加单元测试"
```

---

## Systemd 服务部署

### 创建服务文件

```bash
sudo cat > /etc/systemd/system/ruvltra-8402.service << 'EOF'
[Unit]
Description=RuvLTRA Agent Routing Service
After=network.target

[Service]
Type=notify
WorkingDirectory=/mnt/volume3/llama_cpp
ExecStart=/mnt/volume3/llama_cpp/downloads/llama-b8069/llama-server \
    --model /mnt/volume3/llama_cpp/models/ruvltra/ruvltra-claude-code-0.5b-q4_k_m.gguf \
    --host 0.0.0.0 \
    --port 8402 \
    --ctx-size 4096 \
    --n-predict 512 \
    --n-threads 4 \
    --batch-size 2048 \
    --cache-type-k q8_0 \
    --cache-type-v q8_0

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

### 启用服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable ruvltra-8402
sudo systemctl start ruvltra-8402
sudo systemctl status ruvltra-8402
```

---

## 支持的 Agent 类型

### 核心开发
| Agent | 用途 | 触发关键词 |
|-------|------|------------|
| `coder` | 通用代码开发 | 实现，开发，编写，创建，添加 |
| `reviewer` | 代码审查 | 审查，检查，review, 代码质量 |
| `tester` | 测试编写 | 测试，单元测试，集成测试，bug |
| `debugger` | 调试修复 | 调试，修复，错误，问题 |

### 架构设计
| Agent | 用途 | 触发关键词 |
|-------|------|------------|
| `system-architect` | 系统架构 | 架构，设计，系统，模块，微服务 |
| `backend-dev` | 后端开发 | 后端，API, 数据库，服务器 |
| `frontend-dev` | 前端开发 | 前端，界面，UI, React, Vue |

### 安全
| Agent | 用途 | 触发关键词 |
|-------|------|------------|
| `security-architect` | 安全设计 | 安全，认证，授权，加密，jwt |
| `security-auditor` | 安全审计 | 安全审计，漏洞，渗透测试 |

### 性能
| Agent | 用途 | 触发关键词 |
|-------|------|------------|
| `performance-optimizer` | 性能优化 | 优化，性能，加速，缓存 |

### DevOps
| Agent | 用途 | 触发关键词 |
|-------|------|------------|
| `cicd-engineer` | CI/CD | CI/CD, 部署，流水线 |
| `release-manager` | 版本发布 | 发布，版本，changelog |

---

## API 使用

### 1. 聊天完成（推荐）

```bash
curl http://localhost:8402/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ruvltra",
    "messages": [{
      "role": "user",
      "content": "Route: implement OAuth2 authentication"
    }],
    "max_tokens": 256,
    "temperature": 0.1
  }'
```

### 2. 嵌入向量

```bash
curl http://localhost:8402/embedding \
  -H "Content-Type: application/json" \
  -d '{"content": "fix the memory leak"}'
```

### 3. 文本补全

```bash
curl http://localhost:8402/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Route this: add unit tests",
    "max_tokens": 128
  }'
```

---

## Python 集成示例

### 简单路由

```python
import urllib.request
import json

def route_task(query: str) -> dict:
    url = "http://localhost:8402/v1/chat/completions"
    prompt = f"""Route this task to the best agent.
Available: coder, reviewer, tester, architect, security
Task: {query}
Return: JSON with agent name and confidence"""

    data = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 128,
        "temperature": 0.1
    }).encode()

    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# 使用
result = route_task("实现 JWT 认证")
print(result)
```

### 嵌入相似度匹配

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def get_embedding(text: str) -> np.ndarray:
    url = "http://localhost:8402/embedding"
    data = json.dumps({"content": text}).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        return np.array(result["embedding"])

# 预定义 Agent 描述
agent_descs = {
    "coder": "编写和实现代码功能",
    "tester": "编写测试用例和验证",
    "security": "安全认证和授权设计"
}

# 计算相似度
query_emb = get_embedding("添加用户登录功能")
agent_embs = {k: get_embedding(v) for k, v in agent_descs.items()}

similarities = {k: cosine_similarity([query_emb], [emb])[0][0]
                for k, emb in agent_embs.items()}

best_agent = max(similarities, key=similarities.get)
print(f"推荐 Agent: {best_agent}, 相似度：{similarities[best_agent]:.3f}")
```

---

## 混合路由策略

RuvLTRA 的最佳实践是结合 **关键词匹配** + **嵌入相似度**：

```python
def hybrid_route(query: str) -> dict:
    """
    混合路由策略:
    1. 首先尝试关键词匹配 (快速，准确)
    2. 如果关键词不足，使用嵌入相似度
    3. 返回综合决策
    """
    # 1. 关键词匹配
    keyword_result = keyword_match(query)

    # 2. 嵌入相似度
    embedding = get_embedding(query)
    similarity_result = similarity_match(embedding)

    # 3. 综合决策
    if keyword_result["score"] >= 2:
        return keyword_result  # 关键词足够，直接返回
    elif embedding:
        return similarity_result  # 使用嵌入结果
    else:
        return {"agent": "coder", "confidence": 0.5}  # 默认
```

---

## 多 Agent 协作集成

### Claude Code 技能集成

```python
class AgentRouter:
    """RuvLTRA 驱动的多 Agent 路由"""

    def __init__(self, api_url: str = "http://localhost:8402"):
        self.api_url = api_url
        self.agent_taxonomy = self._load_taxonomy()

    def _load_taxonomy(self) -> dict:
        """加载 Agent 分类"""
        return {
            "coder": {"keywords": ["实现", "开发", "编写"], "desc": "代码开发"},
            "reviewer": {"keywords": ["审查", "检查"], "desc": "代码审查"},
            # ... 更多 Agent
        }

    def route(self, task: str) -> dict:
        """路由任务到最佳 Agent"""
        # 实现混合路由逻辑
        pass

    async def dispatch(self, task: str) -> str:
        """路由并 dispatch 到选中的 Agent"""
        routing = self.route(task)
        agent = routing["recommended_agent"]
        return f"Dispatching to: {agent}"
```

---

## 性能基准

| 操作 | 延迟 | 吞吐量 |
|------|------|--------|
| 查询分解 | 340 ns | 2.9M/s |
| 缓存查找 | 23.5 ns | 42.5M/s |
| 嵌入 (384d) | 293 ns | 3.4M/s |
| 端到端路由 | <1 ms | 1K+/s |

---

## 故障排查

### 服务未启动

```bash
# 检查状态
./bin/llama-server-ruvltra.sh status

# 查看日志
./bin/llama-server-ruvltra.sh logs

# 重启服务
./bin/llama-server-ruvltra.sh restart
```

### 模型加载失败

```bash
# 检查模型文件
ls -la models/ruvltra/

# 重新下载
huggingface-cli download ruv/ruvltra \
    ruvltra-claude-code-0.5b-q4_k_m.gguf \
    --local-dir models/ruvltra
```

### API 无响应

```bash
# 测试端口
curl http://localhost:8402/health

# 检查进程
ps aux | grep llama-server

# 查看系统日志
journalctl -u ruvltra-8402 -f
```

---

## 参考资料

- [RuvLTRA 文档](https://github.com/ruvnet/ruvllm)
- [Claude Flow 项目](https://github.com/ruvnet/claude-flow)
- [Rust 实现](https://crates.io/crates/ruvllm)
- [npm 包](https://www.npmjs.com/package/@ruvector/ruvllm)

---

*最后更新：2026-02-20*
