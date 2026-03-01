#pragma once

/**
 * RyzenAI Backend for llama.cpp
 *
 * AMD NPU support via RyzenAI-Server (ONNX Runtime GenAI)
 * Reference: https://github.com/lemonade-sdk/ryzenai-server
 */

#include <string>
#include <cstdint>
#include <memory>
#include <stdexcept>

namespace ryzenai {

/**
 * RyzenAI configuration
 */
struct RyzenAIConfig {
    std::string ryzenai_path;       // ryzenai-server executable path
    std::string model_path;         // ONNX model path
    int ctx_size = 8192;            // Context length
    int port = 0;                   // Port (0 = auto select)
    std::string host = "127.0.0.1"; // Bind address
    bool debug = false;             // Debug mode
};

/**
 * Error codes
 */
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

/**
 * RyzenAI exception
 */
class RyzenAIException : public std::runtime_error {
public:
    RyzenAIException(ErrorCode code, const std::string& message)
        : std::runtime_error(message), code_(code) {}

    ErrorCode code() const { return code_; }

private:
    ErrorCode code_;
};

/**
 * RyzenAI Backend
 *
 * Manages ryzenai-server process and forwards HTTP requests
 */
class RyzenAIBackend {
public:
    RyzenAIBackend();
    ~RyzenAIBackend();

    /**
     * Check if ryzenai-server is available
     */
    static bool is_available();

    /**
     * Download ryzenai-server from GitHub releases
     * @param version Version to download (e.g., "v1.7.0")
     * @return true if download succeeded
     */
    static bool download(const std::string& version = "v1.7.0");

    /**
     * Get ryzenai-server path
     * @throws RyzenAIException if not found
     */
    static std::string get_ryzenai_server_path();

    /**
     * Initialize backend
     * @param config Configuration
     * @return true if initialization succeeded
     */
    bool init(const RyzenAIConfig& config);

    /**
     * Load ONNX model
     * @return true if model loaded successfully
     */
    bool load_model();

    /**
     * Unload model and stop ryzenai-server
     */
    void unload_model();

    /**
     * Chat completion
     * @param messages JSON messages array
     * @param max_tokens Maximum tokens to generate
     * @param temperature Sampling temperature
     * @return JSON response
     */
    std::string chat_completion(const std::string& messages,
                                int max_tokens = 512,
                                float temperature = 0.7f);

    /**
     * Text completion
     * @param prompt Input prompt
     * @param max_tokens Maximum tokens to generate
     * @param temperature Sampling temperature
     * @return JSON response
     */
    std::string completion(const std::string& prompt,
                          int max_tokens = 512,
                          float temperature = 0.7f);

    /**
     * Health check
     */
    bool is_healthy() const;

    /**
     * Check if model is loaded
     */
    bool is_loaded() const { return m_loaded_; }

    /**
     * Get server port
     */
    int get_port() const { return m_port; }

private:
    RyzenAIConfig m_config;
    pid_t m_server_pid = 0;
    int m_port = 0;
    bool m_loaded_ = false;

    /**
     * Wait for server to be ready
     * @param timeout_ms Timeout in milliseconds
     * @return true if server became ready
     */
    bool wait_for_ready(int timeout_ms = 30000);

    /**
     * Send HTTP request
     * @param endpoint API endpoint (e.g., "/v1/chat/completions")
     * @param body Request body JSON
     * @return Response body JSON
     */
    std::string send_http_request(const std::string& endpoint,
                                  const std::string& body);

    /**
     * Choose available port
     * @return Port number
     */
    int choose_port();
};

} // namespace ryzenai
