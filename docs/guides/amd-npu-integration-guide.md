# llama.cpp 集成 AMD NPU 支持实施方案

> **摘要**: 基于 Lemonade SDK 经验，在 llama.cpp 中实现 AMD NPU Linux 支持
> **方法**: 分阶段实现，先集成现有方案，再开发原生后端
> **最后更新**: 2026-02-20

---

## 1. 实施方案概述

### 1.1 三阶段策略

```
┌─────────────────────────────────────────────────────────────┐
│  阶段 1: FastFlowLM 集成 (1-2 周) ← 从这里开始              │
│  - 检测系统 FLM 安装                                        │
│  - 通过 flm serve 启动 NPU 推理                             │
│  - HTTP 转发请求                                            │
├─────────────────────────────────────────────────────────────┤
│  阶段 2: RyzenAI-Server 集成 (1-2 周)                       │
│  - 下载/启动 ryzenai-server 进程                            │
│  - ONNX 模型 NPU 推理                                       │
│  - 支持 NPU+iGPU 混合模式                                   │
├─────────────────────────────────────────────────────────────┤
│  阶段 3: 原生 ggml-npu 后端 (2-3 个月)                      │
│  - XDNA DRM 直接通信                                        │
│  - 实现 NPU Kernel                                          │
│  - GGUF 格式原生支持                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 阶段 1: FastFlowLM 集成

### 2.1 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    llama-server                             │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  GPU (Vulkan)│  │   CPU (x64) │  │  NPU (FLM)  │         │
│  │   Backend   │  │   Backend   │  │   Backend   │         │
│  └─────────────┘  └─────────────┘  └──────┬──────┘         │
│                                          │                  │
│                                          ▼                  │
│                              ┌───────────────────┐          │
│                              │  flm-server       │          │
│                              │  (独立进程)       │          │
│                              │  端口：8001       │          │
│                              └───────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 代码实现

#### 2.2.1 FLM 后端检测

**文件**: `src/flm/flm_backend.h`

```cpp
#pragma once

#include <string>
#include <vector>
#include <cstdint>

namespace flm {

struct FLMConfig {
    std::string flm_path;           // flm 可执行文件路径
    std::string model_checkpoint;   // 模型名称，如 "gemma3:4b"
    int ctx_len = 8192;             // 上下文长度
    int port = 8001;                // 服务端口
    std::string host = "127.0.0.1"; // 绑定地址
    bool debug = false;             // 调试模式
};

class FLMBackend {
public:
    FLMBackend();
    ~FLMBackend();

    // 检测 FLM 是否已安装
    static bool is_available();

    // 获取 flm 可执行文件路径
    static std::string get_flm_path();

    // 获取最低内核版本要求
    static std::string get_min_kernel_version();

    // 检测当前内核版本
    static std::string get_current_kernel_version();

    // 检查 NPU 驱动/内核是否满足要求
    static bool check_npu_driver();

    // 初始化后端
    bool init(const FLMConfig& config);

    // 加载模型
    bool load_model();

    // 卸载模型
    void unload_model();

    // 推理请求
    std::string chat_completion(const std::string& prompt,
                                int max_tokens = 512,
                                float temperature = 0.7f);

    // 健康检查
    bool is_healthy();

private:
    FLMConfig m_config;
    pid_t m_server_pid = 0;
    bool m_loaded = false;

    // 等待服务器就绪
    bool wait_for_ready(int timeout_ms = 30000);

    // 发送 HTTP 请求
    std::string send_http_request(const std::string& endpoint,
                                  const std::string& body);
};

} // namespace flm
```

#### 2.2.2 FLM 后端实现

**文件**: `src/flm/flm_backend.cpp`

```cpp
#include "flm_backend.h"
#include <unistd.h>
#include <sys/utsname.h>
#include <sys/wait.h>
#include <fstream>
#include <thread>
#include <chrono>
#include <cstdlib>

// 简化的 HTTP 客户端实现 (可使用 libcurl)
#include <curl/curl.h>

namespace flm {

static std::string receive_response(CURL* curl, const std::string& url,
                                    const std::string& body) {
    std::string response;
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, body.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, [](void* ptr, size_t size,
                            size_t nmemb, void* userp) -> size_t {
        ((std::string*)userp)->append((char*)ptr, size * nmemb);
        return size * nmemb;
    });
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

    CURLcode res = curl_easy_perform(curl);
    if (res != CURLE_OK) {
        throw std::runtime_error("HTTP request failed: " +
                                 std::string(curl_easy_strerror(res)));
    }
    return response;
}

bool FLMBackend::is_available() {
    return !get_flm_path().empty();
}

std::string FLMBackend::get_flm_path() {
    // 在 PATH 中查找 flm
    const char* path_env = std::getenv("PATH");
    if (!path_env) return "";

    std::string path_list(path_env);
    std::vector<std::string> paths;
    size_t start = 0;
    while ((start = path_list.find(':', start)) != std::string::npos) {
        size_t end = path_list.find(':', start + 1);
        if (end == std::string::npos) end = path_list.length();
        std::string dir = path_list.substr(start + 1, end - start - 1);
        std::string flm_path = dir + "/flm";
        if (access(flm_path.c_str(), X_OK) == 0) {
            return flm_path;
        }
        start = end;
    }
    return "";
}

std::string FLMBackend::get_min_kernel_version() {
    return "7.0";  // 来自 backend_versions.json
}

std::string FLMBackend::get_current_kernel_version() {
    struct utsname uts;
    if (uname(&uts) != 0) {
        return "";
    }
    return std::string(uts.release);
}

bool FLMBackend::check_npu_driver() {
    std::string current = get_current_kernel_version();
    std::string min = get_min_kernel_version();

    if (current.empty()) {
        std::cerr << "[FLM] 无法检测内核版本，假设满足要求" << std::endl;
        return true;
    }

    std::cout << "[FLM] 内核版本：" << current
              << " (最低要求：" << min << ")" << std::endl;

    // 简单版本比较 (只比较主版本.次版本)
    int major_cur = 0, minor_cur = 0;
    int major_min = 0, minor_min = 0;

    sscanf(current.c_str(), "%d.%d", &major_cur, &minor_cur);
    sscanf(min.c_str(), "%d.%d", &major_min, &minor_min);

    if (major_cur > major_min) return true;
    if (major_cur == major_min && minor_cur >= minor_min) return true;

    std::cerr << "[FLM] 错误：内核版本过低，需要 " << min << " 或更高" << std::endl;
    return false;
}

bool FLMBackend::init(const FLMConfig& config) {
    m_config = config;

    // 检查 FLM 是否可用
    if (!is_available()) {
        std::cerr << "[FLM] 错误：未找到 flm 可执行文件" << std::endl;
        return false;
    }

    // 检查 NPU 驱动
    if (!check_npu_driver()) {
        std::cerr << "[FLM] 错误：NPU 驱动检查失败" << std::endl;
        return false;
    }

    m_config.flm_path = get_flm_path();
    std::cout << "[FLM] 找到 flm：" << m_config.flm_path << std::endl;
    return true;
}

bool FLMBackend::load_model() {
    std::cout << "[FLM] 加载模型：" << m_config.model_checkpoint << std::endl;

    // 构建命令
    std::vector<std::string> args = {
        m_config.flm_path,
        "serve",
        m_config.model_checkpoint,
        "--ctx-len", std::to_string(m_config.ctx_len),
        "--port", std::to_string(m_config.port),
        "--host", m_config.host
    };

    if (m_config.debug) {
        args.push_back("--debug");
    }

    // 打印命令
    std::cout << "[FLM] 启动命令：";
    for (const auto& arg : args) {
        std::cout << " " << arg;
    }
    std::cout << std::endl;

    // 创建管道用于子进程输出
    int pipefd[2];
    if (pipe(pipefd) == -1) {
        std::cerr << "[FLM] 创建管道失败" << std::endl;
        return false;
    }

    // Fork 子进程
    pid_t pid = fork();
    if (pid == -1) {
        std::cerr << "[FLM] fork 失败" << std::endl;
        close(pipefd[0]);
        close(pipefd[1]);
        return false;
    }

    if (pid == 0) {
        // 子进程
        close(pipefd[0]);  // 关闭读端
        dup2(pipefd[1], STDOUT_FILENO);
        dup2(pipefd[1], STDERR_FILENO);
        close(pipefd[1]);

        // 构建 argv
        std::vector<char*> argv;
        for (auto& arg : args) {
            argv.push_back(const_cast<char*>(arg.c_str()));
        }
        argv.push_back(nullptr);

        // 执行
        execv(args[0].c_str(), argv.data());

        // 如果 execv 返回，说明失败
        std::cerr << "[FLM] execv 失败：" << strerror(errno) << std::endl;
        exit(1);
    }

    // 父进程
    close(pipefd[1]);  // 关闭写端
    m_server_pid = pid;

    // 等待服务器就绪
    if (!wait_for_ready()) {
        std::cerr << "[FLM] 服务器启动失败" << std::endl;
        kill(pid, SIGTERM);
        close(pipefd[0]);
        return false;
    }

    m_loaded = true;
    std::cout << "[FLM] 模型已加载，端口：" << m_config.port << std::endl;
    return true;
}

bool FLMBackend::wait_for_ready(int timeout_ms) {
    std::string url = "http://" + m_config.host + ":" +
                      std::to_string(m_config.port) + "/api/tags";

    CURL* curl = curl_easy_init();
    if (!curl) {
        std::cerr << "[FLM] curl 初始化失败" << std::endl;
        return false;
    }

    curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, 1000);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);

    int elapsed = 0;
    while (elapsed < timeout_ms) {
        std::string response;
        try {
            receive_response(curl, url, "");
            std::cout << "[FLM] 服务器已就绪" << std::endl;
            curl_easy_cleanup(curl);
            return true;
        } catch (...) {
            // 服务器还未就绪
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        elapsed += 500;

        if (elapsed % 5000 == 0) {
            std::cout << "[FLM] 等待服务器启动... ("
                      << (elapsed/1000) << "s)" << std::endl;
        }
    }

    curl_easy_cleanup(curl);
    return false;
}

std::string FLMBackend::chat_completion(const std::string& prompt,
                                        int max_tokens, float temperature) {
    if (!m_loaded) {
        throw std::runtime_error("FLM 模型未加载");
    }

    std::string url = "http://" + m_config.host + ":" +
                      std::to_string(m_config.port) + "/v1/chat/completions";

    std::string body = R"({
        "model": ")" + m_config.model_checkpoint + R"(",
        "messages": [{"role": "user", "content": ")" + prompt + R"("}],
        "max_tokens": )" + std::to_string(max_tokens) + R"(,
        "temperature": )" + std::to_string(temperature) + R"(
    })";

    return send_http_request(url, body);
}

void FLMBackend::unload_model() {
    if (m_server_pid > 0) {
        std::cout << "[FLM] 停止服务器 (PID: " << m_server_pid << ")" << std::endl;
        kill(m_server_pid, SIGTERM);
        waitpid(m_server_pid, nullptr, 0);
        m_server_pid = 0;
    }
    m_loaded = false;
}

bool FLMBackend::is_healthy() {
    if (!m_loaded) return false;

    std::string url = "http://" + m_config.host + ":" +
                      std::to_string(m_config.port) + "/api/tags";

    CURL* curl = curl_easy_init();
    if (!curl) return false;

    curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, 1000);
    curl_easy_setopt(curl, CURLOPT_NOBODY, 1L);

    CURLcode res = curl_easy_perform(curl);
    curl_easy_cleanup(curl);

    return (res == CURLE_OK);
}

std::string FLMBackend::send_http_request(const std::string& endpoint,
                                          const std::string& body) {
    CURL* curl = curl_easy_init();
    if (!curl) {
        throw std::runtime_error("curl 初始化失败");
    }

    struct curl_slist* headers = nullptr;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    headers = curl_slist_append(headers, "Accept: application/json");

    std::string response = receive_response(curl, endpoint, body);

    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);

    return response;
}

} // namespace flm
```

### 2.3 CMakeLists.txt 集成

**文件**: `src/CMakeLists.txt` (追加)

```cmake
# AMD NPU 支持 (FastFlowLM)
option(LLAMA_FLM "Enable FastFlowLM NPU backend" OFF)

if(LLAMA_FLM)
    find_package(CURL REQUIRED)

    add_library(llama-flm STATIC
        flm/flm_backend.cpp
    )

    target_include_directories(llama-flm PRIVATE
        ${CURL_INCLUDE_DIRS}
    )

    target_link_libraries(llama-flm PRIVATE
        ${CURL_LIBRAR}
    )

    target_compile_definitions(llama-flm PRIVATE
        GGML_USE_FLM
    )
endif()
```

### 2.4 llama-server 集成

**文件**: `examples/server/server.cpp` (修改)

```cpp
#ifdef GGML_USE_FLM
#include "flm/flm_backend.h"
#endif

// 在服务器参数中添加
struct server_params {
    // ... 现有参数 ...

#ifdef GGML_USE_FLM
    bool flm = false;
    std::string flm_model;
    int flm_ctx_len = 8192;
    int flm_port = 8001;
#endif
};

// 在服务器启动时初始化
#ifdef GGML_USE_FLM
if (params.flm) {
    flm::FLMBackend flm_backend;
    flm::FLMConfig config;
    config.model_checkpoint = params.flm_model;
    config.ctx_len = params.flm_ctx_len;
    config.port = params.flm_port;
    config.debug = params.debug;

    if (flm_backend.init(config) && flm_backend.load_model()) {
        log_info("FLM NPU backend initialized\n");
        // 注册 FLM 后端到路由器
        router.register_backend("flm", &flm_backend);
    } else {
        log_warning("FLM backend init failed, falling back to CPU/GPU\n");
    }
}
#endif
```

---

## 3. 阶段 2: RyzenAI-Server 集成

### 3.1 架构设计

与 FLM 类似，RyzenAI-Server 也是独立进程，但使用 ONNX 模型。

```
┌─────────────────────────────────────────────────────────────┐
│                    llama-server                             │
│                                                             │
│  ┌─────────────┐  ┌─────────────────────────────┐          │
│  │  GGUF Models│  │   ONNX Models (NPU)         │          │
│  │   (Vulkan)  │  │   → RyzenAI-Server          │          │
│  └─────────────┘  └──────────────┬──────────────┘          │
│                                 │                           │
│                                 ▼                           │
│                    ┌───────────────────────┐                │
│                    │  ryzenai-server       │                │
│                    │  (独立进程，内部端口)   │                │
│                    │  ONNX Runtime GenAI   │                │
│                    └───────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 代码实现

**文件**: `src/ryzenai/ryzenai_backend.h`

```cpp
#pragma once

#include <string>
#include <cstdint>

namespace ryzenai {

struct RyzenAIConfig {
    std::string ryzenai_path;       // ryzenai-server 路径
    std::string onnx_model_path;    // ONNX 模型路径
    int ctx_size = 8192;
    int port = 8002;
    std::string host = "127.0.0.1";
    bool debug = false;
};

class RyzenAIBackend {
public:
    RyzenAIBackend();
    ~RyzenAIBackend();

    // 检测是否可用
    static bool is_available();

    // 获取/下载 ryzenai-server
    static std::string get_or_download_ryzenai_server();

    // 初始化
    bool init(const RyzenAIConfig& config);

    // 加载 ONNX 模型
    bool load_model();

    // 卸载
    void unload();

    // 推理
    std::string chat_completion(const std::string& prompt,
                                int max_tokens = 512,
                                float temperature = 0.7f);

private:
    RyzenAIConfig m_config;
    pid_t m_server_pid = 0;
    bool m_loaded = false;

    bool wait_for_ready(int timeout_ms = 30000);
    std::string send_http_request(const std::string& endpoint,
                                  const std::string& body);
};

} // namespace ryzenai
```

---

## 4. 阶段 3: 原生 ggml-npu 后端

参考实现计划文档中的详细设计。

---

## 5. 测试计划

### 5.1 FLM 集成测试

```bash
# 1. 检测 FLM
./llama-server --flm-detect

# 2. 加载 FLM 模型
./llama-server --flm --flm-model "gemma3:4b" --port 8400

# 3. 测试推理
curl http://localhost:8400/v1/chat/completions \
  -d '{"model": "gemma3:4b", "messages": [{"role": "user", "content": "Hello"}]}'
```

### 5.2 RyzenAI-Server 测试

```bash
# 1. 下载 RyzenAI-Server
./llama-server --ryzenai-download

# 2. 加载 ONNX 模型
./llama-server --ryzenai --model "model.onnx" --port 8400

# 3. 测试推理
curl http://localhost:8400/v1/chat/completions \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

---

## 6. 构建说明

### 6.1 Linux 构建

```bash
# 安装依赖
sudo apt install libcurl4-openssl-dev

# 启用 FLM 后端
cmake -B build -DLLAMA_FLM=ON

# 启用 RyzenAI 后端
cmake -B build -DLLAMA_RYZENAI=ON

# 构建
cmake --build build --config Release
```

### 6.2 模型获取

**FLM 模型**:
```bash
flm pull gemma3:4b
```

**ONNX 模型**:
```bash
# 从 HuggingFace 下载
# https://huggingface.co/collections/amd/ryzenai-15-llm-npu-models-6859846d7c13f81298990db0
```

---

## 7. 故障排除

### 7.1 FLM 问题

| 问题 | 解决方案 |
|------|----------|
| `flm not found` | 安装 FastFlowLM: 参考 https://github.com/FastFlowLM/FastFlowLM |
| 内核版本过低 | 升级到 Linux 内核 7.0+ |
| 模型加载失败 | 检查 NPU 驱动：`lsmod | grep amdxdna` |

### 7.2 RyzenAI-Server 问题

| 问题 | 解决方案 |
|------|----------|
| 二进制不存在 | 运行 `--ryzenai-download` |
| ONNX 模型不兼容 | 使用 AMD 官方转换的模型 |
| 端口冲突 | 修改 `--ryzenai-port` |

---

*文档创建时间：2026-02-20*
