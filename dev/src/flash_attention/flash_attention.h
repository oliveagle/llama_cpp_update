// Flash Attention 2 Implementation
// Based on "FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning"
// by Tri Dao, 2023

#ifndef FLASH_ATTENTION_H
#define FLASH_ATTENTION_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// Configuration Constants
// ============================================================================

// Block sizes - these are tunable based on hardware
#ifndef FA_BLOCK_SIZE_D
#define FA_BLOCK_SIZE_D 128  // d_k/d_v block size
#endif

#ifndef FA_BLOCK_SIZE_N
#define FA_BLOCK_SIZE_N 64   // Sequence length block size
#endif

#ifndef FA_BLOCK_SIZE_H
#define FA_BLOCK_SIZE_H 1    // Head block size (usually 1 for simplicity)
#endif

// Warp and thread configuration
#define FA_WARP_SIZE 32
#define FA_THREADS_PER_BLOCK 128

// ============================================================================
// Data Types
// ============================================================================

// Precision types
typedef enum {
    FA_PRECISION_FP32 = 0,
    FA_PRECISION_FP16 = 1,
    FA_PRECISION_BF16 = 2,
    FA_PRECISION_FP8  = 3
} fa_precision_t;

// Backend types
typedef enum {
    FA_BACKEND_CPU = 0,
    FA_BACKEND_CUDA = 1,
    FA_BACKEND_HIP = 2,
    FA_BACKEND_VULKAN = 3,
    FA_BACKEND_METAL = 4
} fa_backend_t;

// Status codes
typedef enum {
    FA_SUCCESS = 0,
    FA_ERROR_INVALID_ARGUMENT = -1,
    FA_ERROR_OUT_OF_MEMORY = -2,
    FA_ERROR_NOT_IMPLEMENTED = -3,
    FA_ERROR_INTERNAL = -4,
    FA_ERROR_HARDWARE_UNAVAILABLE = -5
} fa_status_t;

// ============================================================================
// Attention Descriptor
// ============================================================================

typedef struct {
    // Dimensions
    int batch_size;
    int num_heads;
    int seq_len_q;
    int seq_len_kv;
    int head_dim;

    // Strides (in elements)
    int stride_q_b;  // Q stride for batch
    int stride_q_h;  // Q stride for head
    int stride_q_s;  // Q stride for sequence
    int stride_k_b;  // K stride for batch
    int stride_k_h;  // K stride for head
    int stride_k_s;  // K stride for sequence
    int stride_v_b;  // V stride for batch
    int stride_v_h;  // V stride for head
    int stride_v_s;  // V stride for sequence
    int stride_o_b;  // O stride for batch
    int stride_o_h;  // O stride for head
    int stride_o_s;  // O stride for sequence

    // Attention mask
    int has_mask;
    int is_causal;

    // Dropout
    float dropout_prob;
    int is_training;

    // Scaling factor (usually 1/sqrt(head_dim))
    float scale;

    // Precision and backend
    fa_precision_t precision;
    fa_backend_t backend;

    // Block sizes (tunable)
    int block_size_d;
    int block_size_n;
} fa_attn_desc_t;

// ============================================================================
// Workspace
// ============================================================================

typedef struct {
    void* data;
    size_t size;
    fa_backend_t backend;
} fa_workspace_t;

// ============================================================================
// API Functions
// ============================================================================

// Initialize attention descriptor with default values
fa_status_t fa_attn_desc_init(fa_attn_desc_t* desc);

// Calculate required workspace size
fa_status_t fa_workspace_query_size(
    const fa_attn_desc_t* desc,
    size_t* size_out
);

// Initialize workspace
fa_status_t fa_workspace_init(
    fa_workspace_t* workspace,
    const fa_attn_desc_t* desc,
    void* buffer,
    size_t buffer_size
);

// ----------------------------------------------------------------------------
// Core Attention Forward Pass
// ----------------------------------------------------------------------------

// Standard flash attention forward (Q, K, V -> O)
fa_status_t fa_attention_forward(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    const void* attention_mask,  // optional, can be NULL
    void* output,
    fa_workspace_t* workspace
);

// Flash attention with attention bias (e.g., ALiBi, relative positional bias)
fa_status_t fa_attention_forward_with_bias(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    const void* attention_bias,    // bias to add to attention scores
    const void* attention_mask,    // optional, can be NULL
    void* output,
    fa_workspace_t* workspace
);

// Paged KV cache attention (for inference)
fa_status_t fa_attention_paged_kv(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k_cache,
    const void* v_cache,
    const int32_t* page_indices,    // [batch_size, max_pages]
    const int32_t* seq_lengths,     // [batch_size]
    int page_size,
    void* output,
    fa_workspace_t* workspace
);

// ----------------------------------------------------------------------------
// Backward Pass (Training)
// ----------------------------------------------------------------------------

fa_status_t fa_attention_backward(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    const void* output,
    const void* grad_output,
    const void* attention_mask,
    void* grad_q,
    void* grad_k,
    void* grad_v,
    fa_workspace_t* workspace
);

// ----------------------------------------------------------------------------
// Variants
// ----------------------------------------------------------------------------

// Sliding window attention
fa_status_t fa_attention_sliding_window(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    int window_size,
    void* output,
    fa_workspace_t* workspace
);

// Grouped query attention
fa_status_t fa_attention_grouped_query(
    const fa_attn_desc_t* desc,
    const void* q,           // [batch, num_heads_q, seq_len, head_dim]
    const void* k,           // [batch, num_heads_kv, seq_len, head_dim]
    const void* v,           // [batch, num_heads_kv, seq_len, head_dim]
    int num_heads_q,
    int num_heads_kv,
    void* output,
    fa_workspace_t* workspace
);

// ----------------------------------------------------------------------------
// Utility Functions
// ----------------------------------------------------------------------------

const char* fa_status_string(fa_status_t status);

int fa_supports_backend(fa_backend_t backend);

// Set default strides for packed layout (batch, heads, seq_len, dim)
void fa_set_default_strides(fa_attn_desc_t* desc);

// ============================================================================
// CPU Reference Implementation
// ============================================================================

fa_status_t fa_cpu_attention_forward(
    const fa_attn_desc_t* desc,
    const float* q,
    const float* k,
    const float* v,
    const float* attention_mask,
    float* output,
    fa_workspace_t* workspace
);

// Reference (non-flash) attention for verification
fa_status_t fa_reference_attention(
    const fa_attn_desc_t* desc,
    const float* q,
    const float* k,
    const float* v,
    const float* attention_mask,
    float* output
);

#ifdef __cplusplus
}
#endif

#endif // FLASH_ATTENTION_H
