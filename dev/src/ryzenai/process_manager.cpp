#include "process_manager.h"

#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <signal.h>
#include <fcntl.h>
#include <cstring>
#include <iostream>

namespace ryzenai {

ProcessHandle ProcessManager::start_process(
    const std::string& executable,
    const std::vector<std::string>& args,
    bool capture_output) {

    ProcessHandle handle;
    handle.pid = 0;
    handle.running = false;

    // Create pipe for output capture if needed
    int pipefd[2];
    if (capture_output && pipe(pipefd) == -1) {
        std::cerr << "[RyzenAI] Failed to create pipe: " << strerror(errno) << std::endl;
        return handle;
    }

    pid_t pid = fork();
    if (pid == -1) {
        std::cerr << "[RyzenAI] Fork failed: " << strerror(errno) << std::endl;
        if (capture_output) {
            close(pipefd[0]);
            close(pipefd[1]);
        }
        return handle;
    }

    if (pid == 0) {
        // Child process
        if (capture_output) {
            close(pipefd[0]);  // Close read end
            dup2(pipefd[1], STDOUT_FILENO);
            dup2(pipefd[1], STDERR_FILENO);
            close(pipefd[1]);
        }

        // Build argv
        std::vector<char*> argv;
        argv.push_back(const_cast<char*>(executable.c_str()));
        for (auto& arg : args) {
            argv.push_back(const_cast<char*>(arg.c_str()));
        }
        argv.push_back(nullptr);

        // Execute
        execv(executable.c_str(), argv.data());

        // If execv returns, it failed
        std::cerr << "[RyzenAI] execv failed: " << strerror(errno) << std::endl;
        _exit(127);
    }

    // Parent process
    if (capture_output) {
        close(pipefd[1]);  // Close write end
    }

    handle.pid = pid;
    handle.running = true;

    std::cout << "[RyzenAI] Process started with PID: " << pid << std::endl;
    return handle;
}

bool ProcessManager::is_running(const ProcessHandle& handle) {
    if (handle.pid <= 0) {
        return false;
    }

    int status;
    pid_t result = waitpid(handle.pid, &status, WNOHANG);

    if (result == -1) {
        // Error occurred
        return false;
    }
    if (result == 0) {
        // Still running (child hasn't exited)
        return true;
    }
    // Child has exited
    if (WIFEXITED(status)) {
        std::cout << "[RyzenAI] Process exited with code: " << WEXITSTATUS(status) << std::endl;
    } else if (WIFSIGNALED(status)) {
        std::cout << "[RyzenAI] Process killed by signal: " << WTERMSIG(status) << std::endl;
    }
    return false;
}

void ProcessManager::stop_process(ProcessHandle& handle) {
    if (handle.pid <= 0 || !handle.running) {
        return;
    }

    std::cout << "[RyzenAI] Stopping process (PID: " << handle.pid << ")" << std::endl;

    // Send SIGTERM for graceful shutdown
    kill(handle.pid, SIGTERM);

    // Wait up to 5 seconds for process to exit
    const int max_wait = 50;  // 50 * 100ms = 5s
    for (int i = 0; i < max_wait; ++i) {
        if (!is_running(handle)) {
            handle.running = false;
            return;
        }
        usleep(100000);  // 100ms
    }

    // Process still running, send SIGKILL
    std::cout << "[RyzenAI] Process did not exit gracefully, sending SIGKILL" << std::endl;
    kill(handle.pid, SIGKILL);

    // Wait for process to be reaped
    waitpid(handle.pid, nullptr, 0);

    handle.running = false;
    handle.pid = 0;
}

int ProcessManager::get_exit_code(const ProcessHandle& handle) {
    if (handle.pid <= 0) {
        return -1;
    }

    int status;
    pid_t result = waitpid(handle.pid, &status, WNOHANG);

    if (result > 0 && WIFEXITED(status)) {
        return WEXITSTATUS(status);
    }
    return -1;  // Still running or error
}

} // namespace ryzenai
