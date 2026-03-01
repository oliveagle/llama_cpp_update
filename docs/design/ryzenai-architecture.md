# RyzenAI-Server 集成架构设计

> **项目**: llama.cpp AMD NPU Linux 支持
> **方案**: RyzenAI-Server 独立进程集成
> **版本**: 1.0
> **日期**: 2026-02-20

---

## 1. 架构概述

### 1.1 设计目标

在 llama.cpp 中集成 AMD NPU 支持，通过复用 Lemonade SDK 的 RyzenAI-Server 实现，支持 ONNX 格式模型在 AMD XDNA NPU 上运行。

### 1.2 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        llama-server                             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │
│  │ CPU Backend │  │ GPU Backend │  │ RyzenAI Backend     │    │
│  │ (ggml-cpu)  │  │ (ggml-vulkan)│ │ (ggml-ryzenai)      │    │
│  └─────────────┘  └─────────────┘  └───────┬─────────────┘    │
│                                            │                    │
│                                    ┌───────▼────────┐          │
│                                    │ ProcessManager │          │
│                                    │ - spawn        │          │
│                                    │ - monitor      │          │
│                                    │ - terminate    │          │
│                                    └───────┬────────┘          │
│                                            │                    │
│                                    ┌───────▼────────┐          │
│                                    │ HTTPClient     │          │
│                                    │ - forward      │          │
│                                    │ - health check │          │
│                                    └───────┬────────┘          │
└────────────────────────────────────────────┼────────────────────┘
                                             │
                                    ┌────────▼────────┐
                                    │ ryzenai-server  │
                                    │ (独立进程)      │
                                    │ 端口：8002      │
                                    ├─────────────────┤
                                    │ ONNX Runtime    │
                                    │ GenAI (OGA)     │
                                    ├─────────────────┤
                                    │ AMD XDNA NPU    │
                                    │ - AIE Tiles     │
                                    │ - DMA Engine    │
                                    └─────────────────┘
```

### 1.3 关键组件

| 组件 | 文件 | 职责 |
|------|------|------|
| **RyzenAI Backend** | `src/ryzenai/ryzenai_backend.h/cpp` | 后端主逻辑 |
| **Process Manager** | `src/ryzenai/process_manager.h/cpp` | 进程生命周期管理 |
| **HTTP Client** | `src/ryzenai/http_client.h/cpp` | HTTP 请求转发 |
| **Downloader** | `src/ryzenai/downloader.h/cpp` | ryzenai-server 下载 |

---

## 2. Lemonade SDK 实现分析

### 2.1 版本配置

```json
// backend_versions.json
{
  "ryzenai-server": "v1.7.0"
}
```

### 2.2 安装流程 (Lemonade `ryzenaiserver.cpp:180-273`)

```cpp
void RyzenAIServer::download_and_install(const std::string& version) {
    // 1. 构建下载 URL
    std::string repo = "lemonade-sdk/ryzenai-server";
    std::string filename = "ryzenai-server.zip";
    std::string url = "https://github.com/" + repo + "/releases/download/"
                      + version + "/" + filename;

    // 2. 下载到用户缓存目录
    fs::path install_dir = get_install_directory();
    std::string zip_path = (fs::path(utils::get_downloaded_bin_dir()) / filename).string();

    // 3. HTTP 下载 (带进度回调)
    auto download_result = utils::HttpClient::download_file(url, zip_path, ...);

    // 4. 解压 ZIP
    BackendUtils::extract_archive(zip_path, install_dir.string(), "RyzenAI-Server");

    // 5. 验证可执行文件
    std::string exe_path = find_executable_in_install_dir(install_dir);

    // 6. 保存版本信息
    std::string version_file = (install_dir / "version.txt").string();
    std::ofstream vf(version_file);
    vf << version;

    // 7. Linux 下设置执行权限
    chmod(exe_path.c_str(), 0755);

    // 8. 清理 ZIP 文件
    fs::remove(zip_path);
}
```

### 2.3 进程启动流程 (Lemonade `ryzenaiserver.cpp:275-353`)

```cpp
void RyzenAIServer::load(const std::string& model_name,
                        const ModelInfo& model_info,
                        const RecipeOptions& options,
                        bool do_not_upgrade) {
    // 1. 安装/检查 ryzenai-server
    install();

    // 2. 获取可执行文件路径
    std::string ryzenai_server_path = get_ryzenai_server_path();

    // 3. 验证模型路径
    if (model_path_.empty()) {
        throw std::runtime_error("Model path is required");
    }

    // 4. 选择端口
    port_ = choose_port();

    // 5. 构建命令行参数
    std::vector<std::string> args = {
        "-m", model_path_,
        "--port", std::to_string(port_),
        "--ctx-size", std::to_string(ctx_size)
    };

    // 6. 启动进程
    process_handle_ = ProcessManager::start_process(
        ryzenai_server_path, args, "", is_debug(), true);

    // 7. 等待服务就绪
    if (!wait_for_ready("/health")) {
        throw std::runtime_error("RyzenAI-Server failed to start");
    }

    is_loaded_ = true;
}
```

### 2.4 HTTP 请求转发 (Lemonade `ryzenaiserver.cpp:376-392`)

```cpp
json RyzenAIServer::chat_completion(const json& request) {
    if (!is_loaded_) {
        throw ModelNotLoadedException("RyzenAI-Server");
    }

    // 转发到 /v1/chat/completions 端点
    return forward_request("/v1/chat/completions", request);
}

json RyzenAIServer::completion(const json& request) {
    if (!is_loaded_) {
        throw ModelNotLoadedException("RyzenAI-Server");
    }

    // 转发到 /v1/completions 端点
    return forward_request("/v1/completions", request);
}
```

### 2.5 健康检查 (Lemonade `WrappedServer::wait_for_ready`)

```cpp
bool WrappedServer::wait_for_ready(const std::string& endpoint) {
    std::string url = get_base_url() + endpoint;

    const int max_attempts = 300;  // 5 分钟超时
    for (int attempt = 0; attempt < max_attempts; ++attempt) {
        if (!utils::ProcessManager::is_running(process_handle_)) {
            return false;  // 进程已终止
        }

        if (utils::HttpClient::is_reachable(url, 1)) {
            return true;  // 服务已就绪
        }
    }

    return false;  // 超时
}
```

---

## 3. llama.cpp 集成设计

### 3.1 目录结构

```
llama.cpp/
├── src/
│   ├── ryzenai/
│   │   ├── CMakeLists.txt
│   │   ├── ryzenai_backend.h
│   │   ├── ryzenai_backend.cpp
│   │   ├── process_manager.h
│   │   ├── process_manager.cpp
│   │   ├── http_client.h
│   │   ├── http_client.cpp
│   │   └── downloader.h
│   └── server.cpp  (修改)
├── CMakeLists.txt  (修改)
└── examples/server/main.cpp  (修改)
```

### 3.2 CMakeLists.txt 集成

**根目录 `CMakeLists.txt`**:
```cmake
# AMD RyzenAI NPU Backend
option(GGML_RYZENAI "Enable AMD RyzenAI NPU backend via RyzenAI-Server" OFF)

if(GGML_RYZENAI)
    add_subdirectory(src/ryzenai)

    target_compile_definitions(llama-common PRIVATE GGML_USE_RYZENAI)
    target_link_libraries(llama-server PRIVATE ryzenai-backend)
endif()
```

**`src/ryzenai/CMakeLists.txt`**:
```cmake
find_package(CURL REQUIRED)

add_library(ryzenai-backend STATIC
    ryzenai_backend.cpp
    process_manager.cpp
    http_client.cpp
    downloader.cpp
)

target_include_directories(ryzenai-backend PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CURL_INCLUDE_DIRS}
)

target_link_libraries(ryzenai-backend PRIVATE
    ${CURL_LIBRARIES}
    llama-common
)

target_compile_features(ryzenai-backend PRIVATE cxx_std_17)
```

### 3.3 RyzenAI Backend 接口

**`ryzenai_backend.h`**:
```cpp
#pragma once

#include <string>
#include <cstdint>
#include <memory>

namespace ryzenai {

struct RyzenAIConfig {
    std::string ryzenai_path;       // ryzenai-server 路径
    std::string model_path;         // ONNX 模型路径
    int ctx_size = 8192;            // 上下文长度
    int port = 0;                   // 0=自动选择
    std::string host = "127.0.0.1"; // 绑定地址
    bool debug = false;             // 调试模式
};

class RyzenAIBackend {
public:
    RyzenAIBackend();
    ~RyzenAIBackend();

    // 检测是否可用
    static bool is_available();

    // 下载 ryzenai-server
    static bool download(const std::string& version = "v1.7.0");

    // 获取 ryzenai-server 路径
    static std::string get_ryzenai_server_path();

    // 初始化后端
    bool init(const RyzenAIConfig& config);

    // 加载模型
    bool load_model();

    // 卸载模型
    void unload_model();

    // 聊天完成
    std::string chat_completion(const std::string& messages,
                                int max_tokens = 512,
                                float temperature = 0.7f);

    // 健康检查
    bool is_healthy() const;

    // 获取状态
    bool is_loaded() const { return m_loaded_; }
    int get_port() const { return m_port_; }

private:
    RyzenAIConfig m_config;
    pid_t m_server_pid = 0;
    int m_port = 0;
    bool m_loaded_ = false;

    // 内部方法
    bool wait_for_ready(int timeout_ms = 30000);
    std::string send_http_request(const std::string& endpoint,
                                  const std::string& body);
    int choose_port();
};

} // namespace ryzenai
```

### 3.4 进程管理器

**`process_manager.h`**:
```cpp
#pragma once

#include <string>
#include <vector>
#include <cstdint>

namespace ryzenai {

struct ProcessHandle {
    pid_t pid = 0;
    bool running = false;
};

class ProcessManager {
public:
    // 启动进程
    static ProcessHandle start_process(
        const std::string& executable,
        const std::vector<std::string>& args,
        bool capture_output = false
    );

    // 检查进程是否运行
    static bool is_running(const ProcessHandle& handle);

    // 停止进程
    static void stop_process(ProcessHandle& handle);

    // 获取退出码
    static int get_exit_code(const ProcessHandle& handle);
};

} // namespace ryzenai
```

**`process_manager.cpp`**:
```cpp
#include "process_manager.h"
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <signal.h>
#include <fcntl.h>

namespace ryzenai {

ProcessHandle ProcessManager::start_process(
    const std::string& executable,
    const std::vector<std::string>& args,
    bool capture_output) {

    ProcessHandle handle;

    // 创建管道
    int pipefd[2];
    if (capture_output && pipe(pipefd) == -1) {
        return handle;
    }

    pid_t pid = fork();
    if (pid == -1) {
        if (capture_output) {
            close(pipefd[0]);
            close(pipefd[1]);
        }
        return handle;
    }

    if (pid == 0) {
        // 子进程
        if (capture_output) {
            close(pipefd[0]);
            dup2(pipefd[1], STDOUT_FILENO);
            dup2(pipefd[1], STDERR_FILENO);
            close(pipefd[1]);
        }

        // 构建 argv
        std::vector<char*> argv;
        argv.push_back(const_cast<char*>(executable.c_str()));
        for (auto& arg : args) {
            argv.push_back(const_cast<char*>(arg.c_str()));
        }
        argv.push_back(nullptr);

        execv(executable.c_str(), argv.data());
        _exit(127);
    }

    // 父进程
    if (capture_output) {
        close(pipefd[1]);
    }

    handle.pid = pid;
    handle.running = true;
    return handle;
}

bool ProcessManager::is_running(const ProcessHandle& handle) {
    if (handle.pid <= 0) return false;

    int status;
    pid_t result = waitpid(handle.pid, &status, WNOHANG);

    if (result == -1) {
        return false;  // 错误
    }
    if (result == 0) {
        return true;   // 仍在运行
    }
    return false;      // 已终止
}

void ProcessManager::stop_process(ProcessHandle& handle) {
    if (handle.pid > 0 && handle.running) {
        kill(handle.pid, SIGTERM);

        // 等待最多 5 秒
        for (int i = 0; i < 50; ++i) {
            if (!is_running(handle)) {
                break;
            }
            usleep(100000);  // 100ms
        }

        // 如果还在运行，强制杀死
        if (is_running(handle)) {
            kill(handle.pid, SIGKILL);
        }
    }

    handle.running = false;
    handle.pid = 0;
}

int ProcessManager::get_exit_code(const ProcessHandle& handle) {
    if (handle.pid <= 0) return -1;

    int status;
    pid_t result = waitpid(handle.pid, &status, WNOHANG);

    if (result > 0 && WIFEXITED(status)) {
        return WEXITSTATUS(status);
    }
    return -1;
}

} // namespace ryzenai
```

### 3.5 HTTP 客户端

**`http_client.h`**:
```cpp
#pragma once

#include <string>

namespace ryzenai {

class HTTPClient {
public:
    // 发送 POST 请求
    static std::string post(const std::string& url,
                           const std::string& body,
                           int timeout_ms = 60000);

    // 发送 GET 请求
    static std::string get(const std::string& url,
                          int timeout_ms = 5000);

    // 检查端点是否可达
    static bool is_reachable(const std::string& url,
                            int timeout_ms = 1000);

private:
    static std::string request(const std::string& method,
                              const std::string& url,
                              const std::string& body,
                              int timeout_ms);
};

} // namespace ryzenai
```

**`http_client.cpp`**:
```cpp
#include "http_client.h"
#include <curl/curl.h>
#include <stdexcept>

namespace ryzenai {

static size_t write_callback(void* ptr, size_t size, size_t nmemb, void* userdata) {
    std::string* response = static_cast<std::string*>(userdata);
    response->append(static_cast<char*>(ptr), size * nmemb);
    return size * nmemb;
}

std::string HTTPClient::request(const std::string& method,
                                const std::string& url,
                                const std::string& body,
                                int timeout_ms) {
    CURL* curl = curl_easy_init();
    if (!curl) {
        throw std::runtime_error("curl_easy_init failed");
    }

    std::string response;
    struct curl_slist* headers = nullptr;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    headers = curl_slist_append(headers, "Accept: application/json");

    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, timeout_ms);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

    if (method == "POST") {
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, body.c_str());
    }

    CURLcode res = curl_easy_perform(curl);

    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);

    if (res != CURLE_OK) {
        throw std::runtime_error("HTTP request failed: " +
                                 std::string(curl_easy_strerror(res)));
    }

    return response;
}

std::string HTTPClient::post(const std::string& url,
                            const std::string& body,
                            int timeout_ms) {
    return request("POST", url, body, timeout_ms);
}

std::string HTTPClient::get(const std::string& url,
                           int timeout_ms) {
    return request("GET", url, "", timeout_ms);
}

bool HTTPClient::is_reachable(const std::string& url, int timeout_ms) {
    try {
        get(url, timeout_ms);
        return true;
    } catch (...) {
        return false;
    }
}

} // namespace ryzenai
```

---

## 4. llama-server 集成

### 4.1 服务器参数

**修改 `examples/server/main.cpp`**:
```cpp
// 添加 RyzenAI 参数
struct ryzenai_params {
    bool use_ryzenai = false;
    std::string ryzenai_model;
    int ryzenai_ctx_size = 8192;
    int ryzenai_port = 0;  // 0 = 自动选择
    bool ryzenai_download = false;  // 下载 ryzenai-server
};

// 在命令行参数解析中添加
if (argc == "--ryzenai") {
    params.ryzenai.use_ryzenai = true;
} else if (argc == "--ryzenai-model") {
    params.ryzenai.ryzenai_model = argv[++i];
} else if (argc == "--ryzenai-ctx-size") {
    params.ryzenai.ryzenai_ctx_size = std::stoi(argv[++i]);
} else if (argc == "--ryzenai-port") {
    params.ryzenai.ryzenai_port = std::stoi(argv[++i]);
} else if (argc == "--ryzenai-download") {
    params.ryzenai.ryzenai_download = true;
}
```

### 4.2 服务器初始化

```cpp
#ifdef GGML_USE_RYZENAI
#include "ryzenai/ryzenai_backend.h"

// 在服务器启动时
if (params.ryzenai.ryzenai_download) {
    std::cout << "Downloading ryzenai-server..." << std::endl;
    if (!ryzenai::RyzenAIBackend::download()) {
        std::cerr << "Failed to download ryzenai-server" << std::endl;
        return 1;
    }
    std::cout << "Download complete!" << std::endl;
    return 0;
}

if (params.ryzenai.use_ryzenai) {
    ryzenai::RyzenAIBackend backend;
    ryzenai::RyzenAIConfig config;
    config.model_path = params.ryzenai.ryzenai_model;
    config.ctx_size = params.ryzenai.ryzenai_ctx_size;
    config.port = params.ryzenai.ryzenai_port;
    config.debug = params.debug;

    if (backend.init(config) && backend.load_model()) {
        printf("RyzenAI backend initialized on port %d\n", backend.get_port());
        // 注册后端到路由器
        router.register_backend("ryzenai", &backend);
    } else {
        fprintf(stderr, "Failed to initialize RyzenAI backend\n");
        return 1;
    }
}
#endif
```

---

## 5. 数据流

### 5.1 请求处理流程

```
用户请求
   │
   ▼
llama-server (端口 8400)
   │
   ▼
路由判断 (模型类型 = ONNX?)
   │
   ├─→ GGUF → Vulkan/CPU 后端
   │
   └─→ ONNX → RyzenAI 后端
              │
              ▼
         HTTPClient::post()
              │
              ▼
         ryzenai-server (端口 8002)
              │
              ▼
         ONNX Runtime GenAI
              │
              ▼
         AMD XDNA NPU
              │
              ▼
         返回响应
```

### 5.2 生命周期管理

```
1. llama-server 启动
   │
2. --ryzenai-download? → 下载 ryzenai-server
   │
3. --ryzenai? → 初始化后端
   │
4. load_model()
   │   ├─ 启动 ryzenai-server 进程
   │   ├─ 等待 /health 端点就绪
   │   └─ 记录端口
   │
5. 处理推理请求
   │   ├─ 转发 HTTP 请求
   │   └─ 返回响应
   │
6. llama-server 退出
   │
7. unload_model()
   │   └─ 停止 ryzenai-server 进程
```

---

## 6. 配置选项

### 6.1 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--ryzenai` | 启用 RyzenAI 后端 | false |
| `--ryzenai-model <path>` | ONNX 模型路径 | - |
| `--ryzenai-ctx-size <n>` | 上下文长度 | 8192 |
| `--ryzenai-port <n>` | ryzenai-server 端口 | 0 (自动) |
| `--ryzenai-download` | 下载 ryzenai-server 并退出 | false |

### 6.2 环境变量

| 变量 | 说明 |
|------|------|
| `LLAMA_RYZENAI_SERVER_BIN` | 自定义 ryzenai-server 路径 |
| `LLAMA_RYZENAI_SERVER_VERSION` | ryzenai-server 版本 |

---

## 7. 错误处理

### 7.1 错误类型

```cpp
namespace ryzenai {

enum class ErrorCode {
    OK = 0,
    RYZENAI_NOT_FOUND,
    RYZENAI_DOWNLOAD_FAILED,
    MODEL_NOT_FOUND,
    PROCESS_START_FAILED,
    PROCESS_CRASHED,
    PORT_UNAVAILABLE,
    HTTP_REQUEST_FAILED,
    TIMEOUT
};

class RyzenAIException : public std::runtime_error {
public:
    RyzenAIException(ErrorCode code, const std::string& message)
        : std::runtime_error(message), code_(code) {}

    ErrorCode code() const { return code_; }

private:
    ErrorCode code_;
};

} // namespace ryzenai
```

### 7.2 错误恢复

```cpp
// 进程崩溃自动重启
if (!ProcessManager::is_running(m_process_handle)) {
    fprintf(stderr, "ryzenai-server crashed, restarting...\n");
    unload_model();
    if (!load_model()) {
        throw RyzenAIException(
            ErrorCode::PROCESS_CRASHED,
            "Failed to restart ryzenai-server"
        );
    }
}
```

---

## 8. 测试计划

### 8.1 单元测试

```cpp
TEST(RyzenAIBackend, IsAvailable) {
    // 测试 ryzenai-server 检测
    EXPECT_FALSE(ryzenai::RyzenAIBackend::is_available());
}

TEST(RyzenAIBackend, Download) {
    // 测试下载
    EXPECT_TRUE(ryzenai::RyzenAIBackend::download("v1.7.0"));
}

TEST(ProcessManager, StartStop) {
    // 测试进程管理
    auto handle = ProcessManager::start_process("/bin/echo", {"hello"});
    EXPECT_TRUE(handle.running);
    EXPECT_FALSE(ProcessManager::is_running(handle));
}
```

### 8.2 集成测试

```bash
# 1. 下载 ryzenai-server
./llama-server --ryzenai-download

# 2. 启动服务
./llama-server --ryzenai \
    --ryzenai-model model.onnx \
    --port 8400

# 3. 测试推理
curl http://localhost:8400/v1/chat/completions \
    -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

---

## 9. 参考资料

- Lemonade SDK: `/tmp/lemonade/src/cpp/server/backends/ryzenaiserver.cpp`
- RyzenAI-Server Releases: https://github.com/lemonade-sdk/ryzenai-server
- ONNX Runtime GenAI: https://github.com/microsoft/onnxruntime-genai
- AMD XDNA DRM: `/usr/src/.../include/uapi/drm/amdxdna_accel.h`

---

*架构设计完成时间：2026-02-20*
