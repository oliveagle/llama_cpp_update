#include "downloader.h"
#include "process_manager.h"

#include <iostream>
#include <fstream>
#include <filesystem>
#include <curl/curl.h>
#include <zip.h>
#include <unistd.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

namespace ryzenai {

/**
 * Progress data for curl callback
 */
struct ProgressData {
    int64_t last_update = 0;
    ProgressCallback callback;
};

/**
 * Progress callback for curl (throttled)
 */
static int progress_callback(void* clientp, curl_off_t dltotal, curl_off_t dlnow,
                             curl_off_t ultotal, curl_off_t ulnow) {
    ProgressData* data = static_cast<ProgressData*>(clientp);

    if (data && data->callback && dltotal > 0) {
        // Throttle updates to once per 1MB
        if (dlnow - data->last_update >= 1024 * 1024) {
            data->callback(dlnow, dltotal);
            data->last_update = dlnow;
        }
    }
    (void)ultotal; (void)ulnow;  // Unused
    return 0;
}

std::string Downloader::get_download_url(const std::string& version) {
    const std::string repo = "lemonade-sdk/ryzenai-server";
    const std::string filename = "ryzenai-server.zip";
    return "https://github.com/" + repo + "/releases/download/" + version + "/" + filename;
}

std::string Downloader::get_install_directory() {
    // Get home directory
    const char* home = std::getenv("HOME");
    if (!home) {
        home = std::getenv("USERPROFILE");
    }
    if (!home) {
        throw std::runtime_error("HOME environment variable not set");
    }

    fs::path install_dir = fs::path(home) / ".cache" / "llama.cpp" / "ryzenai-server";
    fs::create_directories(install_dir);

    return install_dir.string();
}

bool Downloader::download_and_install(const std::string& version,
                                      const std::string& install_dir,
                                      ProgressCallback progress) {
    std::cout << "[RyzenAI] Downloading ryzenai-server " << version << "..." << std::endl;

    std::string url = get_download_url(version);
    std::string zip_path = (fs::path(install_dir) / "ryzenai-server.zip").string();

    std::cout << "[RyzenAI] URL: " << url << std::endl;
    std::cout << "[RyzenAI] Installing to: " << install_dir << std::endl;

    // Download ZIP file
    if (!download_file(url, zip_path, progress)) {
        std::cerr << "[RyzenAI] Download failed" << std::endl;
        return false;
    }

    std::cout << "[RyzenAI] Download complete!" << std::endl;

    // Verify file exists and is reasonable size
    if (!fs::exists(zip_path)) {
        std::cerr << "[RyzenAI] Downloaded file does not exist" << std::endl;
        return false;
    }

    std::uintmax_t file_size = fs::file_size(zip_path);
    std::cout << "[RyzenAI] Downloaded size: " << (file_size / 1024 / 1024) << " MB" << std::endl;

    if (file_size < 1024 * 1024) {  // Less than 1MB
        std::cerr << "[RyzenAI] Downloaded file too small, may be corrupted" << std::endl;
        fs::remove(zip_path);
        return false;
    }

    // Extract ZIP
    std::cout << "[RyzenAI] Extracting..." << std::endl;
    if (!extract_zip(zip_path, install_dir)) {
        std::cerr << "[RyzenAI] Extraction failed" << std::endl;
        fs::remove(zip_path);
        return false;
    }

    // Verify extraction
    fs::path exe_path = fs::path(install_dir) / "ryzenai-server";
    if (!fs::exists(exe_path)) {
        std::cerr << "[RyzenAI] Executable not found after extraction" << std::endl;
        return false;
    }

    // Make executable on Linux
    chmod(exe_path.c_str(), 0755);

    // Save version info
    std::string version_file = (fs::path(install_dir) / "version.txt").string();
    std::ofstream vf(version_file);
    vf << version;
    vf.close();

    // Clean up ZIP
    fs::remove(zip_path);

    std::cout << "[RyzenAI] Installation complete!" << std::endl;
    return true;
}

bool Downloader::download_file(const std::string& url,
                               const std::string& dest,
                               ProgressCallback progress) {
    CURL* curl = curl_easy_init();
    if (!curl) {
        std::cerr << "[RyzenAI] curl_easy_init failed" << std::endl;
        return false;
    }

    std::ofstream file(dest, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "[RyzenAI] Failed to open file for writing: " << dest << std::endl;
        curl_easy_cleanup(curl);
        return false;
    }

    // Write callback
    auto write_callback = [](void* ptr, size_t size, size_t nmemb, void* userdata) -> size_t {
        std::ofstream* file = static_cast<std::ofstream*>(userdata);
        file->write(static_cast<char*>(ptr), size * nmemb);
        return size * nmemb;
    };

    // Progress callback wrapper
    ProgressData progress_data;
    progress_data.callback = progress;
    progress_data.last_update = 0;

    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl, CURLOPT_NOPROGRESS, 0L);
    curl_easy_setopt(curl, CURLOPT_XFERINFOFUNCTION, progress_callback);
    curl_easy_setopt(curl, CURLOPT_XFERINFODATA, &progress_data);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &file);

    CURLcode res = curl_easy_perform(curl);

    file.close();

    if (res != CURLE_OK) {
        std::cerr << "[RyzenAI] Download failed: " << curl_easy_strerror(res) << std::endl;
        fs::remove(dest);
        curl_easy_cleanup(curl);
        return false;
    }

    curl_easy_cleanup(curl);
    return true;
}

bool Downloader::extract_zip(const std::string& zip_path,
                             const std::string& dest_dir) {
    int err = 0;
    struct zip* archive = zip_open(zip_path.c_str(), ZIP_RDONLY, &err);

    if (!archive) {
        std::cerr << "[RyzenAI] Failed to open ZIP archive" << std::endl;
        return false;
    }

    int num_entries = zip_get_num_entries(archive, 0);
    std::cout << "[RyzenAI] Extracting " << num_entries << " entries..." << std::endl;

    for (int i = 0; i < num_entries; ++i) {
        struct zip_stat stat;
        if (zip_stat_index(archive, i, 0, &stat) != 0) {
            continue;
        }

        std::string entry_name = stat.name;

        // Skip directories
        if (entry_name.back() == '/') {
            continue;
        }

        // Extract file
        fs::path dest_path = fs::path(dest_dir) / entry_name;
        fs::create_directories(dest_path.parent_path());

        struct zip_file* file = zip_fopen_index(archive, i, 0);
        if (!file) {
            std::cerr << "[RyzenAI] Failed to open entry: " << entry_name << std::endl;
            continue;
        }

        std::ofstream out(dest_path, std::ios::binary);
        if (!out.is_open()) {
            std::cerr << "[RyzenAI] Failed to create file: " << dest_path.string() << std::endl;
            zip_fclose(file);
            continue;
        }

        char buffer[8192];
        zip_int64_t bytes_read;
        while ((bytes_read = zip_fread(file, buffer, sizeof(buffer))) > 0) {
            out.write(buffer, bytes_read);
        }

        out.close();
        zip_fclose(file);
    }

    zip_close(archive);
    return true;
}

} // namespace ryzenai
