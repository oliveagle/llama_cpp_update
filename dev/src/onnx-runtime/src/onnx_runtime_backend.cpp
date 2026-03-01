// ONNX Runtime Backend Implementation

#include "onnx_runtime_backend.h"
#include <onnxruntime_cxx_api.h>
#include <iostream>
#include <chrono>
#include <cstring>
#include <algorithm>

namespace onnx_runtime {

// ONNXRuntimeSession 实现
ONNXRuntimeSession::ONNXRuntimeSession(const ModelConfig& config)
    : config_(config) {
}

ONNXRuntimeSession::~ONNXRuntimeSession() {
    Release();
}

bool ONNXRuntimeSession::Initialize() {
    if (initialized_) {
        return true;
    }

    try {
        // 创建环境
        Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "llama-cpp-onnx");
        env_ = std::make_unique<Ort::Env>(std::move(env));

        // 创建会话选项
        Ort::SessionOptions session_options;
        session_options.SetIntraOpNumThreads(config_.intra_op_num_threads);
        session_options.SetInterOpNumThreads(config_.inter_op_num_threads);
        session_options.SetGraphOptimizationLevel(
            static_cast<GraphOptimizationLevel>(config_.graph_optimization_level)
        );

        if (config_.enable_cpu_mem_arena) {
            session_options.SetCpuMemArena(true);
        }

        if (config_.enable_mem_pattern) {
            session_options.SetExecutionMode(ExecutionMode::ORT_SEQUENTIAL);
        }

        if (!config_.cache_dir.empty()) {
            session_options.SetOptimizedModelFilePath(config_.cache_dir.c_str());
        }

        // 设置 Execution Provider
        if (!SetExecutionProvider(config_.ep, session_options)) {
            std::cerr << "Warning: Failed to set " <<
                static_cast<int>(config_.ep) << " EP, falling back to CPU" << std::endl;
            SetExecutionProvider(ExecutionProvider::CPU, session_options);
        }

        session_options_ = std::make_unique<Ort::SessionOptions>(std::move(session_options));

        // 创建内存信息
        Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(
            OrtArenaAllocator, OrtMemTypeDefault
        );
        memory_info_ = std::make_unique<Ort::MemoryInfo>(std::move(memory_info));

        initialized_ = true;
        return true;

    } catch (const Ort::Exception& e) {
        std::cerr << "ONNX Runtime Exception: " << e.what() << std::endl;
        return false;
    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return false;
    }
}

bool ONNXRuntimeSession::LoadModel(const std::string& model_path) {
    if (!Initialize()) {
        return false;
    }

    try {
        Ort::Session session(*env_, model_path.c_str(), *session_options_);
        session_ = std::make_unique<Ort::Session>(std::move(session));

        // 解析模型信息
        if (!ParseModelInfo()) {
            return false;
        }

        std::cout << "Model loaded successfully: " << model_path << std::endl;
        std::cout << "  Inputs: " << input_info_.size() << std::endl;
        std::cout << "  Outputs: " << output_info_.size() << std::endl;
        std::cout << "  EP: " << static_cast<int>(config_.ep) << std::endl;

        return true;

    } catch (const Ort::Exception& e) {
        std::cerr << "Failed to load model: " << e.what() << std::endl;
        return false;
    }
}

bool ONNXRuntimeSession::SetExecutionProvider(
    ExecutionProvider ep, OrtSessionOptions* options) {

    // 注意：这里需要实际的 ONNX Runtime C API
    // 由于 XDNA EP 可能不可用，我们先实现基本的支持
    try {
        Ort::SessionOptions* opts = reinterpret_cast<Ort::SessionOptions*>(options);

        switch (ep) {
            case ExecutionProvider::CPU:
                // CPU 是默认的，不需要额外设置
                return true;

            case ExecutionProvider::CUDA:
                // 需要编译带 CUDA EP 的 ORT
                // OrtCUDAProviderOptions cuda_options;
                // opts->AppendExecutionProvider_CUDA(cuda_options);
                return false;  // 当前未实现

            case ExecutionProvider::ROCM:
                // 需要编译带 ROCm EP 的 ORT
                return false;  // 当前未实现

            case ExecutionProvider::XDNA:
                // XDNA EP - 需要特殊编译
                // 详见: https://github.com/onnxruntime/onnxruntime/tree/main/onnxruntime/core/providers/xdna
                return false;  // 当前未实现

            case ExecutionProvider::OPENVINO:
                // OpenVINO EP
                // opts->AppendExecutionProvider_OpenVINO(...)
                return false;  // 当前未实现

            case ExecutionProvider::TENSORRT:
                // TensorRT EP
                return false;  // 当前未实现
        }
    } catch (...) {
        return false;
    }
    return false;
}

bool ONNXRuntimeSession::ParseModelInfo() {
    try {
        Ort::Session& session = *session_;

        // 解析输入
        size_t num_inputs = session.GetInputCount();
        input_info_.clear();
        input_info_.reserve(num_inputs);

        for (size_t i = 0; i < num_inputs; ++i) {
            auto name = session.GetInputNameAllocated(i, *allocator_);
            auto type_info = session.GetInputTypeInfo(i);
            auto tensor_info = type_info.GetTensorTypeAndShapeInfo();

            TensorInfo info;
            info.name = name.get();
            info.type = tensor_info.GetElementType();

            // 获取形状
            std::vector<int64_t> shape;
            tensor_info.GetDimensionsCount(&info.num_elements);
            shape.resize(info.num_elements);
            tensor_info.GetDimensions(shape.data(), shape.size());
            info.shape = shape;

            // 计算元素数量和字节大小
            info.num_elements = 1;
            for (auto dim : info.shape) {
                info.num_elements *= (dim >= 0) ? dim : 1;
            }

            size_t element_size = 0;
            switch (info.type) {
                case ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT: element_size = sizeof(float); break;
                case ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT16: element_size = sizeof(uint16_t); break;
                case ONNX_TENSOR_ELEMENT_DATA_TYPE_INT8: element_size = sizeof(int8_t); break;
                case ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT8: element_size = sizeof(uint8_t); break;
                case ONNX_TENSOR_ELEMENT_DATA_TYPE_INT32: element_size = sizeof(int32_t); break;
                case ONNX_TENSOR_ELEMENT_DATA_TYPE_INT64: element_size = sizeof(int64_t); break;
                default: element_size = sizeof(float); break;
            }
            info.size_bytes = info.num_elements * element_size;

            input_info_.push_back(std::move(info));
        }

        // 解析输出
        size_t num_outputs = session.GetOutputCount();
        output_info_.clear();
        output_info_.reserve(num_outputs);

        for (size_t i = 0; i < num_outputs; ++i) {
            auto name = session.GetOutputNameAllocated(i, *allocator_);
            auto type_info = session.GetOutputTypeInfo(i);
            auto tensor_info = type_info.GetTensorTypeAndShapeInfo();

            TensorInfo info;
            info.name = name.get();
            info.type = tensor_info.GetElementType();

            std::vector<int64_t> shape;
            tensor_info.GetDimensionsCount(&info.num_elements);
            shape.resize(info.num_elements);
            tensor_info.GetDimensions(shape.data(), shape.size());
            info.shape = shape;

            info.num_elements = 1;
            for (auto dim : info.shape) {
                info.num_elements *= (dim >= 0) ? dim : 1;
            }

            size_t element_size = sizeof(float);  // 默认 float
            switch (info.type) {
                case ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT: element_size = sizeof(float); break;
                case ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT16: element_size = sizeof(uint16_t); break;
                default: break;
            }
            info.size_bytes = info.num_elements * element_size;

            output_info_.push_back(std::move(info));
        }

        return true;

    } catch (const Ort::Exception& e) {
        std::cerr << "Failed to parse model info: " << e.what() << std::endl;
        return false;
    }
}

InferenceResult ONNXRuntimeSession::Run(
    const std::unordered_map<std::string, const void*>& inputs,
    const std::unordered_map<std::string, std::vector<int64_t>>& input_shapes) {

    InferenceResult result;
    auto start_time = std::chrono::high_resolution_clock::now();

    try {
        if (!session_) {
            result.success = false;
            result.error_msg = "Session not loaded";
            return result;
        }

        // 准备输入张量
        std::vector<Ort::Value> input_tensors;
        input_tensors.reserve(inputs.size());

        for (const auto& [name, data] : inputs) {
            auto it = input_shapes.find(name);
            if (it == input_shapes.end()) {
                result.success = false;
                result.error_msg = "Shape not found for input: " + name;
                return result;
            }

            Ort::Value tensor = Ort::Value::CreateTensor(
                *memory_info_,
                const_cast<void*>(data),
                input_tensors.size(),
                it->second.data(),
                it->second.size(),
                ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT
            );
            input_tensors.push_back(std::move(tensor));
        }

        // 准备输出名称
        std::vector<const char*> output_names;
        output_names.reserve(output_info_.size());
        for (const auto& info : output_info_) {
            output_names.push_back(info.name.c_str());
        }

        // 运行推理
        auto outputs = session_->Run(
            Ort::RunOptions{nullptr},
            nullptr,  // input names (从 session 获取)
            input_tensors.data(),
            input_tensors.size(),
            output_names.data(),
            output_names.size()
        );

        // 收集输出
        size_t total_output_size = 0;
        for (const auto& output : outputs) {
            auto info = output.GetTensorTypeAndShapeInfo();
            size_t num_elements = info.GetElementCount();
            total_output_size += num_elements;
        }

        result.outputs.resize(total_output_size);
        size_t offset = 0;
        for (size_t i = 0; i < outputs.size(); ++i) {
            float* data = outputs[i].GetTensorMutableData<float>();
            auto info = outputs[i].GetTensorTypeAndShapeInfo();
            size_t num_elements = info.GetElementCount();
            std::memcpy(result.outputs.data() + offset, data, num_elements * sizeof(float));
            offset += num_elements;
        }

        result.info = output_info_;
        result.success = true;

    } catch (const Ort::Exception& e) {
        result.success = false;
        result.error_msg = e.what();
    } catch (const std::exception& e) {
        result.success = false;
        result.error_msg = e.what();
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    result.inference_time_ms = std::chrono::duration<double, std::milli>(
        end_time - start_time).count();

    if (result.success) {
        inference_count_++;
        total_inference_time_ms_ += result.inference_time_ms;
    }

    return result;
}

InferenceResult ONNXRuntimeSession::Run(
    const std::unordered_map<std::string, std::vector<float>>& inputs) {

    std::unordered_map<std::string, const void*> input_ptrs;
    std::unordered_map<std::string, std::vector<int64_t>> input_shapes;

    for (const auto& [name, data] : inputs) {
        input_ptrs[name] = data.data();
        input_shapes[name] = {static_cast<int64_t>(data.size())};
    }

    return Run(input_ptrs, input_shapes);
}

double ONNXRuntimeSession::GetAverageInferenceTimeMs() const {
    uint64_t count = inference_count_.load();
    if (count == 0) return 0.0;
    return total_inference_time_ms_.load() / count;
}

uint64_t ONNXRuntimeSession::GetInferenceCount() const {
    return inference_count_.load();
}

void ONNXRuntimeSession::Release() {
    session_.reset();
    session_options_.reset();
    memory_info_.reset();
    allocator_.reset();
    env_.reset();
    initialized_ = false;
}

// ONNXRuntimeBackend 实现
ONNXRuntimeBackend& ONNXRuntimeBackend::Instance() {
    static ONNXRuntimeBackend instance;
    return instance;
}

bool ONNXRuntimeBackend::Initialize() {
    if (initialized_) return true;

    // 检查可用的 EP
    available_eps_.push_back(ExecutionProvider::CPU);

    // TODO: 检查其他 EP 的可用性
    // 需要动态链接检测

    initialized_ = true;
    return true;
}

bool ONNXRuntimeBackend::CreateSession(const std::string& session_id,
                                     const ModelConfig& config) {
    if (!Initialize()) {
        return false;
    }

    auto session = std::make_unique<ONNXRuntimeSession>(config);
    if (!session->Initialize() || !session->LoadModel(config.model_path)) {
        return false;
    }

    sessions_[session_id] = std::move(session);
    return true;
}

ONNXRuntimeSession* ONNXRuntimeBackend::GetSession(const std::string& session_id) {
    auto it = sessions_.find(session_id);
    return (it != sessions_.end()) ? it->second.get() : nullptr;
}

bool ONNXRuntimeBackend::RemoveSession(const std::string& session_id) {
    return sessions_.erase(session_id) > 0;
}

std::vector<ExecutionProvider> ONNXRuntimeBackend::GetAvailableExecutionProviders() const {
    return available_eps_;
}

bool ONNXRuntimeBackend::IsExecutionProviderAvailable(ExecutionProvider ep) const {
    return std::find(available_eps_.begin(), available_eps_.end(), ep)
        != available_eps_.end();
}

void ONNXRuntimeBackend::Shutdown() {
    sessions_.clear();
    initialized_ = false;
}

// C API 绑定（简化版）
extern "C" {

int ort_create_session(const char* session_id, const char* model_path,
                     int ep_type, int num_threads, void** session_ptr) {
    try {
        onnx_runtime::ModelConfig config;
        config.model_path = model_path;
        config.ep = static_cast<onnx_runtime::ExecutionProvider>(ep_type);
        config.num_threads = num_threads;

        auto& backend = onnx_runtime::ONNXRuntimeBackend::Instance();
        if (!backend.CreateSession(session_id, config)) {
            return -1;
        }

        *session_ptr = backend.GetSession(session_id);
        return 0;
    } catch (...) {
        return -1;
    }
}

int ort_load_session(const char* model_path, int ep_type, void** session_ptr) {
    // 简化版 - 直接加载单个会话
    try {
        onnx_runtime::ModelConfig config;
        config.model_path = model_path;
        config.ep = static_cast<onnx_runtime::ExecutionProvider>(ep_type);

        auto session = std::make_unique<onnx_runtime::ONNXRuntimeSession>(config);
        if (!session->LoadModel(model_path)) {
            return -1;
        }

        *session_ptr = session.release();
        return 0;
    } catch (...) {
        return -1;
    }
}

int ort_run_inference(void* session_ptr, const void* inputs,
                     const int64_t* input_shapes, int num_inputs,
                     void* outputs, int* output_count) {
    // 简化版 - 需要更完整的实现
    return 0;
}

int ort_free_session(void* session_ptr) {
    try {
        delete reinterpret_cast<onnx_runtime::ONNXRuntimeSession*>(session_ptr);
        return 0;
    } catch (...) {
        return -1;
    }
}

int ort_get_input_info(void* session_ptr, char*** names,
                      int64_t** shapes, int* num_inputs) {
    // TODO: 实现
    return 0;
}

int ort_get_output_info(void* session_ptr, char*** names,
                       int64_t** shapes, int* num_outputs) {
    // TODO: 实现
    return 0;
}

double ort_get_average_time_ms(void* session_ptr) {
    auto* session = reinterpret_cast<onnx_runtime::ONNXRuntimeSession*>(session_ptr);
    return session ? session->GetAverageInferenceTimeMs() : 0.0;
}

uint64_t ort_get_inference_count(void* session_ptr) {
    auto* session = reinterpret_cast<onnx_runtime::ONNXRuntimeSession*>(session_ptr);
    return session ? session->GetInferenceCount() : 0;
}

} // extern "C"

} // namespace onnx_runtime
