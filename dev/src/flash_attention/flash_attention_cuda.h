// CUDA Kernel Implementation of Flash Attention 2
// Optimized for NVIDIA GPUs

#ifndef FLASH_ATTENTION_CUDA_H
#define FLASH_ATTENTION_CUDA_H

#include "flash_attention.h"

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// CUDA Constants
// ============================================================================

// Block sizes for different configurations
#define FA_CUDA_BLOCK_M 128
#define FA_CUDA_BLOCK_N 128
#define FA_CUDA_BLOCK_D 128

// Warp tile sizes
#define FA_CUDA_WARPM 32
#define FA_CUDA_WARPN 32
#define FA_CUDA_WARPQ 32

// ============================================================================
// Status Codes
// ============================================================================

typedef enum {
    FA_CUDA_SUCCESS = 0,
    FA_CUDA_ERROR_NOT_INITIALIZED = -100,
    FA_CUDA_ERROR_DEVICE_UNAVAILABLE = -101,
    FA_CUDA_ERROR_OUT_OF_MEMORY = -102,
    FA_CUDA_ERROR_LAUNCH_FAILED = -103,
    FA_CUDA_ERROR_INVALID_KERNEL = -104
} fa_cuda_status_t;

// ============================================================================
// CUDA Stream Management
// ============================================================================

typedef struct {
    void* stream;  // cudaStream_t*
} fa_cuda_stream_t;

// Initialize CUDA resources
fa_cuda_status_t fa_cuda_init();

// Clean up CUDA resources
fa_cuda_status_t fa_cuda_cleanup();

// Get available device count
fa_cuda_status_t fa_cuda_get_device_count(int* count);

// Set device
fa_cuda_status_t fa_cuda_set_device(int device_id);

// Create stream
fa_cuda_status_t fa_cuda_stream_create(fa_cuda_stream_t* stream);

// Destroy stream
fa_cuda_status_t fa_cuda_stream_destroy(fa_cuda_stream_t* stream);

// Synchronize stream
fa_cuda_status_t fa_cuda_stream_synchronize(fa_cuda_stream_t* stream);

// ============================================================================
// Memory Management
// ============================================================================

// Allocate device memory
fa_cuda_status_t fa_cuda_malloc(void** ptr, size_t size);

// Free device memory
fa_cuda_status_t fa_cuda_free(void* ptr);

// Copy memory (host to device)
fa_cuda_status_t fa_cuda_memcpy_h2d(void* dst, const void* src, size_t size);

// Copy memory (device to host)
fa_cuda_status_t fa_cuda_memcpy_d2h(void* dst, const void* src, size_t size);

// Copy memory (device to device)
fa_cuda_status_t fa_cuda_memcpy_d2d(void* dst, const void* src, size_t size);

// Copy async with stream
fa_cuda_status_t fa_cuda_memcpy_async_h2d(
    void* dst,
    const void* src,
    size_t size,
    fa_cuda_stream_t* stream
);

fa_cuda_status_t fa_cuda_memcpy_async_d2h(
    void* dst,
    const void* src,
    size_t size,
    fa_cuda_stream_t* stream
);

// ============================================================================
// CUDA Flash Attention Kernels
// ============================================================================

// Flash attention forward (FP16/BF16)
fa_cuda_status_t fa_cuda_flash_attention_forward(
    const fa_attn_desc_t* desc,
    const void* q,         // [batch, heads, seq_len_q, head_dim]
    const void* k,         // [batch, heads, seq_len_kv, head_dim]
    const void* v,         // [batch, heads, seq_len_kv, head_dim]
    const void* mask,      // optional attention mask
    void* output,          // [batch, heads, seq_len_q, head_dim]
    fa_workspace_t* workspace,
    fa_cuda_stream_t* stream
);

// Flash attention forward with FP32 accumulation
fa_cuda_status_t fa_cuda_flash_attention_forward_fp32acc(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    const void* mask,
    void* output,
    fa_workspace_t* workspace,
    fa_cuda_stream_t* stream
);

// Flash attention with causal mask
fa_cuda_status_t fa_cuda_flash_attention_causal(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    void* output,
    fa_workspace_t* workspace,
    fa_cuda_stream_t* stream
);

// Flash attention backward (training)
fa_cuda_status_t fa_cuda_flash_attention_backward(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    const void* output,
    const void* grad_output,
    const void* mask,
    void* grad_q,
    void* grad_k,
    void* grad_v,
    fa_workspace_t* workspace,
    fa_cuda_stream_t* stream
);

// ============================================================================
// Grouped Query Attention
// ============================================================================

fa_cuda_status_t fa_cuda_gqa_forward(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    int num_heads_q,
    int num_heads_kv,
    void* output,
    fa_workspace_t* workspace,
    fa_cuda_stream_t* stream
);

// ============================================================================
// Paged KV Cache Attention
// ============================================================================

fa_cuda_status_t fa_cuda_paged_kv_forward(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k_cache,
    const void* v_cache,
    const int32_t* page_indices,
    const int32_t* seq_lengths,
    int page_size,
    void* output,
    fa_workspace_t* workspace,
    fa_cuda_stream_t* stream
);

// ============================================================================
// Sliding Window Attention
// ============================================================================

fa_cuda_status_t fa_cuda_sliding_window_forward(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    int window_size,
    void* output,
    fa_workspace_t* workspace,
    fa_cuda_stream_t* stream
);

// ============================================================================
// Benchmarking
// ============================================================================

typedef struct {
    float forward_time_ms;
    float backward_time_ms;
    float gflops;
    size_t bytes_read;
    size_t bytes_written;
} fa_cuda_benchmark_t;

fa_cuda_status_t fa_cuda_benchmark_attention(
    const fa_attn_desc_t* desc,
    fa_cuda_benchmark_t* benchmark,
    fa_cuda_stream_t* stream
);

// ============================================================================
// Error Handling
// ============================================================================

const char* fa_cuda_status_string(fa_cuda_status_t status);

// Get last CUDA error
fa_cuda_status_t fa_cuda_get_last_error(const char** error_string);

// Clear last error
fa_cuda_status_t fa_cuda_clear_error();

#ifdef __cplusplus
}
#endif

#endif // FLASH_ATTENTION_CUDA_H
