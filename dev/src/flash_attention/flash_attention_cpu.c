// CPU Implementation of Flash Attention
// Uses tiled computation to minimize memory access

#include "flash_attention.h"
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

// ============================================================================
// Constants
// ============================================================================

#define FA_MIN(a, b) ((a) < (b) ? (a) : (b))
#define FA_MAX(a, b) ((a) > (b) ? (a) : (b))

// ============================================================================
// Softmax with online algorithm
// ============================================================================

// Softmax reduction: combines two (m, l) pairs
// (m, l) represents max value and sum(exp(x-m))
struct softmax_reduction {
    float m;  // current max
    float l;  // current sum of exp(x-m)
};

static inline struct softmax_reduction softmax_combine(
    struct softmax_reduction a,
    struct softmax_reduction b
) {
    struct softmax_reduction r;
    if (b.m > a.m) {
        r.m = b.m;
        r.l = b.l + a.l * expf(a.m - b.m);
    } else {
        r.m = a.m;
        r.l = a.l + b.l * expf(b.m - a.m);
    }
    return r;
}

// ============================================================================
// CPU Flash Attention Forward (Tiled)
// ============================================================================

static void fa_cpu_flash_forward_tiled(
    const float* q,    // [batch, num_heads, seq_len_q, head_dim]
    const float* k,    // [batch, num_heads, seq_len_kv, head_dim]
    const float* v,    // [batch, num_heads, seq_len_kv, head_dim]
    float* output,     // [batch, num_heads, seq_len_q, head_dim]
    float* l_cache,    // [seq_len_q] - softmax sum accumulator
    float* m_cache,    // [seq_len_q] - softmax max accumulator
    float* o_tile,     // [block_size_n, head_dim] - output tile
    float* q_tile,     // [block_size_n, head_dim] - query tile
    float* k_tile,     // [block_size_n, head_dim] - key tile
    float* v_tile,     // [block_size_n, head_dim] - value tile

    int batch_idx,
    int head_idx,
    int seq_len_q,
    int seq_len_kv,
    int head_dim,
    int stride_q_bs,
    int stride_q_hs,
    int stride_k_bs,
    int stride_k_hs,
    int stride_v_bs,
    int stride_v_hs,
    int stride_o_bs,
    int stride_o_hs,
    int block_size_n,
    int block_size_d,
    float scale,
    int is_causal
) {
    // Initialize caches
    for (int i = 0; i < seq_len_q; i++) {
        m_cache[i] = -INFINITY;
        l_cache[i] = 0.0f;
        for (int d = 0; d < head_dim; d++) {
            o_tile[i * head_dim + d] = 0.0f;
        }
    }

    // Process K, V in blocks (tr_K, tr_V blocks)
    for (int start_j = 0; start_j < seq_len_kv; start_j += block_size_n) {
        int end_j = FA_MIN(start_j + block_size_n, seq_len_kv);

        // Load K, V tile: [block_n, head_dim]
        for (int j = start_j; j < end_j; j++) {
            const float* k_row = k + batch_idx * stride_q_bs + head_idx * stride_q_hs + j * head_dim;
            const float* v_row = v + batch_idx * stride_k_bs + head_idx * stride_k_hs + j * head_dim;

            int tile_j = j - start_j;
            for (int d = 0; d < head_dim; d++) {
                k_tile[tile_j * head_dim + d] = k_row[d] * scale;
                v_tile[tile_j * head_dim + d] = v_row[d];
            }
        }

        // Process Q in blocks (tr_Q blocks)
        for (int start_i = 0; start_i < seq_len_q; start_i += block_size_n) {
            int end_i = FA_MIN(start_i + block_size_n, seq_len_q);

            // Load Q tile: [block_n, head_dim]
            for (int i = start_i; i < end_i; i++) {
                const float* q_row = q + batch_idx * stride_q_bs + head_idx * stride_q_hs + i * head_dim;
                int tile_i = i - start_i;
                for (int d = 0; d < head_dim; d++) {
                    q_tile[tile_i * head_dim + d] = q_row[d];
                }
            }

            // Compute attention and update output
            for (int i = start_i; i < end_i; i++) {
                int tile_i = i - start_i;
                float m_i = m_cache[i];
                float l_i = l_cache[i];
                float* o_i = output + batch_idx * stride_o_bs + head_idx * stride_o_hs + i * head_dim;

                // Compute Q @ K^T and softmax
                for (int j = start_j; j < end_j; j++) {
                    // Causal mask: only attend to tokens before current
                    if (is_causal && j > i) continue;

                    int tile_j = j - start_j;

                    // Compute attention score: q @ k^T
                    float score = 0.0f;
                    for (int d = 0; d < head_dim; d++) {
                        score += q_tile[tile_i * head_dim + d] * k_tile[tile_j * head_dim + d];
                    }

                    // Softmax: online update
                    float new_m_i = FA_MAX(m_i, score);
                    float alpha = expf(m_i - new_m_i);
                    float beta = expf(score - new_m_i);
                    l_i = alpha * l_i + beta;

                    // Update output
                    for (int d = 0; d < head_dim; d++) {
                        o_i[d] = alpha * o_i[d] + beta * v_tile[tile_j * head_dim + d];
                    }
                    m_i = new_m_i;
                }

                // Normalize output
                for (int d = 0; d < head_dim; d++) {
                    o_i[d] /= l_i;
                }

                m_cache[i] = m_i;
                l_cache[i] = l_i;
            }
        }
    }
}

// ============================================================================
// CPU Reference (Standard) Attention
// ============================================================================

static void fa_cpu_reference_attention(
    const float* q,
    const float* k,
    const float* v,
    float* output,

    int batch_idx,
    int head_idx,
    int seq_len_q,
    int seq_len_kv,
    int head_dim,
    int stride_q_bs,
    int stride_q_hs,
    int stride_k_bs,
    int stride_k_hs,
    int stride_v_bs,
    int stride_v_hs,
    int stride_o_bs,
    int stride_o_hs,
    float scale,
    int is_causal
) {
    // Temporary scores: [seq_len_q, seq_len_kv]
    float* scores = (float*)malloc(seq_len_q * seq_len_kv * sizeof(float));
    if (!scores) return;

    // Compute Q @ K^T
    for (int i = 0; i < seq_len_q; i++) {
        const float* q_row = q + batch_idx * stride_q_bs + head_idx * stride_q_hs + i * head_dim;

        for (int j = 0; j < seq_len_kv; j++) {
            const float* k_row = k + batch_idx * stride_k_bs + head_idx * stride_k_hs + j * head_dim;

            float score = 0.0f;
            for (int d = 0; d < head_dim; d++) {
                score += q_row[d] * k_row[d];
            }
            scores[i * seq_len_kv + j] = score * scale;
        }
    }

    // Softmax over sequence dimension
    for (int i = 0; i < seq_len_q; i++) {
        // Apply causal mask
        if (is_causal) {
            for (int j = i + 1; j < seq_len_kv; j++) {
                scores[i * seq_len_kv + j] = -INFINITY;
            }
        }

        // Find max for numerical stability
        float max_score = -INFINITY;
        for (int j = 0; j < seq_len_kv; j++) {
            if (scores[i * seq_len_kv + j] > max_score) {
                max_score = scores[i * seq_len_kv + j];
            }
        }

        // Compute exp and sum
        float sum = 0.0f;
        for (int j = 0; j < seq_len_kv; j++) {
            scores[i * seq_len_kv + j] = expf(scores[i * seq_len_kv + j] - max_score);
            sum += scores[i * seq_len_kv + j];
        }

        // Normalize
        for (int j = 0; j < seq_len_kv; j++) {
            scores[i * seq_len_kv + j] /= sum;
        }
    }

    // Compute output: scores @ V
    for (int i = 0; i < seq_len_q; i++) {
        float* o_row = output + batch_idx * stride_o_bs + head_idx * stride_o_hs + i * head_dim;

        for (int d = 0; d < head_dim; d++) {
            o_row[d] = 0.0f;
            for (int j = 0; j < seq_len_kv; j++) {
                const float* v_row = v + batch_idx * stride_v_bs + head_idx * stride_v_hs + j * head_dim;
                o_row[d] += scores[i * seq_len_kv + j] * v_row[d];
            }
        }
    }

    free(scores);
}

// ============================================================================
// API Implementations
// ============================================================================

const char* fa_status_string(fa_status_t status) {
    switch (status) {
        case FA_SUCCESS: return "Success";
        case FA_ERROR_INVALID_ARGUMENT: return "Invalid argument";
        case FA_ERROR_OUT_OF_MEMORY: return "Out of memory";
        case FA_ERROR_NOT_IMPLEMENTED: return "Not implemented";
        case FA_ERROR_INTERNAL: return "Internal error";
        case FA_ERROR_HARDWARE_UNAVAILABLE: return "Hardware unavailable";
        default: return "Unknown status";
    }
}

int fa_supports_backend(fa_backend_t backend) {
    // CPU always supported
    if (backend == FA_BACKEND_CPU) return 1;
    // TODO: Add GPU backend detection
    return 0;
}

fa_status_t fa_attn_desc_init(fa_attn_desc_t* desc) {
    if (!desc) return FA_ERROR_INVALID_ARGUMENT;

    memset(desc, 0, sizeof(fa_attn_desc_t));

    // Default values
    desc->has_mask = 0;
    desc->is_causal = 0;
    desc->dropout_prob = 0.0f;
    desc->is_training = 0;
    desc->scale = 1.0f;
    desc->precision = FA_PRECISION_FP32;
    desc->backend = FA_BACKEND_CPU;

    // Default block sizes
    desc->block_size_d = FA_BLOCK_SIZE_D;
    desc->block_size_n = FA_BLOCK_SIZE_N;

    return FA_SUCCESS;
}

void fa_set_default_strides(fa_attn_desc_t* desc) {
    if (!desc) return;

    // Packed layout: [batch, heads, seq_len, dim]
    desc->stride_q_b = desc->num_heads * desc->seq_len_q * desc->head_dim;
    desc->stride_q_h = desc->seq_len_q * desc->head_dim;
    desc->stride_q_s = desc->head_dim;

    desc->stride_k_b = desc->num_heads * desc->seq_len_kv * desc->head_dim;
    desc->stride_k_h = desc->seq_len_kv * desc->head_dim;
    desc->stride_k_s = desc->head_dim;

    desc->stride_v_b = desc->num_heads * desc->seq_len_kv * desc->head_dim;
    desc->stride_v_h = desc->seq_len_kv * desc->head_dim;
    desc->stride_v_s = desc->head_dim;

    desc->stride_o_b = desc->num_heads * desc->seq_len_q * desc->head_dim;
    desc->stride_o_h = desc->seq_len_q * desc->head_dim;
    desc->stride_o_s = desc->head_dim;
}

fa_status_t fa_workspace_query_size(
    const fa_attn_desc_t* desc,
    size_t* size_out
) {
    if (!desc || !size_out) return FA_ERROR_INVALID_ARGUMENT;

    int bs_n = desc->block_size_n;
    int bs_d = desc->block_size_d;

    // Temporary tiles: [block_n, block_d]
    size_t tile_size = bs_n * bs_d * sizeof(float);

    // Softmax accumulators: [max(seq_len_q, seq_len_kv)]
    size_t max_seq = desc->seq_len_q > desc->seq_len_kv ? desc->seq_len_q : desc->seq_len_kv;
    size_t softmax_size = 2 * max_seq * sizeof(float);

    *size_out = tile_size * 4 + softmax_size;  // q, k, v, o tiles + softmax cache

    return FA_SUCCESS;
}

fa_status_t fa_workspace_init(
    fa_workspace_t* workspace,
    const fa_attn_desc_t* desc,
    void* buffer,
    size_t buffer_size
) {
    if (!workspace || !desc) return FA_ERROR_INVALID_ARGUMENT;

    workspace->data = buffer;
    workspace->size = buffer_size;
    workspace->backend = desc->backend;

    return FA_SUCCESS;
}

fa_status_t fa_cpu_attention_forward(
    const fa_attn_desc_t* desc,
    const float* q,
    const float* k,
    const float* v,
    const float* attention_mask,
    float* output,
    fa_workspace_t* workspace
) {
    if (!desc || !q || !k || !v || !output) {
        return FA_ERROR_INVALID_ARGUMENT;
    }

    // Check workspace
    size_t required_size;
    fa_status_t status = fa_workspace_query_size(desc, &required_size);
    if (status != FA_SUCCESS) return status;

    if (!workspace || workspace->size < required_size) {
        return FA_ERROR_INVALID_ARGUMENT;
    }

    // Get temporary storage from workspace
    float* workspace_ptr = (float*)workspace->data;
    int bs_n = desc->block_size_n;
    int bs_d = desc->block_size_d;

    float* l_cache = workspace_ptr;
    float* m_cache = l_cache + desc->seq_len_q;
    float* o_tile = m_cache + desc->seq_len_q;
    float* q_tile = o_tile + bs_n * bs_d;
    float* k_tile = q_tile + bs_n * bs_d;
    float* v_tile = k_tile + bs_n * bs_d;

    // Compute scaling factor if not set
    float scale = desc->scale > 0.0f ? desc->scale : 1.0f / sqrtf((float)desc->head_dim);

    // Process each batch and head
    for (int b = 0; b < desc->batch_size; b++) {
        for (int h = 0; h < desc->num_heads; h++) {
            fa_cpu_flash_forward_tiled(
                q, k, v, output,
                l_cache, m_cache, o_tile, q_tile, k_tile, v_tile,
                b, h,
                desc->seq_len_q,
                desc->seq_len_kv,
                desc->head_dim,
                desc->stride_q_b,
                desc->stride_q_h,
                desc->stride_k_b,
                desc->stride_k_h,
                desc->stride_v_b,
                desc->stride_v_h,
                desc->stride_o_b,
                desc->stride_o_h,
                bs_n,
                bs_d,
                scale,
                desc->is_causal
            );
        }
    }

    // TODO: Apply attention_mask if provided
    (void)attention_mask;

    return FA_SUCCESS;
}

fa_status_t fa_reference_attention(
    const fa_attn_desc_t* desc,
    const float* q,
    const float* k,
    const float* v,
    const float* attention_mask,
    float* output
) {
    if (!desc || !q || !k || !v || !output) {
        return FA_ERROR_INVALID_ARGUMENT;
    }

    float scale = desc->scale > 0.0f ? desc->scale : 1.0f / sqrtf((float)desc->head_dim);

    for (int b = 0; b < desc->batch_size; b++) {
        for (int h = 0; h < desc->num_heads; h++) {
            fa_cpu_reference_attention(
                q, k, v, output,
                b, h,
                desc->seq_len_q,
                desc->seq_len_kv,
                desc->head_dim,
                desc->stride_q_b,
                desc->stride_q_h,
                desc->stride_k_b,
                desc->stride_k_h,
                desc->stride_v_b,
                desc->stride_v_h,
                desc->stride_o_b,
                desc->stride_o_h,
                scale,
                desc->is_causal
            );
        }
    }

    (void)attention_mask;
    return FA_SUCCESS;
}

fa_status_t fa_attention_forward(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    const void* attention_mask,
    void* output,
    fa_workspace_t* workspace
) {
    if (!desc) return FA_ERROR_INVALID_ARGUMENT;

    switch (desc->backend) {
        case FA_BACKEND_CPU:
            return fa_cpu_attention_forward(
                desc, (const float*)q, (const float*)k, (const float*)v,
                (const float*)attention_mask, (float*)output, workspace
            );
        default:
            return FA_ERROR_NOT_IMPLEMENTED;
    }
}

fa_status_t fa_attention_forward_with_bias(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    const void* attention_bias,
    const void* attention_mask,
    void* output,
    fa_workspace_t* workspace
) {
    (void)desc; (void)q; (void)k; (void)v; (void)attention_bias;
    (void)attention_mask; (void)output; (void)workspace;
    return FA_ERROR_NOT_IMPLEMENTED;
}

fa_status_t fa_attention_paged_kv(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k_cache,
    const void* v_cache,
    const int32_t* page_indices,
    const int32_t* seq_lengths,
    int page_size,
    void* output,
    fa_workspace_t* workspace
) {
    (void)desc; (void)q; (void)k_cache; (void)v_cache;
    (void)page_indices; (void)seq_lengths; (void)page_size;
    (void)output; (void)workspace;
    return FA_ERROR_NOT_IMPLEMENTED;
}

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
) {
    (void)desc; (void)q; (void)k; (void)v; (void)output; (void)grad_output;
    (void)attention_mask; (void)grad_q; (void)grad_k; (void)grad_v;
    (void)workspace;
    return FA_ERROR_NOT_IMPLEMENTED;
}

fa_status_t fa_attention_sliding_window(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    int window_size,
    void* output,
    fa_workspace_t* workspace
) {
    (void)desc; (void)q; (void)k; (void)v; (void)window_size;
    (void)output; (void)workspace;
    return FA_ERROR_NOT_IMPLEMENTED;
}

fa_status_t fa_attention_grouped_query(
    const fa_attn_desc_t* desc,
    const void* q,
    const void* k,
    const void* v,
    int num_heads_q,
    int num_heads_kv,
    void* output,
    fa_workspace_t* workspace
) {
    (void)desc; (void)q; (void)k; (void)v; (void)num_heads_q;
    (void)num_heads_kv; (void)output; (void)workspace;
    return FA_ERROR_NOT_IMPLEMENTED;
}
