#pragma once

/**
 * Process Manager for RyzenAI-Server
 */

#include <string>
#include <vector>
#include <cstdint>

namespace ryzenai {

/**
 * Process handle
 */
struct ProcessHandle {
    pid_t pid = 0;
    bool running = false;
};

/**
 * Process manager
 *
 * Manages ryzenai-server subprocess lifecycle
 */
class ProcessManager {
public:
    /**
     * Start a process
     * @param executable Executable path
     * @param args Command line arguments (excluding executable)
     * @param capture_output Capture stdout/stderr
     * @return Process handle
     */
    static ProcessHandle start_process(
        const std::string& executable,
        const std::vector<std::string>& args,
        bool capture_output = false
    );

    /**
     * Check if process is running
     * @param handle Process handle
     * @return true if process is running
     */
    static bool is_running(const ProcessHandle& handle);

    /**
     * Stop a process gracefully (SIGTERM then SIGKILL)
     * @param handle Process handle (modified)
     */
    static void stop_process(ProcessHandle& handle);

    /**
     * Get process exit code
     * @param handle Process handle
     * @return Exit code, or -1 if still running
     */
    static int get_exit_code(const ProcessHandle& handle);
};

} // namespace ryzenai
