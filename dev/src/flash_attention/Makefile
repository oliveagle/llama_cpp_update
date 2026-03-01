# Makefile for Flash Attention
# Supports both CPU and CUDA builds

CC = gcc
NVCC = nvcc

# Compiler flags
CFLAGS = -O3 -Wall -Wextra -std=c99 -I..
NVCCFLAGS = -O3 -arch=sm_70 -std=c++11 -I..

# Source files
CPU_SRC = flash_attention_cpu.c test_flash_attention.c
EXAMPLES_SRC = flash_attention_cpu.c examples.c
CUDA_SRC = flash_attention_cuda.cu test_flash_attention.c

# Targets
CPU_TARGET = build/test_flash_attention
EXAMPLES_TARGET = build/examples
CUDA_TARGET = build/test_flash_attention_cuda

# Directories
BUILD_DIR = build

.PHONY: all cpu cuda examples clean test help

all: cpu

help:
	@echo "Flash Attention Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all       - Build CPU version (default)"
	@echo "  cpu       - Build CPU version only"
	@echo "  examples  - Build and run examples"
	@echo "  cuda      - Build CUDA version only"
	@echo "  clean     - Remove build artifacts"
	@echo "  test      - Run CPU tests"
	@echo ""
	@echo "Examples:"
	@echo "  make cpu       # Build CPU version"
	@echo "  make examples  # Build and run examples"
	@echo "  make cuda      # Build CUDA version (requires nvcc)"
	@echo "  make test      # Run tests"

cpu: $(BUILD_DIR) $(CPU_TARGET)

examples: $(BUILD_DIR) $(EXAMPLES_TARGET)
	@echo "Running examples..."
	$(EXAMPLES_TARGET)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(CPU_TARGET): $(CPU_SRC)
	@echo "Building CPU version..."
	$(CC) $(CFLAGS) -o $@ $^ -lm
	@echo "CPU build complete: $@"

$(CUDA_TARGET): $(CUDA_SRC)
	@echo "Building CUDA version..."
	$(NVCC) $(NVCCFLAGS) -c flash_attention_cuda.cu -o $(BUILD_DIR)/flash_attention_cuda.o
	$(NVCC) $(NVCCFLAGS) -o $@ $(BUILD_DIR)/flash_attention_cuda.o test_flash_attention.c -lm
	@echo "CUDA build complete: $@"

test: $(CPU_TARGET)
	@echo "Running CPU tests..."
	$(CPU_TARGET)

test-cuda: $(CUDA_TARGET)
	@echo "Running CUDA tests..."
	$(CUDA_TARGET)

clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)
	@echo "Clean complete"

# Installation (optional)
PREFIX ?= /usr/local
install: cpu
	@echo "Installing to $(PREFIX)/bin..."
	install -d $(PREFIX)/bin
	install -m 755 $(CPU_TARGET) $(PREFIX)/bin/flash-attention-test
	@echo "Install complete"

uninstall:
	@echo "Uninstalling..."
	rm -f $(PREFIX)/bin/flash-attention-test
	@echo "Uninstall complete"
