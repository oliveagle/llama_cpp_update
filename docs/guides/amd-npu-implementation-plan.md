# AMD NPU Linux 支持实现计划

> **目标**: 在 llama.cpp 中实现 AMD NPU (XDNA) Linux 支持
> **参考**: Lemonade SDK RyzenAI-Server / FastFlowLM 实现
> **状态**: 计划阶段
> **最后更新**: 2026-02-20 (含 FastFlowLM Linux 分析)

---

## 1. 执行摘要

### 1.1 现状分析

**Lemonade SDK 实现方式**:
- Lemonade 通过 **两个独立后端** 支持 AMD NPU:
  1. **RyzenAI-Server** (OGA 封装) - Windows/Linux, 使用 ONNX 模型
  2. **FastFlowLM (FLM)** - Windows/Linux, 使用 .q4nx 专有格式

**FastFlowLM Linux 支持关键发现**:
- ✅ **Linux 支持已实现**: `fastflowlm_server.cpp` 有完整的 `#elif defined(__linux__)` 分支
- ✅ **内核要求**: 最低内核版本 7.0 (`min_kernel_version: "7.0"`)
- ✅ **驱动检测**: 通过 `/sys/class/accel/*/device/driver` 检测 amdxdna 驱动
- ✅ **命令**: `flm serve <model> --ctx-len 8192 --port 8001 --host 127.0.0.1`
- ⚠️ **限制**: FLM 使用专有 .q4nx 格式，需要 AMD NPU 驱动支持

**RyzenAI-Server Linux 支持**:
- ✅ **独立进程**: 通过 HTTP API 提供服务
- ✅ **模型格式**: ONNX (非 GGUF)
- ✅ **端口选择**: 自动选择本地端口
- ✅ **健康检查**: `/health` 端点

**关键发现**:
1. Lemonade 的 NPU 支持**不是直接集成**到 llama.cpp 中
2. 而是通过**独立服务器进程**方式，通过 HTTP API 通信
3. Linux 下两种方案都可用，但都需要**特定模型格式** (ONNX 或 .q4nx)

### 1.2 推荐实现方案

**方案 A: 独立 NPU 服务器进程 (推荐，2-4 周)**
- 参考 Lemonade 的 RyzenAI-Server / FastFlowLM 架构
- 在 llama.cpp 项目中创建 `npu-server` 独立进程
- 通过 AMD XDNA DRM API 直接与 NPU 通信
- llama-server 通过内部 HTTP/RPC 调用 npu-server

**方案 B: 原生 ggml-npu 后端 (长期，3-6 个月)**
- 在 ggml 层添加 `libggml-npu.so`
- 实现 NPU Kernel (MatMul, Attention, Norm, etc.)
- 需要 AMD XRT 运行时支持

**方案 C: 集成 FastFlowLM (中等，1-2 周)**
- 在 llama-server 中添加 FLM 后端检测
- 通过 `flm serve` 命令启动 NPU 推理
- 需要用户单独安装 FastFlowLM

---

## 2. 硬件和驱动要求

### 2.1 支持的硬件

| NPU 代 | 设备 ID | 内核驱动 | 状态 |
|--------|--------|----------|------|
| Ryzen AI 300 (XDNA) | 1022:1502 | amdxdna | ✅ 已加载 |
| Ryzen AI 300 v2 (XDNA2) | 1022:17F0 | amdxdna | ✅ 已加载 |

您的设备: **Strix Halo Ryzen AI MAX+ 395** [1022:17F0]

### 2.2 驱动要求

**内核驱动** (已存在):
```
amdxdna.ko - /lib/modules/6.14.0-1020-oem/kernel/drivers/accel/amdxdna/
固件：/lib/firmware/amdnpu/17f0_11/npu.sbin
```

**用户态运行时** (需要获取):
- **XRT (Xilinx Runtime)**: 需要从 AMD 获取
- **Vitis AI Runtime**: 用于 ONNX 模型部署
- 或 **RyzenAI-Server** 二进制 (从 Lemonade 提取)

---

## 3. 架构设计

### 3.1 方案 A: 独立 NPU 服务器

```
┌─────────────────────────────────────────────────────────────┐
│                      llama-server                           │
│  (主服务进程，端口 8400)                                     │
├─────────────────────────────────────────────────────────────┤
│  HTTP Router                                                │
│    │                                                        │
│    ├─→ GGUF Models → libggml-vulkan.so (AMD iGPU)          │
│    │                                                        │
│    └─→ ONNX Models → npu-server (HTTP forward)             │
│                          │                                  │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │    npu-server         │                      │
│              │  (独立进程，内部端口)     │                      │
│              ├───────────────────────┤                      │
│              │ AMD XDMA DRM Interface│                      │
│              │ - DRM_IOCTL_AMDXDNA_* │                      │
│              │ - BO 创建/同步/执行     │                      │
│              └───────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| **npu-server** | `src/npu/npu_server.cpp` | NPU 推理服务进程 |
| **NPU Backend** | `ggml/src/ggml-npu/ggml-npu.cpp` | NPU 计算图执行 |
| **DRM Wrapper** | `src/npu/xdna_drm.cpp` | XDNA DRM IOCTL 封装 |
| **模型加载器** | `src/npu/npu_model_loader.cpp` | ONNX 模型加载 |

### 3.3 DRM API 封装

基于内核头文件 `/usr/src/.../include/uapi/drm/amdxdna_accel.h`:

```cpp
// xdna_drm.h - XDNA DRM 接口封装
struct xdna_device {
    int fd;  // DRM 文件描述符

    // 初始化
    int init();

    // 查询 AIE 硬件信息
    int query_aie_metadata(struct amdxdna_drm_query_aie_metadata* meta);

    // 创建硬件上下文
    uint32_t create_hwctx(uint32_t umq_bo, uint32_t log_buf_bo);

    // 创建缓冲区对象 (BO)
    uint32_t create_bo(size_t size, enum amdxdna_bo_type type);

    // 执行命令
    uint64_t exec_cmd(uint32_t hwctx, uint32_t cmd_bo);

    // 同步 BO
    int sync_bo(uint32_t bo, enum amdxdna_sync_direction dir);
};
```

---

## 4. 实现步骤

### 阶段 1: 基础设施 (第 1 周)

#### 任务 1.1: XDNA DRM 封装层

**文件**: `src/npu/xdna_drm.cpp`, `src/npu/xdna_drm.h`

```cpp
// 需要实现的 IOCTL 封装:
// 1. DRM_IOCTL_AMDXDNA_CREATE_HWCTX
// 2. DRM_IOCTL_AMDXDNA_CREATE_BO
// 3. DRM_IOCTL_AMDXDNA_GET_BO_INFO
// 4. DRM_IOCTL_AMDXDNA_SYNC_BO
// 5. DRM_IOCTL_AMDXDNA_EXEC_CMD
// 6. DRM_IOCTL_AMDXDNA_GET_INFO

class XDNADRM {
public:
    XDNADRM();
    ~XDNADRM();

    bool open();
    void close();

    // 上下文管理
    uint32_t createHardwareContext(uint32_t umq_bo, uint32_t log_buf_bo);
    void destroyHardwareContext(uint32_t handle);

    // 缓冲区管理
    uint32_t createBufferObject(size_t size, amdxdna_bo_type type);
    BufferInfo getBufferInfo(uint32_t handle);

    // 执行和同步
    uint64_t executeCommand(uint32_t hwctx, uint32_t cmd_bo);
    void syncBuffer(uint32_t handle, amdxdna_sync_direction dir);

    // 查询
    AieMetadata queryAIEMetadata();
    FirmwareVersion queryFirmwareVersion();

private:
    int m_fd = -1;
};
```

#### 任务 1.2: 构建系统集成

**文件**: `CMakeLists.txt`, `ggml/src/CMakeLists.txt`

```cmake
# 添加 NPU 后端选项
option(GGML_NPU "Enable AMD NPU backend via XDNA DRM" OFF)

if(GGML_NPU)
    add_subdirectory(src/npu)

    # 编译 libggml-npu.so
    add_library(ggml-npu SHARED
        ggml/src/ggml-npu/ggml-npu.cpp
        ggml/src/ggml-npu/ggml-npu-kernels.cpp
    )

    target_link_libraries(ggml-npu PRIVATE drm)
endif()
```

### 阶段 2: NPU 服务器 (第 2 周)

#### 任务 2.1: NPU Server 框架

**文件**: `src/npu/npu_server.cpp`

```cpp
// npu-server 是独立进程，监听本地端口
// 提供 HTTP API:
// POST /v1/chat/completions
// POST /v1/completions
// GET  /health

class NPUServer {
public:
    NPUServer(const std::string& model_path, int port);

    void start();
    void stop();

    // 推理接口
    json chatCompletion(const json& request);
    json completion(const json& request);

private:
    XDNADRM m_drm;
    NPUModel m_model;
    int m_port;
    std::thread m_server_thread;
    bool m_running = false;
};
```

#### 任务 2.2: 模型加载器

**文件**: `src/npu/npu_model_loader.cpp`

```cpp
// 支持 ONNX 模型加载
// 1. 解析 ONNX 图结构
// 2. 映射到 NPU Kernel
// 3. 分配 AIE tile 内存
// 4. 生成命令序列

class NPUModelLoader {
public:
    std::unique_ptr<NPUModel> loadONNXModel(const std::string& path);

private:
    // 将 ONNX 算子映射到 NPU Kernel
    std::map<std::string, NPUKernel> m_kernel_map;

    void mapMatMulKernel(const onnx::NodeProto& node);
    void mapAttentionKernel(const onnx::NodeProto& node);
    void mapNormKernel(const onnx::NodeProto& node);
};
```

### 阶段 3: ggml-npu 后端 (第 3-4 周)

#### 任务 3.1: Backend 初始化

**文件**: `ggml/src/ggml-npu/ggml-npu.cpp`

```cpp
#include "ggml-backend.h"
#include "ggml-backend-impl.h"
#include "ggml-metal.h"  // 参考 Metal 实现

// Backend 接口
static const char* ggml_backend_npu_name(ggml_backend_t backend) {
    return "NPU";
}

static void ggml_backend_npu_free(ggml_backend_t backend) {
    auto* ctx = (NPUContext*)backend->context;
    delete ctx;
    delete backend;
}

static ggml_backend_buffer_type_t ggml_backend_npu_get_buffer_type(ggml_backend_t backend) {
    return ggml_backend_npu_buffer_type();
}

// 计算图执行
static ggml_status ggml_backend_npu_graph_compute(ggml_backend_t backend, ggml_cgraph* cgraph) {
    auto* ctx = (NPUContext*)backend->context;

    // 1. 同步输入数据到 NPU
    ctx->drm->sync_buffers(HOST_TO_DEVICE);

    // 2. 构建命令序列
    ctx->cmd_builder.build(cgraph);

    // 3. 提交到硬件
    uint64_t seq = ctx->drm->exec_cmd(ctx->hwctx, ctx->cmd_bo);

    // 4. 等待完成
    ctx->drm->wait_completion(seq);

    // 5. 同步结果回 Host
    ctx->drm->sync_buffers(DEVICE_TO_HOST);

    return GGML_STATUS_SUCCESS;
}

// Backend 注册
static ggml_backend_i ggml_backend_npu_interface = {
    .get_name = ggml_backend_npu_name,
    .free = ggml_backend_npu_free,
    .get_buffer_type = ggml_backend_npu_get_buffer_type,
    .graph_compute = ggml_backend_npu_graph_compute,
    // ... 其他接口
};

ggml_backend_t ggml_backend_npu_init() {
    auto* drm = new XDNADRM();
    if (!drm->open()) {
        delete drm;
        return nullptr;
    }

    auto* backend = new ggml_backend{
        .device = ggml_backend_npu_device(),
        .context = new NPUContext{drm},
        .iface = ggml_backend_npu_interface
    };

    return backend;
}
```

#### 任务 3.2: Kernel 实现

**文件**: `ggml/src/ggml-npu/ggml-npu-kernels.cpp`

```cpp
// 需要实现的 NPU Kernel:
// 1. Matrix Multiply (GGML_OP_MUL_MAT)
// 2. Attention (GGML_OP_FLASH_ATTN)
// 3. Layer Norm (GGML_OP_NORM)
// 4. RMS Norm (GGML_OP_RMS_NORM)
// 5. Activation (ReLU, SiLU, GeLU)
// 6. RoPE (GGML_OP_ROPE)

struct NPUKernelParams {
    union {
        struct {
            int64_t m, n, k;
            bool transpose_a, transpose_b;
        } matmul;
        struct {
            int64_t n_ctx, n_past;
            int n_head, n_head_kv;
        } attention;
        // ... 其他算子参数
    };
};

class NPUKernel {
public:
    virtual void execute(NPUContext* ctx, ggml_tensor* dst) = 0;

protected:
    void allocate_scratch(size_t size);
    void submit_command();
    void wait_completion();
};

class MatMulKernel : public NPUKernel {
public:
    MatMulKernel(int64_t m, int64_t n, int64_t k);

    void execute(NPUContext* ctx, ggml_tensor* dst) override {
        // 1. 设置输入 BO
        m_src0_bo = ctx->get_bo(dst->src[0]);
        m_src1_bo = ctx->get_bo(dst->src[1]);

        // 2. 设置输出 BO
        m_dst_bo = ctx->allocate_bo(dst->ne[0] * dst->ne[1] * dst->ne[2] * dst->ne[3]);

        // 3. 构建 MatMul 命令
        build_matmul_cmd(ctx->cmd_builder, m_src0_bo, m_src1_bo, m_dst_bo, m_m, m_n, m_k);

        // 4. 提交执行
        submit_and_wait(ctx);

        // 5. 更新输出
        dst->data = ctx->get_host_ptr(m_dst_bo);
    }

private:
    int64_t m_m, m_n, m_k;
    uint32_t m_src0_bo, m_src1_bo, m_dst_bo;
};
```

### 阶段 4: 集成和测试 (第 5 周)

#### 任务 4.1: llama-server 集成

**文件**: `src/server.cpp`

```cpp
// 添加 NPU 后端检测
#ifdef GGML_NPU
#include "ggml-npu.h"

if (params.npu) {
    auto* npu_backend = ggml_backend_npu_init();
    if (npu_backend) {
        log_info("NPU backend initialized\n");
        backends.push_back(npu_backend);
    } else {
        log_warning("NPU backend init failed, falling back to CPU/GPU\n");
    }
}
#endif
```

#### 任务 4.2: 测试用例

**文件**: `tests/test-npu.cmake`

```cmake
# NPU 测试
add_test(NAME test-npu-init
    COMMAND llama-server --npu --help
)

add_test(NAME test-npu-chat
    COMMAND curl http://localhost:8400/v1/chat/completions \\
        -d '{"model": "test-onnx", "messages": [{"role": "user", "content": "Hello"}]}'
)
```

---

## 5. 关键技术挑战

### 5.1 模型格式转换

**问题**: llama.cpp 使用 GGUF 格式，但 NPU 需要 ONNX 格式

**解决方案**:
1. **短期**: 参考 Lemonade，使用 ONNX 模型
2. **中期**: 开发 GGUF → ONNX 转换工具
3. **长期**: 实现 GGUF 原生 NPU 加载

### 5.2 AIE Tile 编程

**问题**: AMD NPU 使用 AIE (AI Engine) tile 架构，需要特殊编程模型

**参考**:
- Lemonade 的 ONNX 模型已经包含 AIE 配置
- 需要理解 AIE tile 的 SRAM 分配和 DMA 传输

### 5.3 内核实现

**问题**: NPU Kernel 需要针对 AIE 架构优化

**策略**:
1. 先实现基础 MatMul (GEMM)
2. 逐步添加 Attention、Norm 等
3. 参考 AMD 提供的 Kernel 库 (如果有)

---

## 6. 依赖获取

### 6.1 必需组件

| 组件 | 来源 | 获取方式 |
|------|------|----------|
| **XDNA DRM 头文件** | Linux 内核 | `/usr/src/.../include/uapi/drm/amdxdna_accel.h` ✅ |
| **libdrm** | 系统包 | `apt install libdrm-dev` |
| **XRT Runtime** | AMD | 需要从 AMD 获取 |
| **ONNX Runtime GenAI** | Microsoft | `pip install onnxruntime-genai` |
| **RyzenAI-Server** | Lemonade | 可从 `/tmp/lemonade` 提取 |

### 6.2 可选组件

| 组件 | 用途 |
|------|------|
| **Vitis AI** | ONNX 模型优化和量化 |
| **amdsmi** | NPU 监控和功率管理 |

---

## 7. 时间估算

| 阶段 | 任务 | 时间 |
|------|------|------|
| **阶段 1** | XDNA DRM 封装、构建系统 | 1 周 |
| **阶段 2** | NPU Server 框架、模型加载器 | 1 周 |
| **阶段 3** | ggml-npu 后端、Kernel 实现 | 2-3 周 |
| **阶段 4** | 集成、测试、文档 | 1 周 |
| **总计** | | **5-6 周** |

---

## 8. FastFlowLM Linux 实现分析

### 8.1 FastFlowLM 架构

FastFlowLM 是 AMD 的专有 NPU 推理引擎，使用 `.q4nx` 量化格式。

**Lemonade 集成方式**:
```cpp
// fastflowlm_server.cpp:179-197
// 通过独立进程启动 flm serve
std::vector<std::string> args = {
    "serve",
    model_info.checkpoint(),  // 模型名称，如 "gemma3:4b"
    "--ctx-len", std::to_string(ctx_size),
    "--port", std::to_string(port_),
    "--host", "127.0.0.1"
};

// 启动进程并等待就绪
process_handle_ = ProcessManager::start_process(flm_path, args, "", is_debug(), true);
wait_for_ready();  // 通过 /api/tags 端点检查
```

### 8.2 Linux 驱动检测

```cpp
// system_info.cpp: Linux NPU 检测
fs::path accel_path = "/sys/class/accel";
for (const auto& entry : fs::directory_iterator(accel_path)) {
    fs::path driver_link = entry.path() / "device" / "driver";
    fs::path driver_path = fs::read_symlink(driver_link);
    std::string driver_name = driver_path.filename().string();

    if (driver_name == "amdxdna") {
        // 读取 NPU 代信息
        fs::path vbnv_file = entry.path() / "device" / "vbnv";
        if (fs::exists(vbnv_file)) {
            std::ifstream vbnv_stream(vbnv_file);
            std::getline(vbnv_stream, vbnv_content);
            npu.name = "AMD NPU (" + vbnv_content + ")";
        }
        npu.available = true;
        break;
    }
}
```

### 8.3 内核版本检查

```cpp
// fastflowlm_server.cpp:470-478, 488-498
#ifdef __linux__
struct utsname uts;
if (uname(&uts) != 0) {
    return "";
}
return std::string(uts.release);  // 返回内核版本，如 "6.14.0-1020-oem"
#endif

// 最低要求：内核 7.0
// backend_versions.json: "min_kernel_version": "7.0"
```

### 8.4 FLM 安装流程

```cpp
// fastflowlm_server.cpp:601-696
bool FastFlowLMServer::install_flm_if_needed() {
    // 1. 检查当前版本
    std::string current_version = get_flm_installed_version();
    std::string required_version = get_flm_required_version();

    // 2. 比较版本，决定是否需要安装/升级
    if (compare_versions(current_version, required_version)) {
        return false;  // 已安装，无需升级
    }

    // 3. 下载安装器
    std::string installer_path = "/tmp/flm-setup";
    download_flm_installer(installer_path);

    // 4. 运行安装器 (Linux 下可能是 shell 脚本)
    run_flm_installer(installer_path, is_upgrade);

    // 5. 验证安装
    verify_flm_installation(required_version);

    return true;
}
```

### 8.5 FLM vs OGA 对比

| 特性 | FastFlowLM | RyzenAI-Server (OGA) |
|------|------------|---------------------|
| **模型格式** | `.q4nx` (专有) | `.onnx` (开放) |
| **Linux 支持** | ✅ 是 | ✅ 是 |
| **内核要求** | ≥7.0 | ≥6.8 |
| **驱动要求** | amdxdna | amdxdna |
| **NPU 代支持** | XDNA2 | XDNA, XDNA2 |
| **性能** | 优化更好 | 标准 ONNX |
| **开源** | ❌ 专有 | ✅ 开源 (部分) |

---

## 9. 下一步行动 (更新)

### 立即可开始

1. **测试 FastFlowLM Linux 可用性**
   ```bash
   # 检查 FLM 是否已安装
   which flm || echo "FLM not installed"

   # 如果已安装，测试 NPU 推理
   flm serve <model> --ctx-len 8192 --port 8001
   ```

2. **获取 RyzenAI-Server 二进制**
   ```bash
   # 从 Lemonade 提取或使用环境变量
   export LEMONADE_RYZENAI_SERVER_BIN=/path/to/ryzenai-server
   ```

3. **安装开发依赖**
   ```bash
   apt install libdrm-dev libonnxruntime-dev
   ```

4. **创建项目结构**
   ```bash
   mkdir -p src/npu ggml/src/ggml-npu
   ```

### 需要 AMD 支持

1. **联系 AMD 获取 XRT 运行时文档**
2. **申请 NPU 开发者访问权限**
3. **获取 AIE Kernel 开发指南**
4. **获取 FastFlowLM Linux SDK** (如有)

---

## 10. 参考资料 (更新)

### 10.1 内核头文件

- `/usr/src/linux-oem-6.14-headers-6.14.0-1017/include/uapi/drm/amdxdna_accel.h`
- `/usr/src/linux-oem-6.14-headers-6.14.0-1017/include/trace/events/amdxdna.h`

### 10.2 Lemonade SDK

- `/tmp/lemonade/src/cpp/server/backends/ryzenaiserver.cpp`
- `/tmp/lemonade/src/cpp/server/backends/fastflowlm_server.cpp`
- `/tmp/lemonade/src/cpp/server/system_info.cpp`
- https://github.com/lemonade-sdk/lemonade

### 10.3 AMD 文档

- https://ryzenai.docs.amd.com/en/latest/
- https://github.com/amd/ryzenai-sw
- https://github.com/FastFlowLM/FastFlowLM

### 10.4 llama.cpp 参考

- `ggml/src/ggml-vulkan/ggml-vulkan.cpp` - Vulkan 后端实现
- `ggml/src/ggml-cuda/ggml-cuda.cu` - CUDA 后端实现

---

*文档创建时间：2026-02-20*
*最后更新：2026-02-20 (含 FastFlowLM Linux 分析)*
