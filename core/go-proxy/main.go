package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"
)

// ============ Configuration ============

const (
	LLamaBaseURL          = "http://localhost:8401"
	DefaultModel          = "Qwen3.5-4B-UD-Q4_K_XL"
	ListenPort            = 8402
	JSONL_LOG_PATH        = "/mnt/volume3/llama_cpp/core/logs/anthropic-proxy-requests.jsonl"
	JSONL_LOG_MAX_SIZE    = 100 * 1024 * 1024 // 100MB
	JSONL_LOG_MAX_BACKUPS = 5                 // Keep 5 old files
)

// ============ Metrics (in-memory, cached from JSONL) ============

var (
	metricsMutex     sync.RWMutex
	totalRequests   int64
	totalResponses int64
	totalErrors    int64
	lastMetricsUpdate time.Time
	metricsCache    []byte
)

// ============ JSONL Logger ============

var jsonlLogFile *os.File

func initJSONLLogger() error {
	var err error

	// Check if file needs rotation
	fileInfo, err := os.Stat(JSONL_LOG_PATH)
	if err != nil {
		return err
	}

	// Rotate if file exceeds max size
	if fileInfo.Size() > JSONL_LOG_MAX_SIZE {
		log.Printf("JSONL log file size %.2fMB exceeds max, rotating", float64(fileInfo.Size())/(1024*1024))
		if err := os.Rename(JSONL_LOG_PATH, JSONL_LOG_PATH+".old"); err != nil {
			log.Printf("Error renaming old log: %v", err)
		}
	}

	jsonlLogFile, err = os.OpenFile(JSONL_LOG_PATH, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	return nil
}

func logJSONL(entry map[string]interface{}) {
	if jsonlLogFile == nil {
		return
	}
	entry["timestamp"] = time.Now().Format(time.RFC3339Nano)
	data, err := json.Marshal(entry)
	if err != nil {
		log.Printf("Error marshaling JSONL entry: %v", err)
		return
	}
	_, err = jsonlLogFile.Write(append(data, '\n'))
	if err != nil {
		log.Printf("Error writing JSONL log: %v", err)
	}
	jsonlLogFile.Sync()
}

// rotateJSONLLog checks if rotation is needed and performs it
func rotateJSONLLog() {
	if jsonlLogFile == nil {
		return
	}

	fileInfo, err := jsonlLogFile.Stat()
	if err != nil {
		return
	}

	if fileInfo.Size() > JSONL_LOG_MAX_SIZE {
		log.Printf("JSONL log file size %.2fMB exceeds max, rotating...", float64(fileInfo.Size())/(1024*1024))

		// Close current file
		jsonlLogFile.Close()

		// Generate backup filename with timestamp
		timestamp := time.Now().Format("20060102_150405")
		backupPath := fmt.Sprintf("%s.%s", JSONL_LOG_PATH, timestamp)

		// Rename current file to backup
		if err := os.Rename(JSONL_LOG_PATH, backupPath); err != nil {
			log.Printf("Error renaming log file: %v", err)
		} else {
			log.Printf("Rotated log to: %s", backupPath)

			// Delete oldest backup if we have too many
			cleanupOldBackups()
		}

		// Open new file
		var err error
		jsonlLogFile, err = os.OpenFile(JSONL_LOG_PATH, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			log.Printf("Error opening new log file: %v", err)
		}
	}
}

// cleanupOldBackups removes old backup files, keeping only the most recent ones
func cleanupOldBackups() {
	// Find all backup files
	pattern := JSONL_LOG_PATH + ".*"
	matches, err := filepath.Glob(pattern)
	if err != nil {
		return
	}

	// Sort by modification time (newest first)
	type fileInfo struct {
		name    string
		modTime time.Time
	}

	var files []fileInfo
	for _, path := range matches {
		if info, err := os.Stat(path); err == nil {
			files = append(files, fileInfo{path, info.ModTime()})
		}
	}

	sort.Slice(files, func(i, j int) bool {
		return files[i].modTime.After(files[j].modTime)
	})

	// Delete old files, keep only JSONL_LOG_MAX_BACKUPS
	if len(files) > JSONL_LOG_MAX_BACKUPS {
		for i := JSONL_LOG_MAX_BACKUPS; i < len(files); i++ {
			if err := os.Remove(files[i].name); err != nil {
				log.Printf("Error removing old backup %s: %v", files[i].name, err)
			} else {
				log.Printf("Removed old backup: %s", files[i].name)
			}
		}
	}
}

// updateMetricsFromJSONL parses JSONL log to update metrics
// This is cached and only updated every 30 seconds
func updateMetricsFromJSONL() {
	now := time.Now()

	metricsMutex.RLock()
	if !lastMetricsUpdate.IsZero() && now.Sub(lastMetricsUpdate) < 30*time.Second {
		metricsMutex.RUnlock()
		return
	}
	metricsMutex.RUnlock()

	metricsMutex.Lock()
	defer metricsMutex.Unlock()

	// Parse JSONL file
	var requests, responses, errors int64
	var fileSize int64

	fileInfo, err := os.Stat(JSONL_LOG_PATH)
	if err == nil {
		fileSize = fileInfo.Size()
	}

	if jsonlLogFile != nil {
		// We need to read the file to count entries
		// For efficiency, we'll reopen and scan
		if f, err := os.Open(JSONL_LOG_PATH); err == nil {
			defer f.Close()
			scanner := bufio.NewScanner(f)
			// Increase buffer size to handle large JSONL entries
			buf := make([]byte, 0, 4*1024*1024) // 4MB buffer
			scanner.Buffer(buf, 4*1024*1024)
			for scanner.Scan() {
				line := scanner.Bytes()
				if len(line) == 0 {
					continue
				}
				// Quick string search for performance (handle both with/without spaces)
				lineStr := string(line)
				if strings.Contains(lineStr, `"type":"request"`) || strings.Contains(lineStr, `"type": "request"`) {
					requests++
				} else if strings.Contains(lineStr, `"type":"response"`) || strings.Contains(lineStr, `"type": "response"`) {
					responses++
				} else if strings.Contains(lineStr, `"type":"error"`) || strings.Contains(lineStr, `"type": "error"`) {
					errors++
				}
			}
		}
	}

	totalRequests = requests
	totalResponses = responses
	totalErrors = errors
	lastMetricsUpdate = now

	// Update metrics cache
	successRate := 0.0
	if requests > 0 {
		successRate = float64(responses) / float64(requests) * 100
	}

	errorRate := 0.0
	if requests > 0 {
		errorRate = float64(errors) / float64(requests) * 100
	}

	metricsCache = []byte(fmt.Sprintf(`# HELP anthropic_proxy_requests_total Total number of requests received
# TYPE anthropic_proxy_requests_total counter
anthropic_proxy_requests_total %d

# HELP anthropic_proxy_responses_total Total number of responses sent
# TYPE anthropic_proxy_responses_total counter
anthropic_proxy_responses_total %d

# HELP anthropic_proxy_errors_total Total number of errors
# TYPE anthropic_proxy_errors_total counter
anthropic_proxy_errors_total %d

# HELP anthropic_proxy_log_file_size Size of JSONL log file in bytes
# TYPE anthropic_proxy_log_file_size gauge
anthropic_proxy_log_file_size %d

# HELP anthropic_proxy_success_rate Request success rate percentage
# TYPE anthropic_proxy_success_rate gauge
anthropic_proxy_success_rate %.2f

# HELP anthropic_proxy_error_rate Request error rate percentage
# TYPE anthropic_proxy_error_rate gauge
anthropic_proxy_error_rate %.2f

# HELP anthropic_proxy_last_update_time Unix timestamp of last metrics update
# TYPE anthropic_proxy_last_update_time gauge
anthropic_proxy_last_update_time %d
`, requests, responses, errors, fileSize, successRate, errorRate, now.Unix()))
}

// ============ Simplified: Use json.RawMessage and map for flexibility ============

type OpenAIChatRequest struct {
	Model       string              `json:"model"`
	Messages    []OpenAIMessage    `json:"messages"`
	MaxTokens   int                 `json:"max_tokens,omitempty"`
	Temperature float64             `json:"temperature,omitempty"`
	Stream      bool                `json:"stream"`
	Tools       []OpenAITool        `json:"tools,omitempty"`
	ToolChoice  interface{}         `json:"tool_choice,omitempty"`
}

type OpenAIMessage struct {
	Role       string            `json:"role"`
	Content    interface{}       `json:"content"` // string or nil
	ToolCalls  []OpenAIToolCall `json:"tool_calls,omitempty"`
	ToolCallID string            `json:"tool_call_id,omitempty"`
}

type OpenAIToolCall struct {
	ID       string         `json:"id"`
	Type     string         `json:"type"`
	Function OpenAIFunction `json:"function"`
}

type OpenAIFunction struct {
	Name      string `json:"name"`
	Arguments string `json:"arguments"`
}

type OpenAITool struct {
	Type     string           `json:"type"`
	Function OpenAIToolFunction `json:"function"`
}

type OpenAIToolFunction struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description,omitempty"`
	Parameters  map[string]interface{} `json:"parameters"`
}

type OpenAIChatResponse struct {
	ID      string         `json:"id"`
	Object  string         `json:"object"`
	Created int64          `json:"created"`
	Model   string         `json:"model"`
	Choices []OpenAIChoice `json:"choices"`
	Usage   OpenAIUsage    `json:"usage"`
}

type OpenAIChoice struct {
	Index        int           `json:"index"`
	Message      OpenAIMessage `json:"message"`
	FinishReason string        `json:"finish_reason"`
}

type OpenAIUsage struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

type ModelListResponse struct {
	Object string      `json:"object"`
	Data   []ModelInfo `json:"data"`
}

type ModelInfo struct {
	ID      string `json:"id"`
	Object  string `json:"object"`
	Created int64  `json:"created"`
	OwnedBy string `json:"owned_by"`
}

// ============ Helper Functions ============

func mapModel(modelName string) string {
	if strings.Contains(modelName, "claude-3-5-sonnet") {
		return DefaultModel
	} else if strings.Contains(modelName, "claude-3-opus") {
		return "Qwen3.5-9B-UD-Q4_K_XL"
	} else if strings.Contains(modelName, "claude-3-haiku") {
		return "Qwen3.5-0.8B-UD-Q8_K_XL"
	}
	return modelName
}

func extractTextFromContent(content interface{}) string {
	if content == nil {
		return ""
	}

	if str, ok := content.(string); ok {
		return str
	}

	if arr, ok := content.([]interface{}); ok {
		var parts []string
		for _, item := range arr {
			if itemMap, ok := item.(map[string]interface{}); ok {
				if text, ok := itemMap["text"].(string); ok {
					parts = append(parts, text)
				}
			}
		}
		return strings.Join(parts, "")
	}

	return ""
}

func convertAnthropicRequestToOpenAI(bodyBytes []byte) (*OpenAIChatRequest, error) {
	var raw map[string]interface{}
	if err := json.Unmarshal(bodyBytes, &raw); err != nil {
		return nil, err
	}

	model, _ := raw["model"].(string)
	model = mapModel(model)
	if model == "" {
		model = DefaultModel
	}

	maxTokens := 4096
	if mt, ok := raw["max_tokens"].(float64); ok {
		maxTokens = int(mt)
	}

	temperature := 0.7
	if temp, ok := raw["temperature"].(float64); ok {
		temperature = temp
	}

	var messages []OpenAIMessage

	if system, ok := raw["system"]; ok && system != nil {
		systemText := extractTextFromContent(system)
		if systemText != "" {
			messages = append(messages, OpenAIMessage{
				Role:    "system",
				Content: systemText,
			})
		}
	}

	if rawMsgs, ok := raw["messages"].([]interface{}); ok {
		for _, rawMsg := range rawMsgs {
			if msgMap, ok := rawMsg.(map[string]interface{}); ok {
				role, _ := msgMap["role"].(string)
				content := msgMap["content"]

				textContent := extractTextFromContent(content)

				if contentArr, ok := content.([]interface{}); ok && len(contentArr) > 0 {
					var hasToolUse bool
					var hasToolResult bool

					for _, block := range contentArr {
						if blockMap, ok := block.(map[string]interface{}); ok {
							blockType, _ := blockMap["type"].(string)
							if blockType == "tool_use" {
								hasToolUse = true
							} else if blockType == "tool_result" {
								hasToolResult = true
							}
						}
					}

					if hasToolResult {
						for _, block := range contentArr {
							if blockMap, ok := block.(map[string]interface{}); ok {
								blockType, _ := blockMap["type"].(string)
								if blockType == "tool_result" {
									toolUseID, _ := blockMap["tool_use_id"].(string)
									resultContent := extractTextFromContent(blockMap["content"])
									messages = append(messages, OpenAIMessage{
										Role:       "tool",
										ToolCallID: toolUseID,
										Content:    resultContent,
									})
								}
							}
						}
					} else if hasToolUse {
						var toolCalls []OpenAIToolCall
						for _, block := range contentArr {
							if blockMap, ok := block.(map[string]interface{}); ok {
								blockType, _ := blockMap["type"].(string)
								if blockType == "tool_use" {
									id, _ := blockMap["id"].(string)
									name, _ := blockMap["name"].(string)
									input, _ := json.Marshal(blockMap["input"])
									toolCalls = append(toolCalls, OpenAIToolCall{
										ID:   id,
										Type: "function",
										Function: OpenAIFunction{
											Name:      name,
											Arguments: string(input),
										},
									})
								}
							}
						}
						messages = append(messages, OpenAIMessage{
							Role:      "assistant",
							Content:   textContent,
							ToolCalls: toolCalls,
						})
					} else if textContent != "" {
						messages = append(messages, OpenAIMessage{
							Role:    role,
							Content: textContent,
						})
					}
				} else if textContent != "" {
					messages = append(messages, OpenAIMessage{
						Role:    role,
						Content: textContent,
					})
				}
			}
		}
	}

	req := &OpenAIChatRequest{
		Model:       model,
		Messages:    messages,
		MaxTokens:   maxTokens,
		Temperature: temperature,
		Stream:      false,
	}

	if rawTools, ok := raw["tools"].([]interface{}); ok && len(rawTools) > 0 {
		var tools []OpenAITool
		for _, t := range rawTools {
			if toolMap, ok := t.(map[string]interface{}); ok {
				name, _ := toolMap["name"].(string)
				desc, _ := toolMap["description"].(string)
				inputSchema, _ := toolMap["input_schema"].(map[string]interface{})
				tools = append(tools, OpenAITool{
					Type: "function",
					Function: OpenAIToolFunction{
						Name:        name,
						Description: desc,
						Parameters:  inputSchema,
					},
				})
			}
		}
		req.Tools = tools

		if toolChoice, ok := raw["tool_choice"]; ok {
			req.ToolChoice = toolChoice
		}
	}

	return req, nil
}

func convertOpenAIToAnthropicResponse(openAIResp OpenAIChatResponse, model string) map[string]interface{} {
	var content []map[string]interface{}
	var toolUse []map[string]interface{}

	if len(openAIResp.Choices) > 0 {
		choice := openAIResp.Choices[0]

		if textContent, ok := choice.Message.Content.(string); ok && textContent != "" {
			content = append(content, map[string]interface{}{
				"type": "text",
				"text": textContent,
			})
		}

		if len(choice.Message.ToolCalls) > 0 {
			for _, tc := range choice.Message.ToolCalls {
				var inputObj interface{}
				if tc.Function.Arguments != "" {
					if err := json.Unmarshal([]byte(tc.Function.Arguments), &inputObj); err != nil {
						inputObj = tc.Function.Arguments
					}
				}
				toolUse = append(toolUse, map[string]interface{}{
					"type":  "tool_use",
					"id":    tc.ID,
					"name":  tc.Function.Name,
					"input": inputObj,
				})
			}
		}

		if len(toolUse) > 0 {
			content = append(content, toolUse...)
		}
	}

	if content == nil {
		content = []map[string]interface{}{}
	}

	stopReason := "end_turn"
	if len(openAIResp.Choices) > 0 {
		switch openAIResp.Choices[0].FinishReason {
		case "stop":
			stopReason = "end_turn"
		case "length":
			stopReason = "max_tokens"
		case "tool_calls":
			stopReason = "tool_use"
		}
	}

	return map[string]interface{}{
		"id":            fmt.Sprintf("msg_%d", time.Now().Unix()),
		"type":          "message",
		"role":          "assistant",
		"content":       content,
		"model":         model,
		"stop_reason":   stopReason,
		"stop_sequence": nil,
		"usage": map[string]interface{}{
			"input_tokens":  openAIResp.Usage.PromptTokens,
			"output_tokens": openAIResp.Usage.CompletionTokens,
		},
	}
}

var httpClient = &http.Client{
	Timeout: 120 * time.Second,
}

func llamaRequest(path string, method string, data interface{}) (int, []byte, error) {
	url := LLamaBaseURL + path

	var body io.Reader
	if data != nil {
		jsonData, err := json.Marshal(data)
		if err != nil {
			return 0, nil, err
		}
		body = bytes.NewReader(jsonData)
		log.Printf("Forwarding to llama.cpp: %s %s", method, url)
		log.Printf("Request body: %s", string(jsonData))
	}

	req, err := http.NewRequest(method, url, body)
	if err != nil {
		return 0, nil, err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := httpClient.Do(req)
	if err != nil {
		return 0, nil, err
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err == nil {
		log.Printf("llama.cpp response status: %d", resp.StatusCode)
		if resp.StatusCode != 200 {
			log.Printf("llama.cpp error response: %s", string(respBody))
		}
	}
	return resp.StatusCode, respBody, err
}

func sendJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	status, data, err := llamaRequest("/health", "GET", nil)
	if err != nil || status != 200 {
		sendJSON(w, 503, map[string]interface{}{
			"status":         "degraded",
			"llama_backend":  "unavailable",
		})
		return
	}

	var llamaHealth interface{}
	json.Unmarshal(data, &llamaHealth)

	sendJSON(w, 200, map[string]interface{}{
		"status":        "ok",
		"llama_backend": llamaHealth,
	})
}

func handleMetrics(w http.ResponseWriter, r *http.Request) {
	updateMetricsFromJSONL()

	metricsMutex.RLock()
	data := metricsCache
	metricsMutex.RUnlock()

	if len(data) == 0 {
		// Return empty metrics if cache is not ready
		w.Header().Set("Content-Type", "text/plain; version=0.0.4")
		w.WriteHeader(200)
		w.Write([]byte("# No metrics available yet\n"))
		return
	}

	w.Header().Set("Content-Type", "text/plain; version=0.0.4")
	w.WriteHeader(200)
	w.Write(data)
}

func handleListModels(w http.ResponseWriter, r *http.Request) {
	models := ModelListResponse{
		Object: "list",
		Data: []ModelInfo{
			{
				ID:      "claude-3-5-sonnet-20241022",
				Object:  "model",
				Created: 1699000000,
				OwnedBy: "anthropic",
			},
			{
				ID:      "claude-3-opus-20240229",
				Object:  "model",
				Created: 1699000000,
				OwnedBy: "anthropic",
			},
			{
				ID:      "claude-3-haiku-20240307",
				Object:  "model",
				Created: 1699000000,
				OwnedBy: "anthropic",
			},
			{
				ID:      DefaultModel,
				Object:  "model",
				Created: 1699000000,
				OwnedBy: "qwen",
			},
		},
	}
	sendJSON(w, 200, models)
}

func handleMessages(w http.ResponseWriter, r *http.Request) {
	requestID := fmt.Sprintf("req_%d", time.Now().UnixNano())

	body, err := io.ReadAll(r.Body)
	if err != nil {
		log.Printf("Error reading request body: %v", err)
		sendJSON(w, 400, map[string]interface{}{"error": map[string]string{"message": "Failed to read request body"}})
		return
	}

	log.Printf("Received request (len=%d): %s", len(body), string(body))

	var pretty map[string]interface{}
	if json.Unmarshal(body, &pretty) == nil {
		if prettyMsgs, ok := pretty["messages"].([]interface{}); ok {
			log.Printf("Number of messages: %d", len(prettyMsgs))
			for i, m := range prettyMsgs {
				if msgMap, ok := m.(map[string]interface{}); ok {
					role, _ := msgMap["role"].(string)
					content := msgMap["content"]
					if contentArr, ok := content.([]interface{}); ok {
						log.Printf("  Message %d: role=%s, %d content blocks", i, role, len(contentArr))
					} else {
						contentStr := fmt.Sprintf("%v", content)
						log.Printf("  Message %d: role=%s, content len=%d", i, role, len(contentStr))
					}
				}
			}
		}
	}

	logJSONL(map[string]interface{}{
		"type":      "request",
		"request_id": requestID,
		"request":    json.RawMessage(body),
	})

	openAIReq, err := convertAnthropicRequestToOpenAI(body)
	if err != nil {
		log.Printf("Error converting request: %v", err)
		logJSONL(map[string]interface{}{
			"type":      "error",
			"request_id": requestID,
			"error":      err.Error(),
		})
		sendJSON(w, 400, map[string]interface{}{"error": map[string]string{"message": "Invalid request: " + err.Error()}})
		return
	}

	status, respBody, err := llamaRequest("/v1/chat/completions", "POST", openAIReq)
	if err != nil {
		log.Printf("Error forwarding to llama.cpp: %v", err)
		logJSONL(map[string]interface{}{
			"type":      "error",
			"request_id": requestID,
			"error":      err.Error(),
		})
		sendJSON(w, 500, map[string]interface{}{"error": map[string]string{"message": err.Error()}})
		return
	}

	if status != 200 {
		logJSONL(map[string]interface{}{
			"type":              "response",
			"request_id":         requestID,
			"llama_status":      status,
			"llama_response":    json.RawMessage(respBody),
		})
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(status)
		w.Write(respBody)
		return
	}

	var openAIResp OpenAIChatResponse
	if err := json.Unmarshal(respBody, &openAIResp); err != nil {
		log.Printf("Error parsing llama.cpp response: %v", err)
		logJSONL(map[string]interface{}{
			"type":      "error",
			"request_id": requestID,
			"error":      err.Error(),
		})
		sendJSON(w, 500, map[string]interface{}{"error": map[string]string{"message": err.Error()}})
		return
	}

	anthropicResp := convertOpenAIToAnthropicResponse(openAIResp, openAIReq.Model)
	respJSON, _ := json.Marshal(anthropicResp)
	log.Printf("Response: %s", string(respJSON))

	logJSONL(map[string]interface{}{
		"type":              "response",
		"request_id":         requestID,
		"llama_status":      status,
		"llama_response":    json.RawMessage(respBody),
		"anthropic_response": json.RawMessage(respJSON),
	})

	sendJSON(w, 200, anthropicResp)
}

type loggingResponseWriter struct {
	http.ResponseWriter
	statusCode int
}

func (lrw *loggingResponseWriter) WriteHeader(code int) {
	lrw.statusCode = code
	lrw.ResponseWriter.WriteHeader(code)
}

func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		lrw := &loggingResponseWriter{w, 200}

		next.ServeHTTP(lrw, r)

		duration := time.Since(start)
		log.Printf("[%s] %s %s %d %s",
			time.Now().Format("02/Jan/2006:15:04:05 -0700"),
			r.Method,
			r.URL.Path,
			lrw.statusCode,
			duration,
		)
	})
}

func printBanner() {
	fmt.Println("============================================================")
	fmt.Println("Anthropic Claude API -> llama.cpp OpenAI API Proxy")
	fmt.Println("  (with Tool/Function Calling support!)")
	fmt.Println("  (JSONL request/response logging enabled!)")
	fmt.Println("  (Prometheus metrics enabled!)")
	fmt.Println("============================================================")
	fmt.Printf("Proxy Port:     %d\n", ListenPort)
	fmt.Printf("llama.cpp Backend: %s\n", LLamaBaseURL)
	fmt.Printf("Default Model:  %s\n", DefaultModel)
	fmt.Printf("JSONL Log:     %s\n", JSONL_LOG_PATH)
	fmt.Println()
	fmt.Println("Endpoints:")
	fmt.Printf("  - POST http://localhost:%d/v1/messages  (Anthropic Claude API)\n", ListenPort)
	fmt.Printf("  - GET  http://localhost:%d/v1/models    (List models)\n", ListenPort)
	fmt.Printf("  - GET  http://localhost:%d/health        (Health check)\n", ListenPort)
	fmt.Printf("  - GET  http://localhost:%d/metrics       (Prometheus metrics)\n", ListenPort)
	fmt.Println()
	fmt.Println("Features:")
	fmt.Println("  - Basic message conversation")
	fmt.Println("  - System prompt support (string or array)")
	fmt.Println("  - Multi-turn dialogue")
	fmt.Println("  - Tool/Function Calling")
	fmt.Println("  - JSONL request/response logging")
	fmt.Println("  - Prometheus metrics endpoint")
	fmt.Println()
	fmt.Println("Press Ctrl+C to stop")
	fmt.Println("============================================================")
	fmt.Println()
}

func main() {
	if err := initJSONLLogger(); err != nil {
		log.Printf("Warning: Failed to initialize JSONL logger: %v", err)
	} else {
		log.Printf("JSONL logger initialized: %s", JSONL_LOG_PATH)
	}

	printBanner()

	mux := http.NewServeMux()
	mux.HandleFunc("/health", handleHealth)
	mux.HandleFunc("/metrics", handleMetrics)
	mux.HandleFunc("/v1/models", handleListModels)
	mux.HandleFunc("/v1/messages", handleMessages)

	loggedMux := loggingMiddleware(mux)

	// Start log rotation checker goroutine (every 5 minutes)
	go func() {
		for {
			time.Sleep(5 * time.Minute)
			rotateJSONLLog()
		}
	}()

	server := &http.Server{
		Addr:    fmt.Sprintf("0.0.0.0:%d", ListenPort),
			Handler: loggedMux,
	}

	log.Printf("Starting server on :%d", ListenPort)
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Server error: %v", err)
	}
}
