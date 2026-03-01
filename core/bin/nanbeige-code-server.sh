#!/bin/bash
# Nanbeige4.1-3B Code Server Startup Script

MODEL_PATH="/mnt/volume3/modelscope_models/DevQuasar/Nanbeige___Nanbeige4___1-3B-GGUF/Nanbeige.Nanbeige4.1-3B.Q8_0.gguf"
LLAMA_BIN="/mnt/volume3/llama_cpp/downloads/llama-b7952/llama-server"
PORT=8889
CTX_SIZE=4096
TEMP=0.3

# Kill existing server
pkill -f "llama-server.*${PORT}" 2>/dev/null
sleep 2

# Start server
echo "Starting Nanbeige4.1-3B code server..."
${LLAMA_BIN} \
  -m "${MODEL_PATH}" \
  -c ${CTX_SIZE} \
  --temp ${TEMP} \
  --top-p 0.95 \
  -ngl 0 \
  --port ${PORT} \
  > /tmp/nanbeige-code.log 2>&1 &

# Wait for server to start
sleep 20

# Check health
if curl -s http://localhost:${PORT}/health > /dev/null 2>&1; then
    echo "Server started successfully on port ${PORT}"
    echo "Test: curl http://localhost:${PORT}/v1/completions"
else
    echo "Server failed to start. Check /tmp/nanbeige-code.log"
    tail -20 /tmp/nanbeige-code.log
fi
