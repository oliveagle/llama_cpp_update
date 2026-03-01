#include "ryzenai_backend.h"
#include "process_manager.h"
#include "http_client.h"
#include "downloader.h"

#include <iostream>
#include <fstream>
#include <filesystem>
#include <thread>
#include <chrono>
#include <random>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <cstring>

namespace fs = std::filesystem;

namespace ryzenai {

RyzenAIBackend::RyzenAIBackend() = default;

RyzenAIBackend::~RyzenAIBackend() {
    if (m_loaded_) {
        unload_model();
    }
}

bool RyzenAIBackend::is_available() {
    try {
        std::string path = get_ryzenai_server_path();
        return !path.empty() && fs::exists(path);
    } catch (...) {
        return false;
    }
}

bool RyzenAIBackend::download(const std::string& version) {
    try {
        std::string install_dir = Downloader::get_install_directory();
        return Downloader::download_and_install(version, install_dir);
    } catch (const std::exception& e) {
        std::cerr << "[RyzenAI] Download failed: " << e.what() << std::endl;
        return false;
    }
}

std::string RyzenAIBackend::get_ryzenai_server_path() {
    // 1. Check environment variable
    const char* env_path = std::getenv("LLAMA_RYZENAI_SERVER_BIN");
    if (env_path && fs::exists(env_path)) {
        return env_path;
    }

    // 2. Check install directory
    std::string install_dir = Downloader::get_install_directory();
    fs::path exe_path = fs::path(install_dir) / "ryzenai-server";

    if (fs::exists(exe_path)) {
        return exe_path.string();
    }

    // 3. Check PATH
    const char* path_env = std::getenv("PATH");
    if (path_env) {
        std::string path_list(path_env);
        size_t start = 0;
        while (true) {
            size_t end = path_list.find(':', start);
            if (end == std::string::npos) {
                end = path_list.length();
            }
            std::string dir = path_list.substr(start, end - start);
            fs::path candidate = fs::path(dir) / "ryzenai-server";
            if (fs::exists(candidate)) {
                return candidate.string();
            }
            if (end == path_list.length()) break;
            start = end + 1;
        }
    }

    throw RyzenAIException(
        ErrorCode::RYZENAI_NOT_FOUND,
        "ryzenai-server not found. Run with --ryzenai-download to install."
    );
}

bool RyzenAIBackend::init(const RyzenAIConfig& config) {
    m_config = config;

    // Check if ryzenai-server is available
    if (!is_available()) {
        std::cerr << "[RyzenAI] ryzenai-server not found" << std::endl;
        return false;
    }

    m_config.ryzenai_path = get_ryzenai_server_path();
    std::cout << "[RyzenAI] Found ryzenai-server at: " << m_config.ryzenai_path << std::endl;

    // Verify model path
    if (!m_config.model_path.empty() && !fs::exists(m_config.model_path)) {
        std::cerr << "[RyzenAI] Model not found: " << m_config.model_path << std::endl;
        return false;
    }

    // Choose port if not specified
    if (m_config.port == 0) {
        m_port = choose_port();
        if (m_port == 0) {
            std::cerr << "[RyzenAI] Failed to find available port" << std::endl;
            return false;
        }
        m_config.port = m_port;
    } else {
        m_port = m_config.port;
    }

    std::cout << "[RyzenAI] Using port: " << m_port << std::endl;
    return true;
}

bool RyzenAIBackend::load_model() {
    if (m_loaded_) {
        std::cout << "[RyzenAI] Model already loaded" << std::endl;
        return true;
    }

    std::cout << "[RyzenAI] Loading model: " << m_config.model_path << std::endl;

    // Build command line arguments
    std::vector<std::string> args = {
        "-m", m_config.model_path,
        "--port", std::to_string(m_config.port),
        "--ctx-size", std::to_string(m_config.ctx_size),
        "--host", m_config.host
    };

    if (m_config.debug) {
        args.push_back("--verbose");
    }

    // Print command
    std::cout << "[RyzenAI] Starting: " << m_config.ryzenai_path;
    for (const auto& arg : args) {
        std::cout << " " << arg;
    }
    std::cout << std::endl;

    // Start process
    ProcessHandle handle = ProcessManager::start_process(
        m_config.ryzenai_path, args, m_config.debug);

    if (handle.pid <= 0) {
        std::cerr << "[RyzenAI] Failed to start process" << std::endl;
        return false;
    }

    m_server_pid = handle.pid;

    // Wait for server to be ready
    if (!wait_for_ready()) {
        std::cerr << "[RyzenAI] Server failed to start" << std::endl;
        ProcessManager::stop_process(handle);
        m_server_pid = 0;
        return false;
    }

    m_loaded_ = true;
    std::cout << "[RyzenAI] Model loaded successfully" << std::endl;
    return true;
}

void RyzenAIBackend::unload_model() {
    if (!m_loaded_) {
        return;
    }

    std::cout << "[RyzenAI] Unloading model..." << std::endl;

    if (m_server_pid > 0) {
        ProcessHandle handle;
        handle.pid = m_server_pid;
        handle.running = true;
        ProcessManager::stop_process(handle);
    }

    m_server_pid = 0;
    m_port = 0;
    m_loaded_ = false;
}

std::string RyzenAIBackend::chat_completion(const std::string& messages,
                                            int max_tokens,
                                            float temperature) {
    if (!m_loaded_) {
        throw RyzenAIException(ErrorCode::PROCESS_CRASHED, "Model not loaded");
    }

    std::string url = "http://" + m_config.host + ":" +
                      std::to_string(m_port) + "/v1/chat/completions";

    std::string body = R"({
        "messages": )" + messages + R"(,
        "max_tokens": )" + std::to_string(max_tokens) + R"(,
        "temperature": )" + std::to_string(temperature) + R"(
    })";

    return send_http_request(url, body);
}

std::string RyzenAIBackend::completion(const std::string& prompt,
                                       int max_tokens,
                                       float temperature) {
    if (!m_loaded_) {
        throw RyzenAIException(ErrorCode::PROCESS_CRASHED, "Model not loaded");
    }

    std::string url = "http://" + m_config.host + ":" +
                      std::to_string(m_port) + "/v1/completions";

    std::string body = R"({
        "prompt": ")" + prompt + R"(",
        "max_tokens": )" + std::to_string(max_tokens) + R"(,
        "temperature": )" + std::to_string(temperature) + R"(
    })";

    return send_http_request(url, body);
}

bool RyzenAIBackend::is_healthy() const {
    if (!m_loaded_) {
        return false;
    }

    std::string url = "http://" + m_config.host + ":" +
                      std::to_string(m_port) + "/health";

    return HTTPClient::is_reachable(url, 1000);
}

bool RyzenAIBackend::wait_for_ready(int timeout_ms) {
    std::string url = "http://" + m_config.host + ":" +
                      std::to_string(m_port) + "/health";

    std::cout << "[RyzenAI] Waiting for server to be ready..." << std::endl;

    const int max_attempts = timeout_ms / 500;
    for (int attempt = 0; attempt < max_attempts; ++attempt) {
        // Check if process is still running
        ProcessHandle handle;
        handle.pid = m_server_pid;
        handle.running = true;
        if (!ProcessManager::is_running(handle)) {
            std::cerr << "[RyzenAI] Server process terminated" << std::endl;
            return false;
        }

        // Try to reach health endpoint
        if (HTTPClient::is_reachable(url, 500)) {
            std::cout << "[RyzenAI] Server is ready" << std::endl;
            return true;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(500));

        if (attempt % 10 == 0 && attempt > 0) {
            std::cout << "[RyzenAI] Still waiting... (" << (attempt * 500 / 1000) << "s)" << std::endl;
        }
    }

    std::cerr << "[RyzenAI] Server not ready after " << timeout_ms << "ms" << std::endl;
    return false;
}

std::string RyzenAIBackend::send_http_request(const std::string& endpoint,
                                              const std::string& body) {
    try {
        return HTTPClient::post(endpoint, body, 120000);  // 2 minute timeout
    } catch (const std::exception& e) {
        throw RyzenAIException(
            ErrorCode::HTTP_REQUEST_FAILED,
            "HTTP request failed: " + std::string(e.what())
        );
    }
}

int RyzenAIBackend::choose_port() {
    // Try random ports in range 8000-9000
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dist(8000, 9000);

    for (int attempt = 0; attempt < 100; ++attempt) {
        int port = dist(gen);

        // Check if port is available
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
            continue;
        }

        int opt = 1;
        setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port);

        if (bind(sock, (struct sockaddr*)&addr, sizeof(addr)) == 0) {
            close(sock);
            return port;
        }

        close(sock);
    }

    return 0;  // Failed to find port
}

} // namespace ryzenai
