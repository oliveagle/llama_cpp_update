#pragma once

/**
 * HTTP Client for RyzenAI-Server communication
 */

#include <string>

namespace ryzenai {

/**
 * HTTP client
 *
 * Simple curl-based HTTP client for communicating with ryzenai-server
 */
class HTTPClient {
public:
    /**
     * Send POST request
     * @param url URL
     * @param body Request body JSON
     * @param timeout_ms Timeout in milliseconds
     * @return Response body
     * @throws std::runtime_error on failure
     */
    static std::string post(const std::string& url,
                           const std::string& body,
                           int timeout_ms = 60000);

    /**
     * Send GET request
     * @param url URL
     * @param timeout_ms Timeout in milliseconds
     * @return Response body
     * @throws std::runtime_error on failure
     */
    static std::string get(const std::string& url,
                          int timeout_ms = 5000);

    /**
     * Check if endpoint is reachable
     * @param url URL
     * @param timeout_ms Timeout in milliseconds
     * @return true if reachable
     */
    static bool is_reachable(const std::string& url,
                            int timeout_ms = 1000);

private:
    /**
     * Internal request method
     */
    static std::string request(const std::string& method,
                              const std::string& url,
                              const std::string& body,
                              int timeout_ms);
};

} // namespace ryzenai
