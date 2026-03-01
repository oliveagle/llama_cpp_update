# RyzenAI Backend for llama.cpp
# AMD NPU support via RyzenAI-Server

find_package(CURL REQUIRED)

# Find libzip for ZIP extraction
find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBZIP REQUIRED libzip)

add_library(ryzenai-backend STATIC
    ryzenai_backend.cpp
    process_manager.cpp
    http_client.cpp
    downloader.cpp
)

target_include_directories(ryzenai-backend PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CURL_INCLUDE_DIRS}
    ${LIBZIP_INCLUDE_DIRS}
)

target_link_libraries(ryzenai-backend PRIVATE
    ${CURL_LIBRARIES}
    ${LIBZIP_LIBRARIES}
    llama-common
)

target_compile_features(ryzenai-backend PRIVATE cxx_std_17)

# Install target
install(TARGETS ryzenai-backend
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)
