#pragma once

/**
 * Downloader for RyzenAI-Server
 */

#include <string>
#include <functional>

namespace ryzenai {

/**
 * Download progress callback
 * @param downloaded_bytes Bytes downloaded so far
 * @param total_bytes Total bytes to download
 */
using ProgressCallback = std::function<void(int64_t, int64_t)>;

/**
 * Downloader
 *
 * Downloads ryzenai-server from GitHub releases
 */
class Downloader {
public:
    /**
     * Download ryzenai-server
     * @param version Version to download (e.g., "v1.7.0")
     * @param install_dir Installation directory
     * @param progress Progress callback (optional)
     * @return true if download and extraction succeeded
     */
    static bool download_and_install(const std::string& version,
                                     const std::string& install_dir,
                                     ProgressCallback progress = nullptr);

    /**
     * Get download URL for a specific version
     */
    static std::string get_download_url(const std::string& version);

    /**
     * Get install directory
     */
    static std::string get_install_directory();

private:
    /**
     * Download file from URL
     */
    static bool download_file(const std::string& url,
                             const std::string& dest,
                             ProgressCallback progress);

    /**
     * Extract ZIP archive
     */
    static bool extract_zip(const std::string& zip_path,
                           const std::string& dest_dir);
};

} // namespace ryzenai
