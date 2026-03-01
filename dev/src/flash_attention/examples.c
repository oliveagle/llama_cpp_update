// Flash Attention 简单使用示例
// 演示如何使用 Flash Attention API

#include "flash_attention.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// ============================================================================
// 示例 1: 基础自注意力
// ============================================================================

void example_1_basic_self_attention() {
    printf("\n=== 示例 1: 基础自注意力 ===\n\n");

    // 配置参数
    const int batch_size = 2;
    const int num_heads = 4;
    const int seq_len = 16;
    const int head_dim = 32;

    const int total_elements = batch_size * num_heads * seq_len * head_dim;

    // 分配内存
    float* q = (float*)malloc(total_elements * sizeof(float));
    float* k = (float*)malloc(total_elements * sizeof(float));
    float* v = (float*)malloc(total_elements * sizeof(float));
    float* output = (float*)malloc(total_elements * sizeof(float));

    // 初始化数据 (这里使用简单的值填充，实际应用中应该从模型加载)
    for (int i = 0; i < total_elements; i++) {
        q[i] = ((i % 10) - 5) * 0.01f;  // -0.05 到 0.04
        k[i] = ((i % 13) - 6) * 0.01f;
        v[i] = ((i % 7) - 3) * 0.01f;
    }

    // 创建描述符
    fa_attn_desc_t desc;
    fa_attn_desc_init(&desc);

    desc.batch_size = batch_size;
    desc.num_heads = num_heads;
    desc.seq_len_q = seq_len;
    desc.seq_len_kv = seq_len;
    desc.head_dim = head_dim;
    desc.is_causal = 0;  // 双向注意力
    desc.scale = 1.0f / sqrtf((float)head_dim);  // 标准缩放
    desc.backend = FA_BACKEND_CPU;
    fa_set_default_strides(&desc);

    // 创建 workspace
    size_t workspace_size;
    fa_workspace_query_size(&desc, &workspace_size);
    void* workspace_buf = malloc(workspace_size);
    fa_workspace_t workspace;
    fa_workspace_init(&workspace, &desc, workspace_buf, workspace_size);

    printf("配置信息:\n");
    printf("  Batch: %d, Heads: %d, Seq: %d, Dim: %d\n",
           batch_size, num_heads, seq_len, head_dim);
    printf("  Workspace: %zu bytes\n\n", workspace_size);

    // 运行注意力
    fa_status_t status = fa_attention_forward(
        &desc, q, k, v, NULL, output, &workspace
    );

    if (status == FA_SUCCESS) {
        printf("✓ 计算成功！\n");

        // 打印第一个 token 的输出 (batch=0, head=0, token=0)
        printf("\n第一个 token 的输出 (head 0):\n");
        const float* out_ptr = output + 0 * desc.stride_o_b + 0 * desc.stride_o_h + 0 * desc.stride_o_s;
        printf("  [");
        for (int d = 0; d < 8; d++) {  // 只打印前 8 维
            printf(" %.4f", out_ptr[d]);
        }
        printf(" ... ]\n");
    } else {
        printf("✗ 计算失败: %s\n", fa_status_string(status));
    }

    // 清理
    free(q); free(k); free(v); free(output);
    free(workspace_buf);
}

// ============================================================================
// 示例 2: 因果注意力 (GPT 风格)
// ============================================================================

void example_2_causal_attention() {
    printf("\n=== 示例 2: 因果注意力 ===\n\n");

    const int batch_size = 1;
    const int num_heads = 8;
    const int seq_len = 32;
    const int head_dim = 64;

    const int total_elements = batch_size * num_heads * seq_len * head_dim;

    float* q = (float*)malloc(total_elements * sizeof(float));
    float* k = (float*)malloc(total_elements * sizeof(float));
    float* v = (float*)malloc(total_elements * sizeof(float));
    float* output = (float*)malloc(total_elements * sizeof(float));

    // 简单初始化
    for (int i = 0; i < total_elements; i++) {
        q[i] = (i % 256) / 256.0f;
        k[i] = ((i + 128) % 256) / 256.0f;
        v[i] = ((i + 64) % 256) / 256.0f;
    }

    fa_attn_desc_t desc;
    fa_attn_desc_init(&desc);

    desc.batch_size = batch_size;
    desc.num_heads = num_heads;
    desc.seq_len_q = seq_len;
    desc.seq_len_kv = seq_len;
    desc.head_dim = head_dim;
    desc.is_causal = 1;  // 因果掩码 - 只能看到过去的 token
    desc.scale = 1.0f / sqrtf((float)head_dim);
    desc.backend = FA_BACKEND_CPU;
    fa_set_default_strides(&desc);

    size_t workspace_size;
    fa_workspace_query_size(&desc, &workspace_size);
    void* workspace_buf = malloc(workspace_size);
    fa_workspace_t workspace;
    fa_workspace_init(&workspace, &desc, workspace_buf, workspace_size);

    printf("配置:\n");
    printf("  Causal mask: 启用\n");
    printf("  Sequence length: %d\n\n", seq_len);

    fa_status_t status = fa_attention_forward(
        &desc, q, k, v, NULL, output, &workspace
    );

    if (status == FA_SUCCESS) {
        printf("✓ 因果注意力计算成功！\n");
    }

    free(q); free(k); free(v); free(output);
    free(workspace_buf);
}

// ============================================================================
// 示例 3: 交叉注意力 (Decoder 架构)
// ============================================================================

void example_3_cross_attention() {
    printf("\n=== 示例 3: 交叉注意力 ===\n\n");

    const int batch_size = 1;
    const int num_heads = 8;
    const int seq_len_q = 10;   // Query 序列长度
    const int seq_len_kv = 50;  // Key/Value 序列长度 (encoder 输出)
    const int head_dim = 64;

    const int q_elements = batch_size * num_heads * seq_len_q * head_dim;
    const int kv_elements = batch_size * num_heads * seq_len_kv * head_dim;

    float* q = (float*)malloc(q_elements * sizeof(float));
    float* k = (float*)malloc(kv_elements * sizeof(float));
    float* v = (float*)malloc(kv_elements * sizeof(float));
    float* output = (float*)malloc(q_elements * sizeof(float));

    // 初始化
    for (int i = 0; i < q_elements; i++) q[i] = (i % 128) / 128.0f;
    for (int i = 0; i < kv_elements; i++) {
        k[i] = ((i + 64) % 128) / 128.0f;
        v[i] = ((i + 32) % 128) / 128.0f;
    }

    fa_attn_desc_t desc;
    fa_attn_desc_init(&desc);

    desc.batch_size = batch_size;
    desc.num_heads = num_heads;
    desc.seq_len_q = seq_len_q;
    desc.seq_len_kv = seq_len_kv;  // 不同的序列长度
    desc.head_dim = head_dim;
    desc.is_causal = 0;
    desc.scale = 1.0f / sqrtf((float)head_dim);
    desc.backend = FA_BACKEND_CPU;

    // 设置不同的步长
    desc.stride_q_b = num_heads * seq_len_q * head_dim;
    desc.stride_q_h = seq_len_q * head_dim;
    desc.stride_q_s = head_dim;

    desc.stride_k_b = num_heads * seq_len_kv * head_dim;
    desc.stride_k_h = seq_len_kv * head_dim;
    desc.stride_k_s = head_dim;

    desc.stride_v_b = num_heads * seq_len_kv * head_dim;
    desc.stride_v_h = seq_len_kv * head_dim;
    desc.stride_v_s = head_dim;

    desc.stride_o_b = num_heads * seq_len_q * head_dim;
    desc.stride_o_h = seq_len_q * head_dim;
    desc.stride_o_s = head_dim;

    size_t workspace_size;
    fa_workspace_query_size(&desc, &workspace_size);
    void* workspace_buf = malloc(workspace_size);
    fa_workspace_t workspace;
    fa_workspace_init(&workspace, &desc, workspace_buf, workspace_size);

    printf("配置:\n");
    printf("  Query seq: %d, KV seq: %d\n", seq_len_q, seq_len_kv);
    printf("  (典型的 decoder cross-attention 模式)\n\n");

    fa_status_t status = fa_attention_forward(
        &desc, q, k, v, NULL, output, &workspace
    );

    if (status == FA_SUCCESS) {
        printf("✓ 交叉注意力计算成功！\n");
    }

    free(q); free(k); free(v); free(output);
    free(workspace_buf);
}

// ============================================================================
// 示例 4: 错误处理
// ============================================================================

void example_4_error_handling() {
    printf("\n=== 示例 4: 错误处理 ===\n\n");

    fa_attn_desc_t desc;
    fa_status_t status;

    // 测试 1: 未初始化的描述符
    fa_workspace_t workspace = {NULL, 0, FA_BACKEND_CPU};
    status = fa_attention_forward(NULL, NULL, NULL, NULL, NULL, NULL, &workspace);
    printf("测试 1 - NULL 描述符: %s\n", fa_status_string(status));

    // 测试 2: 不支持的后端
    fa_attn_desc_init(&desc);
    desc.backend = FA_BACKEND_HIP;  // 当前未实现
    status = fa_attention_forward(&desc, NULL, NULL, NULL, NULL, NULL, &workspace);
    printf("测试 2 - 不支持的后端: %s\n", fa_status_string(status));

    // 测试 3: 验证后端支持
    printf("\n后端支持检查:\n");
    printf("  CPU:  %s\n", fa_supports_backend(FA_BACKEND_CPU) ? "✓ 支持" : "✗ 不支持");
    printf("  CUDA: %s\n", fa_supports_backend(FA_BACKEND_CUDA) ? "✓ 支持" : "✗ 不支持");
    printf("  HIP:  %s\n", fa_supports_backend(FA_BACKEND_HIP) ? "✓ 支持" : "✗ 不支持");
}

// ============================================================================
// 主函数
// ============================================================================

int main() {
    printf("====================================\n");
    printf("Flash Attention 使用示例\n");
    printf("====================================\n");

    example_1_basic_self_attention();
    example_2_causal_attention();
    example_3_cross_attention();
    example_4_error_handling();

    printf("\n====================================\n");
    printf("所有示例运行完成！\n");
    printf("====================================\n");

    return 0;
}
