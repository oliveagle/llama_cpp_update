// ONNX Runtime Backend for llama.cpp
// 支持 CPU、CUDA、XDNA (AMD NPU) 等多种 Execution Provider

#pragma once

#include <memory>
#include <vector>
#include <string>
#include <unordered_map>
#include <cstdint>
#include <atomic>

// ONNX Runtime C API 前向声明
struct OrtEnv;
struct OrtSession;
struct OrtSessionOptions;
struct OrtMemoryInfo;
struct OrtValue;
struct OrtRunOptions;
struct OrtAllocator;

namespace onnx_runtime {

// Execution Provider 类型
enum class ExecutionProvider {
    CPU,           // CPU (默认)
    CUDA,          // NVIDIA CUDA
    ROCM,          // AMD ROCm
    XDNA,          // AMD XDNA NPU
    OPENVINO,      // Intel OpenVINO
    TENSORRT       // NVIDIA TensorRT
};

// 模型配置
struct ModelConfig {
    std::string model_path;           // 模型路径
    ExecutionProvider ep;             // Execution Provider
    int num_threads = 1;             // CPU 线程数
    bool enable_profiling = false;     // 启用性能分析
    std::string cache_dir;            // 缓存目录
    int intra_op_num_threads = 1;    // 节点内并行度
    int inter_op_num_threads = 1;    // 节点间并行度
};

// Tensor 信息
struct TensorInfo {
    std::string name;
    std::vector<int64_t> shape;
    ONNXTensorElementDataType type;
    size_t num_elements;
    size_t size_bytes;
};

// 推理结果
struct InferenceResult {
    std::vector<float> outputs;       // 输出数据
    std::vector<TensorInfo> info;    // 输出信息
    double inference_time_ms = 0;    // 推理时间（毫秒）
    bool success = false;            // 是否成功
    std::string error_msg;           // 错误信息
};

// 会话选项
struct SessionOptions {
    int graph_optimization_level = 99;  // 0=禁用, 1=基本, 2=扩展, 99=全部
    bool enable_cpu_mem_arena = true;    // CPU 内存竞技场
    bool enable_mem_pattern = false;      // 启用内存模式
    int execution_mode = 0;              // 0=串行, 1=并行
};

// ONNX Runtime 会话类
class ONNXRuntimeSession {
public:
    explicit ONNXRuntimeSession(const ModelConfig& config);
    ~ONNXRuntimeSession();

    // 初始化会话
    bool Initialize();
    bool IsInitialized() const { return initialized_; }

    // 加载模型
    bool LoadModel(const std::string& model_path);

    // 获取输入/输出信息
    std::vector<TensorInfo> GetInputInfo() const;
    std::vector<TensorInfo> GetOutputInfo() const;

    // 运行推理
    InferenceResult Run(
        const std::unordered_map<std::string, const void*>& inputs,
        const std::unordered_map<std::string, std::vector<int64_t>>& input_shapes
    );

    InferenceResult Run(
        const std::unordered_map<std::string, std::vector<float>>& inputs
    );

    // 性能统计
    double GetAverageInferenceTimeMs() const;
    uint64_t GetInferenceCount() const;

    // 释放资源
    void Release();

private:
    ModelConfig config_;
    std::unique_ptr<OrtEnv> env_;
    std::unique_ptr<OrtSession> session_;
    std::unique_ptr<OrtSessionOptions> session_options_;
    std::unique_ptr<OrtMemoryInfo> memory_info_;
    std::unique_ptr<OrtAllocator> allocator_;

    std::vector<TensorInfo> input_info_;
    std::vector<TensorInfo> output_info_;

    std::atomic<uint64_t> inference_count_{0};
    std::atomic<double> total_inference_time_ms_{0.0};

    bool initialized_ = false;

    // 内部辅助函数
    bool SetExecutionProvider(ExecutionProvider ep, OrtSessionOptions* options);
    bool ParseModelInfo();
    OrtValue* CreateTensor(const std::string& name, const void* data,
                         const std::vector<int64_t>& shape);
};

// ONNX Runtime 后端管理器
class ONNXRuntimeBackend {
public:
    static ONNXRuntimeBackend& Instance();

    // 创建/加载会话
    bool CreateSession(const std::string& session_id, const ModelConfig& config);
    bool LoadSession(const std::string& session_id, const std::string& model_path);

    // 获取会话
    ONNXRuntimeSession* GetSession(const std::string& session_id);
    bool RemoveSession(const std::string& session_id);

    // 可用的 EP
    std::vector<ExecutionProvider> GetAvailableExecutionProviders() const;
    bool IsExecutionProviderAvailable(ExecutionProvider ep) const;

    // 全局初始化
    bool Initialize();
    void Shutdown();

private:
    ONNXRuntimeBackend() = default;
    ~ONNXRuntimeBackend() = default;
    ONNXRuntimeBackend(const ONNXRuntimeBackend&) = delete;
    ONNXRuntimeBackend& operator=(const ONNXRuntimeBackend&) = delete;

    std::unordered_map<std::string, std::unique_ptr<ONNXRuntimeSession>> sessions_;
    std::vector<ExecutionProvider> available_eps_;
    bool initialized_ = false;
};

// C API 绑定（用于 Python/其他语言调用）
extern "C" {

// 会话管理
int ort_create_session(const char* session_id, const char* model_path,
                     int ep_type, int num_threads, void** session_ptr);
int ort_load_session(const char* model_path, int ep_type, void** session_ptr);
int ort_run_inference(void* session_ptr, const void* inputs,
                     const int64_t* input_shapes, int num_inputs,
                     void* outputs, int* output_count);
int ort_free_session(void* session_ptr);

// 信息查询
int ort_get_input_info(void* session_ptr, char*** names,
                      int64_t** shapes, int* num_inputs);
int ort_get_output_info(void* session_ptr, char*** names,
                       int64_t** shapes, int* num_outputs);

// 性能统计
double ort_get_average_time_ms(void* session_ptr);
uint64_t ort_get_inference_count(void* session_ptr);

} // extern "C"

} // namespace onnx_runtime
