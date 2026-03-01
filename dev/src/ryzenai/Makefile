# RyzenAI Backend Makefile
# Build RyzenAI-Server backend for llama.cpp

CXX = g++
CXXFLAGS = -std=c++17 -fPIC -Wall -Wextra -O2
INCLUDES = -I.

# Find dependencies
CURL_CFLAGS = $(shell pkg-config --cflags libcurl 2>/dev/null || echo "-I/usr/include/curl")
CURL_LIBS = $(shell pkg-config --libs libcurl 2>/dev/null || echo "-lcurl")
LIBZIP_LIBS = -lzip

# Source files
SRCS = ryzenai_backend.cpp process_manager.cpp http_client.cpp downloader.cpp
OBJS = $(SRCS:.cpp=.o)

# Output
TARGET = libryzenai-backend.a
SERVER_TARGET = llama-npu-server

.PHONY: all clean install server

all: $(TARGET)

$(TARGET): $(OBJS)
	ar rcs $@ $^
	@echo "Built $(TARGET) successfully"

# Build standalone server
server: $(TARGET) main.o
	$(CXX) $(CXXFLAGS) -o $(SERVER_TARGET) main.o $(OBJS) $(CURL_LIBS) $(LIBZIP_LIBS) -pthread
	@echo "Built $(SERVER_TARGET) successfully"

main.o: main.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(CURL_CFLAGS) -c $< -o $@

%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(CURL_CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET) main.o $(SERVER_TARGET)

install: $(TARGET)
	@echo "Installing RyzenAI backend..."
	mkdir -p ../lib
	cp $(TARGET) ../lib/
	@echo "Installation complete"

# Test build
test: $(TARGET)
	@echo "Testing RyzenAI backend..."
	@echo "Build successful!"
	@echo ""
	@echo "To use RyzenAI backend:"
	@echo "  1. Download ryzenai-server: ./llama-server --ryzenai-download"
	@echo "  2. Run with ONNX model: ./llama-server --ryzenai --ryzenai-model model.onnx"

# Build and test standalone server
test-server: server
	@echo ""
	@echo "Standalone server built: $(SERVER_TARGET)"
	@echo ""
	@echo "Usage:"
	@echo "  ./$(SERVER_TARGET) --model /path/to/model.onnx --port 8400"
	@echo "  ./$(SERVER_TARGET) --download  # Download ryzenai-server"
	@echo "  ./$(SERVER_TARGET) --help      # Show help"
