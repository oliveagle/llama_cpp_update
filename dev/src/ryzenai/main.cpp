#include "ryzenai_backend.h"
#include "downloader.h"

#include <iostream>
#include <string>
#include <cstring>
#include <csignal>
#include <atomic>
#include <thread>
#include <chrono>
#include <memory>

using namespace ryzenai;

// Global backend instance
static std::unique_ptr<RyzenAIBackend> g_backend;
static std::atomic<bool> g_running(true);

void signal_handler(int signum) {
    std::cout << "\n[RPU] Received signal " << signum << ", shutting down..." << std::endl;
    g_running = false;
    if (g_backend) {
        g_backend->unload_model();
    }
}

void print_usage(const char* program) {
    std::cout << "Usage: " << program << " [options]\n"
              << "\n"
              << "RyzenAI NPU Server - OpenAI API compatible server for AMD NPU\n"
              << "\n"
              << "Options:\n"
              << "  -m, --model <path>      ONNX model path (required)\n"
              << "  --port <n>              Server port (default: auto-select)\n"
              << "  --host <addr>           Bind address (default: 127.0.0.1)\n"
              << "  --ctx-size <n>          Context length (default: 8192)\n"
              << "  --debug                 Enable debug mode\n"
              << "  --download              Download ryzenai-server and exit\n"
              << "  --version               Show version\n"
              << "  -h, --help              Show this help\n"
              << "\n"
              << "Environment variables:\n"
              << "  LLAMA_RYZENAI_SERVER_BIN    Custom ryzenai-server path\n"
              << "  LLAMA_RYZENAI_SERVER_VERSION  Version to download\n"
              << "\n"
              << "Example:\n"
              << "  " << program << " --model /path/to/model.onnx --port 8400\n"
              << std::endl;
}

int main(int argc, char* argv[]) {
    std::cout << "[RPU] RyzenAI NPU Server starting..." << std::endl;

    // Parse arguments
    RyzenAIConfig config;
    bool download_only = false;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];

        if (arg == "-m" || arg == "--model") {
            if (i + 1 < argc) {
                config.model_path = argv[++i];
            }
        } else if (arg == "--port") {
            if (i + 1 < argc) {
                config.port = std::stoi(argv[++i]);
            }
        } else if (arg == "--host") {
            if (i + 1 < argc) {
                config.host = argv[++i];
            }
        } else if (arg == "--ctx-size") {
            if (i + 1 < argc) {
                config.ctx_size = std::stoi(argv[++i]);
            }
        } else if (arg == "--debug") {
            config.debug = true;
        } else if (arg == "--download") {
            download_only = true;
        } else if (arg == "--version") {
            std::cout << "llama-npu-server v1.0 (RyzenAI Backend)" << std::endl;
            return 0;
        } else if (arg == "-h" || arg == "--help") {
            print_usage(argv[0]);
            return 0;
        }
    }

    // Download only mode
    if (download_only) {
        std::string version = std::getenv("LLAMA_RYZENAI_SERVER_VERSION")
                              ? std::getenv("LLAMA_RYZENAI_SERVER_VERSION")
                              : "v1.7.0";
        std::cout << "[RPU] Downloading ryzenai-server " << version << "..." << std::endl;
        if (RyzenAIBackend::download(version)) {
            std::cout << "[RPU] Download complete!" << std::endl;
            return 0;
        } else {
            std::cerr << "[RPU] Download failed" << std::endl;
            return 1;
        }
    }

    // Validate model path
    if (config.model_path.empty()) {
        std::cerr << "[RPU] Error: --model is required\n" << std::endl;
        print_usage(argv[0]);
        return 1;
    }

    // Setup signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    // Initialize backend
    g_backend = std::make_unique<RyzenAIBackend>();

    std::cout << "[RPU] Initializing backend..." << std::endl;
    if (!g_backend->init(config)) {
        std::cerr << "[RPU] Failed to initialize backend" << std::endl;
        return 1;
    }

    // Load model
    std::cout << "[RPU] Loading model: " << config.model_path << std::endl;
    if (!g_backend->load_model()) {
        std::cerr << "[RPU] Failed to load model" << std::endl;
        return 1;
    }

    int server_port = g_backend->get_port();
    std::cout << "[RPU] Server running on http://" << config.host << ":" << server_port << std::endl;
    std::cout << "[RPU] Press Ctrl+C to stop" << std::endl;
    std::cout << std::endl;

    // Wait for shutdown signal
    while (g_running) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));

        // Health check
        if (!g_backend->is_healthy()) {
            std::cerr << "[RPU] Warning: Server health check failed" << std::endl;
        }
    }

    std::cout << "[RPU] Shutdown complete" << std::endl;
    return 0;
}
