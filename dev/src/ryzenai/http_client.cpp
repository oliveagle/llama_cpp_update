#include "http_client.h"

#include <curl/curl.h>
#include <stdexcept>
#include <iostream>

namespace ryzenai {

/**
 * Write callback for curl
 */
static size_t write_callback(void* ptr, size_t size, size_t nmemb, void* userdata) {
    std::string* response = static_cast<std::string*>(userdata);
    response->append(static_cast<char*>(ptr), size * nmemb);
    return size * nmemb;
}

std::string HTTPClient::request(const std::string& method,
                                const std::string& url,
                                const std::string& body,
                                int timeout_ms) {
    CURL* curl = curl_easy_init();
    if (!curl) {
        throw std::runtime_error("curl_easy_init failed");
    }

    std::string response;
    struct curl_slist* headers = nullptr;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    headers = curl_slist_append(headers, "Accept: application/json");

    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, timeout_ms);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

    // Follow redirects
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);

    if (method == "POST") {
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, body.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, body.size());
    } else if (method == "GET") {
        curl_easy_setopt(curl, CURLOPT_HTTPGET, 1L);
    }

    CURLcode res = curl_easy_perform(curl);

    // Check for errors
    if (res != CURLE_OK) {
        std::string error = "HTTP request failed: ";
        error += curl_easy_strerror(res);

        // Get HTTP response code if available
        long response_code = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);
        if (response_code > 0) {
            error += " (HTTP " + std::to_string(response_code) + ")";
        }

        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
        throw std::runtime_error(error);
    }

    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);

    return response;
}

std::string HTTPClient::post(const std::string& url,
                            const std::string& body,
                            int timeout_ms) {
    return request("POST", url, body, timeout_ms);
}

std::string HTTPClient::get(const std::string& url,
                           int timeout_ms) {
    return request("GET", url, "", timeout_ms);
}

bool HTTPClient::is_reachable(const std::string& url, int timeout_ms) {
    try {
        get(url, timeout_ms);
        return true;
    } catch (const std::exception& e) {
        return false;
    }
}

} // namespace ryzenai
