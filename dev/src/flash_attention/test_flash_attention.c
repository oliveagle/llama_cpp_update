// Flash Attention Test and Demo
// Test the CPU implementation with various configurations

#include "flash_attention.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define FA_MIN(a, b) ((a) < (b) ? (a) : (b))

// ============================================================================
// Utility Functions
// ============================================================================

static void random_float_array(float* arr, int n, float min, float max) {
    for (int i = 0; i < n; i++) {
        float scale = max - min;
        arr[i] = min + scale * ((float)rand() / (float)RAND_MAX);
    }
}

static void print_array(const char* name, const float* arr, int rows, int cols) {
    printf("%s [%d x %d]:\n", name, rows, cols);
    for (int i = 0; i < rows; i++) {
        printf("  [");
        for (int j = 0; j < cols; j++) {
            printf(" %6.3f", arr[i * cols + j]);
        }
        printf(" ]\n");
    }
}

static float max_abs_error(const float* a, const float* b, int n) {
    float max_err = 0.0f;
    for (int i = 0; i < n; i++) {
        float err = fabsf(a[i] - b[i]);
        if (err > max_err) max_err = err;
    }
    return max_err;
}

static float mean_abs_error(const float* a, const float* b, int n) {
    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        sum += fabsf(a[i] - b[i]);
    }
    return sum / (float)n;
}

// ============================================================================
// Test 1: Small Self-Attention
// ============================================================================

int test_small_self_attention() {
    printf("\n=== Test 1: Small Self-Attention ===\n\n");

    // Configuration
    const int batch_size = 1;
    const int num_heads = 1;
    const int seq_len = 4;
    const int head_dim = 8;

    const int total_elements = batch_size * num_heads * seq_len * head_dim;

    // Allocate memory
    float* q = (float*)malloc(total_elements * sizeof(float));
    float* k = (float*)malloc(total_elements * sizeof(float));
    float* v = (float*)malloc(total_elements * sizeof(float));
    float* out_flash = (float*)malloc(total_elements * sizeof(float));
    float* out_ref = (float*)malloc(total_elements * sizeof(float));

    // Initialize with random data
    srand(42);
    random_float_array(q, total_elements, -0.5f, 0.5f);
    random_float_array(k, total_elements, -0.5f, 0.5f);
    random_float_array(v, total_elements, -0.5f, 0.5f);

    // Setup descriptor
    fa_attn_desc_t desc;
    fa_attn_desc_init(&desc);
    desc.batch_size = batch_size;
    desc.num_heads = num_heads;
    desc.seq_len_q = seq_len;
    desc.seq_len_kv = seq_len;
    desc.head_dim = head_dim;
    desc.is_causal = 0;
    fa_set_default_strides(&desc);

    // Allocate workspace
    size_t workspace_size;
    fa_workspace_query_size(&desc, &workspace_size);
    void* workspace_buf = malloc(workspace_size);
    fa_workspace_t workspace;
    fa_workspace_init(&workspace, &desc, workspace_buf, workspace_size);

    printf("Configuration:\n");
    printf("  Batch size:    %d\n", batch_size);
    printf("  Num heads:     %d\n", num_heads);
    printf("  Sequence len:  %d\n", seq_len);
    printf("  Head dim:      %d\n", head_dim);
    printf("  Workspace:     %zu bytes\n", workspace_size);
    printf("\n");

    // Run reference attention
    printf("Running reference attention...\n");
    fa_reference_attention(&desc, q, k, v, NULL, out_ref);

    // Run flash attention
    printf("Running flash attention...\n");
    fa_cpu_attention_forward(&desc, q, k, v, NULL, out_flash, &workspace);

    // Print results
    printf("\nInput Q:\n");
    print_array("  Q", q, seq_len, head_dim);

    printf("\nReference output:\n");
    print_array("  Ref", out_ref, seq_len, head_dim);

    printf("\nFlash output:\n");
    print_array("  Flash", out_flash, seq_len, head_dim);

    // Check error
    float max_err = max_abs_error(out_ref, out_flash, total_elements);
    float mean_err = mean_abs_error(out_ref, out_flash, total_elements);

    printf("\nError analysis:\n");
    printf("  Max absolute error:  %e\n", max_err);
    printf("  Mean absolute error: %e\n", mean_err);

    int passed = max_err < 1e-5f;
    printf("Test %s!\n", passed ? "PASSED" : "FAILED");

    // Cleanup
    free(q);
    free(k);
    free(v);
    free(out_flash);
    free(out_ref);
    free(workspace_buf);

    return passed ? 0 : 1;
}

// ============================================================================
// Test 2: Causal Masked Attention
// ============================================================================

int test_causal_attention() {
    printf("\n=== Test 2: Causal Masked Attention ===\n\n");

    const int batch_size = 1;
    const int num_heads = 1;
    const int seq_len = 5;
    const int head_dim = 8;

    const int total_elements = batch_size * num_heads * seq_len * head_dim;

    float* q = (float*)malloc(total_elements * sizeof(float));
    float* k = (float*)malloc(total_elements * sizeof(float));
    float* v = (float*)malloc(total_elements * sizeof(float));
    float* out_flash = (float*)malloc(total_elements * sizeof(float));
    float* out_ref = (float*)malloc(total_elements * sizeof(float));

    srand(1234);
    random_float_array(q, total_elements, -0.3f, 0.3f);
    random_float_array(k, total_elements, -0.3f, 0.3f);
    random_float_array(v, total_elements, -0.3f, 0.3f);

    fa_attn_desc_t desc;
    fa_attn_desc_init(&desc);
    desc.batch_size = batch_size;
    desc.num_heads = num_heads;
    desc.seq_len_q = seq_len;
    desc.seq_len_kv = seq_len;
    desc.head_dim = head_dim;
    desc.is_causal = 1;  // causal mask
    fa_set_default_strides(&desc);

    size_t workspace_size;
    fa_workspace_query_size(&desc, &workspace_size);
    void* workspace_buf = malloc(workspace_size);
    fa_workspace_t workspace;
    fa_workspace_init(&workspace, &desc, workspace_buf, workspace_size);

    printf("Configuration:\n");
    printf("  Causal mask:   enabled\n");
    printf("  Sequence len:  %d\n", seq_len);
    printf("\n");

    fa_reference_attention(&desc, q, k, v, NULL, out_ref);
    fa_cpu_attention_forward(&desc, q, k, v, NULL, out_flash, &workspace);

    printf("Reference output (causal):\n");
    print_array("  Ref", out_ref, seq_len, head_dim);

    printf("\nFlash output (causal):\n");
    print_array("  Flash", out_flash, seq_len, head_dim);

    float max_err = max_abs_error(out_ref, out_flash, total_elements);
    printf("\nMax absolute error: %e\n", max_err);

    int passed = max_err < 1e-5f;
    printf("Test %s!\n", passed ? "PASSED" : "FAILED");

    free(q); free(k); free(v);
    free(out_flash); free(out_ref);
    free(workspace_buf);

    return passed ? 0 : 1;
}

// ============================================================================
// Test 3: Multi-Head Attention
// ============================================================================

int test_multi_head_attention() {
    printf("\n=== Test 3: Multi-Head Attention ===\n\n");

    const int batch_size = 1;
    const int num_heads = 2;
    const int seq_len = 3;
    const int head_dim = 16;

    const int total_elements = batch_size * num_heads * seq_len * head_dim;

    float* q = (float*)malloc(total_elements * sizeof(float));
    float* k = (float*)malloc(total_elements * sizeof(float));
    float* v = (float*)malloc(total_elements * sizeof(float));
    float* out_flash = (float*)malloc(total_elements * sizeof(float));
    float* out_ref = (float*)malloc(total_elements * sizeof(float));

    srand(5678);
    random_float_array(q, total_elements, -0.2f, 0.2f);
    random_float_array(k, total_elements, -0.2f, 0.2f);
    random_float_array(v, total_elements, -0.2f, 0.2f);

    fa_attn_desc_t desc;
    fa_attn_desc_init(&desc);
    desc.batch_size = batch_size;
    desc.num_heads = num_heads;
    desc.seq_len_q = seq_len;
    desc.seq_len_kv = seq_len;
    desc.head_dim = head_dim;
    desc.is_causal = 0;
    fa_set_default_strides(&desc);

    size_t workspace_size;
    fa_workspace_query_size(&desc, &workspace_size);
    void* workspace_buf = malloc(workspace_size);
    fa_workspace_t workspace;
    fa_workspace_init(&workspace, &desc, workspace_buf, workspace_size);

    printf("Configuration:\n");
    printf("  Num heads:     %d\n", num_heads);
    printf("  Head dim:      %d\n", head_dim);
    printf("\n");

    fa_reference_attention(&desc, q, k, v, NULL, out_ref);
    fa_cpu_attention_forward(&desc, q, k, v, NULL, out_flash, &workspace);

    float max_err = max_abs_error(out_ref, out_flash, total_elements);
    printf("Max absolute error: %e\n", max_err);

    // Print head 0
    printf("\nHead 0 - Reference output:\n");
    print_array("  Ref", out_ref, seq_len, head_dim);

    printf("\nHead 0 - Flash output:\n");
    print_array("  Flash", out_flash, seq_len, head_dim);

    int passed = max_err < 1e-5f;
    printf("\nTest %s!\n", passed ? "PASSED" : "FAILED");

    free(q); free(k); free(v);
    free(out_flash); free(out_ref);
    free(workspace_buf);

    return passed ? 0 : 1;
}

// ============================================================================
// Benchmark
// ============================================================================

void benchmark_attention() {
    printf("\n=== Benchmark ===\n\n");

    // Test various sizes
    const int test_sizes[][3] = {
        {32, 8, 64},    // seq_len, heads, head_dim
        {64, 8, 64},
        {128, 8, 64},
        {256, 8, 64},
        {512, 8, 64},
    };

    const int num_tests = sizeof(test_sizes) / sizeof(test_sizes[0]);

    printf("%-12s %-8s %-10s %-15s %-15s\n",
           "SeqLen", "Heads", "HeadDim", "Ref (ms)", "Flash (ms)");
    printf("------------------------------------------------------------\n");

    for (int t = 0; t < num_tests; t++) {
        int seq_len = test_sizes[t][0];
        int num_heads = test_sizes[t][1];
        int head_dim = test_sizes[t][2];
        int batch_size = 1;

        int total_elements = batch_size * num_heads * seq_len * head_dim;

        float* q = (float*)malloc(total_elements * sizeof(float));
        float* k = (float*)malloc(total_elements * sizeof(float));
        float* v = (float*)malloc(total_elements * sizeof(float));
        float* out = (float*)malloc(total_elements * sizeof(float));

        srand(t);
        random_float_array(q, total_elements, -0.1f, 0.1f);
        random_float_array(k, total_elements, -0.1f, 0.1f);
        random_float_array(v, total_elements, -0.1f, 0.1f);

        fa_attn_desc_t desc;
        fa_attn_desc_init(&desc);
        desc.batch_size = batch_size;
        desc.num_heads = num_heads;
        desc.seq_len_q = seq_len;
        desc.seq_len_kv = seq_len;
        desc.head_dim = head_dim;
        desc.is_causal = 1;
        fa_set_default_strides(&desc);

        size_t workspace_size;
        fa_workspace_query_size(&desc, &workspace_size);
        void* workspace_buf = malloc(workspace_size);
        fa_workspace_t workspace;
        fa_workspace_init(&workspace, &desc, workspace_buf, workspace_size);

        // Benchmark reference
        clock_t start = clock();
        int runs = FA_MIN(10, 1000 / (seq_len / 64 + 1));
        for (int i = 0; i < runs; i++) {
            fa_reference_attention(&desc, q, k, v, NULL, out);
        }
        clock_t end = clock();
        double ref_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000.0 / runs;

        // Benchmark flash
        start = clock();
        for (int i = 0; i < runs; i++) {
            fa_cpu_attention_forward(&desc, q, k, v, NULL, out, &workspace);
        }
        end = clock();
        double flash_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000.0 / runs;

        printf("%-12d %-8d %-10d %-15.2f %-15.2f\n",
               seq_len, num_heads, head_dim, ref_ms, flash_ms);

        free(q); free(k); free(v); free(out);
        free(workspace_buf);
    }
}

// ============================================================================
// Main
// ============================================================================

int main() {
    printf("====================================\n");
    printf("Flash Attention C Implementation\n");
    printf("====================================\n");

    int failed = 0;

    failed += test_small_self_attention();
    failed += test_causal_attention();
    failed += test_multi_head_attention();

    benchmark_attention();

    printf("\n====================================\n");
    if (failed == 0) {
        printf("All tests PASSED!\n");
    } else {
        printf("%d tests FAILED!\n", failed);
    }
    printf("====================================\n");

    return failed;
}
