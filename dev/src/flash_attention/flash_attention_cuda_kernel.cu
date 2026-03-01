/**
 * Flash Attention 2 CUDA Kernel Implementation
 *
 * This file contains the CUDA kernels for FlashAttention-2 as described in
 * "FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning"
 * by Tri Dao (2023)
 *
 * Key optimizations:
 * 1. Tiled computation with shared memory
 * 2. Online softmax to avoid materializing attention matrix
 * 3. Warp-level parallelism for reduction
 * 4. Loop tiling for better data reuse
 */

#include "flash_attention_cuda.h"

// ============================================================================
// Constants
// ============================================================================

// Thread block dimensions
constexpr int BLOCK_M = 128;  // M dimension (sequence length)
constexpr int BLOCK_N = 128;  // N dimension (sequence length)
constexpr int BLOCK_DMODEL = 128;  // D dimension (head dim)

// Warp dimensions
constexpr int WARPM = 32;  // Warp size for M dimension
constexpr int WARPN = 32;  // Warp size for N dimension

// Number of threads per block
constexpr int THREADS_PER_BLOCK = 128;

// ============================================================================
// Device Functions
// ============================================================================

// Max reduction across warp
__device__ inline float warp_max(float x) {
    unsigned int mask = 0xffffffff;
    #pragma unroll
    for (int offset = 16; offset > 0; offset >>= 1) {
        x = fmaxf(x, __shfl_xor_sync(mask, x, offset));
    }
    return x;
}

// Sum reduction across warp
__device__ inline float warp_sum(float x) {
    unsigned int mask = 0xffffffff;
    #pragma unroll
    for (int offset = 16; offset > 0; offset >>= 1) {
        x += __shfl_xor_sync(mask, x, offset);
    }
    return x;
}

// Exp sum with max factor (for softmax stability)
struct SoftmaxState {
    float m;  // Max value
    float l;  // Sum of exp(x-m)
};

__device__ inline SoftmaxState softmax_combine(SoftmaxState a, SoftmaxState b) {
    SoftmaxState s;
    if (b.m > a.m) {
        s.m = b.m;
        s.l = b.l + a.l * expf(a.m - b.m);
    } else {
        s.m = a.m;
        s.l = a.l + b.l * expf(b.m - a.m);
    }
    return s;
}

// Softmax update for a single value
__device__ inline SoftmaxState softmax_update(SoftmaxState s, float x) {
    SoftmaxState r;
    if (x > s.m) {
        r.m = x;
        r.l = 1.0f + s.l * expf(s.m - x);
    } else {
        r.m = s.m;
        r.l = s.l + expf(x - s.m);
    }
    return r;
}

// ============================================================================
// Shared Memory Layout
// ============================================================================

// Shared memory for tiles
__shared__ float shared_q[BLOCK_M * BLOCK_DMODEL];
__shared__ float shared_k[BLOCK_N * BLOCK_DMODEL];
__shared__ float shared_v[BLOCK_N * BLOCK_DMODEL];

// Shared memory for softmax accumulators
__shared__ float shared_m[BLOCK_M];
__shared__ float shared_l[BLOCK_M];

// ============================================================================
// Flash Attention 2 Forward Kernel
// ============================================================================

/**
 * Flash Attention 2 Forward Kernel
 *
 * Args:
 *   q: Query tensor [batch, num_heads, seq_len_q, head_dim]
 *   k: Key tensor [batch, num_heads, seq_len_kv, head_dim]
 *   v: Value tensor [batch, num_heads, seq_len_kv, head_dim]
 *   output: Output tensor [batch, num_heads, seq_len_q, head_dim]
 *   batch_size: Batch size
 *   num_heads: Number of attention heads
 *   seq_len_q: Query sequence length
 *   seq_len_kv: Key/Value sequence length
 *   head_dim: Head dimension
 *   scale: Scaling factor (typically 1/sqrt(head_dim))
 *   is_causal: Whether to apply causal mask
 */
__global__ void flash_attention_2_forward(
    const float* __restrict__ q,
    const float* __restrict__ k,
    const float* __restrict__ v,
    float* __restrict__ output,
    int batch_size,
    int num_heads,
    int seq_len_q,
    int seq_len_kv,
    int head_dim,
    float scale,
    int is_causal
) {
    // Get thread and block indices
    int bx = blockIdx.x;  // Batch index
    int by = blockIdx.y;  // Head index
    int tx = threadIdx.x;  // Thread index within block

    // Total elements per batch-head combination
    const int stride_q_b = num_heads * seq_len_q * head_dim;
    const int stride_q_h = seq_len_q * head_dim;
    const int stride_k_b = num_heads * seq_len_kv * head_dim;
    const int stride_k_h = seq_len_kv * head_dim;
    const int stride_v_b = num_heads * seq_len_kv * head_dim;
    const int stride_v_h = seq_len_kv * head_dim;
    const int stride_o_b = num_heads * seq_len_q * head_dim;
    const int stride_o_h = seq_len_q * head_dim;

    // Pointers for this batch-head
    const float* q_ptr = q + bx * stride_q_b + by * stride_q_h;
    const float* k_ptr = k + bx * stride_k_b + by * stride_k_h;
    const float* v_ptr = v + bx * stride_v_b + by * stride_v_h;
    float* o_ptr = output + bx * stride_o_b + by * stride_o_h;

    // Each thread processes one position in sequence
    int i = tx;  // Position in Q

    if (i >= seq_len_q) return;

    // Initialize softmax state
    SoftmaxState s = {__float_as_int(0x7f800000u) * -1.0f, 0.0f};  // m=-inf, l=0

    // Initialize output accumulator
    float acc[BLOCK_DMODEL / 32] = {0.0f};

    // Load Q row (cached in register)
    const float* q_row = q_ptr + i * head_dim;

    // Process K, V in blocks (tiled computation)
    for (int j_start = 0; j_start < seq_len_kv; j_start += BLOCK_N) {
        int j_end = min(j_start + BLOCK_N, seq_len_kv);

        // Skip causal blocks
        if (is_causal && j_start > i) break;

        // Load K, V tiles to shared memory
        for (int j = j_start + tx; j < j_end; j += blockDim.x) {
            const float* k_row = k_ptr + j * head_dim;
            const float* v_row = v_ptr + j * head_dim;

            int tile_idx = j - j_start;
            for (int d = 0; d < min(head_dim, BLOCK_DMODEL); d++) {
                shared_k[tile_idx * BLOCK_DMODEL + d] = k_row[d] * scale;
                shared_v[tile_idx * BLOCK_DMODEL + d] = v_row[d];
            }
        }

        __syncthreads();

        // Compute attention for this block
        for (int j = j_start; j < j_end; j++) {
            // Causal mask
            if (is_causal && j > i) continue;

            int tile_j = j - j_start;

            // Compute Q @ K^T
            float score = 0.0f;
            for (int d = 0; d < head_dim; d++) {
                score += q_row[d] * shared_k[tile_j * BLOCK_DMODEL + d];
            }

            // Update softmax state
            s = softmax_update(s, score);

            // Update output accumulator
            float attn = expf(score - s.m);
            for (int d = 0; d < min(head_dim, BLOCK_DMODEL / 32 * 32); d++) {
                acc[d / 32] += attn * shared_v[tile_j * BLOCK_DMODEL + d];
            }
        }

        __syncthreads();
    }

    // Normalize output
    float inv_l = 1.0f / s.l;
    float* out_row = o_ptr + i * head_dim;
    for (int d = 0; d < head_dim; d++) {
        out_row[d] = acc[d / 32] * inv_l;
    }
}

// ============================================================================
// Flash Attention 2 Kernel with Loop Tiling
// ============================================================================

/**
 * Flash Attention 2 Forward with Loop Tiling
 *
 * This version uses loop tiling for better data reuse and is optimized
 * for modern NVIDIA GPUs (A100, H100).
 */
__global__ void flash_attention_2_forward_tiled(
    const float* __restrict__ q,
    const float* __restrict__ k,
    const float* __restrict__ v,
    float* __restrict__ output,
    int batch_size,
    int num_heads,
    int seq_len_q,
    int seq_len_kv,
    int head_dim,
    float scale,
    int is_causal
) {
    // Determine block position
    int bid = blockIdx.x;  // Block index in [0, batch_size * num_heads * (seq_len_q / BLOCK_M))
    int block_i = bid % ((seq_len_q + BLOCK_M - 1) / BLOCK_M);  // Q block
    int head = (bid / ((seq_len_q + BLOCK_M - 1) / BLOCK_M)) % num_heads;
    int batch = bid / (num_heads * ((seq_len_q + BLOCK_M - 1) / BLOCK_M));

    // Thread indices
    int tx = threadIdx.x;
    int ty = threadIdx.y;

    // Determine which Q position this thread handles
    int i = block_i * BLOCK_M + ty;
    if (i >= seq_len_q) return;

    // Compute strides
    const int stride_q_b = num_heads * seq_len_q * head_dim;
    const int stride_q_h = seq_len_q * head_dim;
    const int stride_k_b = num_heads * seq_len_kv * head_dim;
    const int stride_k_h = seq_len_kv * head_dim;
    const int stride_v_b = num_heads * seq_len_kv * head_dim;
    const int stride_v_h = seq_len_kv * head_dim;
    const int stride_o_b = num_heads * seq_len_q * head_dim;
    const int stride_o_h = seq_len_q * head_dim;

    // Get pointers
    const float* q_ptr = q + batch * stride_q_b + head * stride_q_h;
    const float* k_ptr = k + batch * stride_k_b + head * stride_k_h;
    const float* v_ptr = v + batch * stride_v_b + head * stride_v_h;
    float* o_ptr = output + batch * stride_o_b + head * stride_o_h;

    // Load Q row
    const float* q_row = q_ptr + i * head_dim;

    // Initialize accumulators
    float m_prev = -INFINITY;
    float l_prev = 0.0f;
    float acc[BLOCK_DMODEL] = {0.0f};

    // Process K, V in blocks
    for (int block_j = 0; block_j < (seq_len_kv + BLOCK_N - 1) / BLOCK_N; block_j++) {
        int j_start = block_j * BLOCK_N;
        int j_end = min(j_start + BLOCK_N, seq_len_kv);

        // Skip causal blocks
        if (is_causal && j_start > i) break;

        // Load K, V tiles collaboratively
        for (int d = tx; d < head_dim; d += blockDim.x) {
            int j = j_start + ty;
            if (j < j_end) {
                shared_k[ty * BLOCK_DMODEL + d] = (k_ptr + j * head_dim)[d] * scale;
                shared_v[ty * BLOCK_DMODEL + d] = (v_ptr + j * head_dim)[d];
            }
        }
        __syncthreads();

        // Compute attention
        float m_curr = -INFINITY;
        float l_curr = 0.0f;
        float acc_curr[BLOCK_DMODEL] = {0.0f};

        for (int j = j_start; j < j_end; j++) {
            if (is_causal && j > i) continue;

            int tile_j = j - j_start;

            // Compute attention score
            float score = 0.0f;
            for (int d = 0; d < head_dim; d++) {
                score += q_row[d] * shared_k[tile_j * BLOCK_DMODEL + d];
            }

            // Update softmax
            if (score > m_curr) {
                float alpha = expf(m_curr - score);
                l_curr = 1.0f + l_curr * alpha;
                for (int d = 0; d < head_dim; d++) {
                    acc_curr[d] = shared_v[tile_j * BLOCK_DMODEL + d] + acc_curr[d] * alpha;
                }
                m_curr = score;
            } else {
                float beta = expf(score - m_curr);
                l_curr += beta;
                for (int d = 0; d < head_dim; d++) {
                    acc_curr[d] += beta * shared_v[tile_j * BLOCK_DMODEL + d];
                }
            }
        }

        // Combine with previous blocks
        if (m_curr > m_prev) {
            float alpha = expf(m_prev - m_curr);
            l_prev = alpha * l_prev + l_curr;
            for (int d = 0; d < head_dim; d++) {
                acc[d] = acc[d] * alpha + acc_curr[d];
            }
            m_prev = m_curr;
        } else {
            float beta = expf(m_curr - m_prev);
            l_prev += l_curr * beta;
            for (int d = 0; d < head_dim; d++) {
                acc[d] += acc_curr[d] * beta;
            }
        }

        __syncthreads();
    }

    // Write output
    float* out_row = o_ptr + i * head_dim;
    for (int d = 0; d < head_dim; d++) {
        out_row[d] = acc[d] / l_prev;
    }
}

// ============================================================================
// Flash Attention Backward Kernel (Training)
// ============================================================================

__global__ void flash_attention_backward(
    const float* __restrict__ q,
    const float* __restrict__ k,
    const float* __restrict__ v,
    const float* __restrict__ o,
    const float* __restrict__ do,
    float* __restrict__ dq,
    float* __restrict__ dk,
    float* __restrict__ dv,
    int batch_size,
    int num_heads,
    int seq_len,
    int head_dim,
    float scale
) {
    // TODO: Implement backward pass
    // This requires recomputing attention matrix for training

    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= batch_size * num_heads * seq_len * head_dim) return;

    // Placeholder: simple gradient
    dq[idx] = 0.0f;
    dk[idx] = 0.0f;
    dv[idx] = 0.0f;
}

// ============================================================================
// Grouped Query Attention Kernel
// ============================================================================

__global__ void flash_attention_gqa_forward(
    const float* __restrict__ q,
    const float* __restrict__ k,
    const float* __restrict__ v,
    float* __restrict__ output,
    int batch_size,
    int num_heads_q,
    int num_heads_kv,
    int seq_len_q,
    int seq_len_kv,
    int head_dim,
    float scale,
    int is_causal
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= batch_size * num_heads_q * seq_len_q * head_dim) return;

    // Compute head index and replication factor
    int elements_per_head = seq_len_q * head_dim;
    int head_q = (idx / elements_per_head) % num_heads_q;
    int head_kv = head_q * num_heads_kv / num_heads_q;  // Replicate K, V heads

    // Point to the correct K, V head
    // ... (implementation)
}

// ============================================================================
// Paged KV Cache Kernel
// ============================================================================

__global__ void flash_attention_paged_kv_forward(
    const float* __restrict__ q,
    const float* __restrict__ k_cache,
    const float* __restrict__ v_cache,
    const int* __restrict__ page_indices,
    const int* __restrict__ seq_lengths,
    float* __restrict__ output,
    int batch_size,
    int num_heads,
    int seq_len_q,
    int head_dim,
    int page_size,
    float scale
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= batch_size * num_heads * seq_len_q * head_dim) return;

    // Implementation for paged KV cache
    // Each cache page contains page_size tokens
    // page_indices maps (batch, page) to cache pages
}
