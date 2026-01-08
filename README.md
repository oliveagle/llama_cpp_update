# llama.cpp 管理脚本集

自动化管理和部署 llama.cpp 服务的脚本工具集。

## 目录结构

```
llama_cpp/
├── scripts/           # 脚本文件
│   ├── vl.sh         # 视觉语言模型服务启动脚本
│   ├── llama_cpp_server.sh
│   ├── llama_cpp_full.sh
│   └── llama_cpp_light.sh
├── presets/          # 模型配置文件
│   └── mypresets.ini # 模型预设配置
├── downloads/        # 下载的版本
├── current/          # 当前版本符号链接
├── auto_switch.sh    # 自动切换模型服务
├── bench.sh          # 性能测试脚本
├── check_invalid_models.sh  # 检查和更新模型配置
└── update_llama_cpp.sh       # 自动更新 llama.cpp
```

## 脚本说明

### check_invalid_models.sh
扫描指定目录下的所有 GGUF 模型文件，检查配置文件中的模型是否有效，并可选择性生成新的配置文件。

**用法：**
```bash
./check_invalid_models.sh
```

**功能：**
- 扫描 `/mnt/volume3/hf_models` 和 `/mnt/volume3/modelscope_models` 目录
- 检查 `presets/mypresets.ini` 中的模型是否存在
- 自动生成新的配置文件（包含所有扫描到的模型）
- 备份旧配置文件（保留最近 5 个）

### update_llama_cpp.sh
自动下载并更新 llama.cpp 到指定版本或最新版本。

**用法：**
```bash
./update_llama_cpp.sh           # 更新到最新版本
./update_llama_cpp.sh 7600      # 更新到指定版本 b7600
./update_llama_cpp.sh b7600     # 更新到指定版本 b7600（带 b 前缀）
./update_llama_cpp.sh list      # 列出所有可用版本
```

**功能：**
- 支持指定版本号或更新到最新版本
- 自动下载并解压到 `downloads` 目录
- 更新 `current` 符号链接
- 可选清理旧版本（保留最近 5 个）
- 通过 HTTP 代理下载

### auto_switch.sh
启动 llama.cpp 服务，使用 `presets/mypresets.ini` 配置文件。

**用法：**
```bash
./auto_switch.sh
```

### bench.sh
运行 llama.cpp 性能测试。

**用法：**
```bash
./bench.sh
```

### scripts/vl.sh
启动支持视觉语言的 llama.cpp 服务。

**用法：**
```bash
./scripts/vl.sh
```

## 配置文件

### presets/mypresets.ini
模型预设配置文件，使用 INI 格式：

```ini
[model_name]
m = /path/to/model.gguf
temp = 0.7
top-p = 0.8
top-k = 20
min-p = 0
ctx-size = 102400
```

## 环境变量

- `MODEL_PATH`: 模型文件路径（docker 脚本使用）
- `PROXY`: HTTP 代理地址（默认: http://127.0.0.1:1080）

## Docker 脚本

- **llama_cpp_server.sh**: 启动完整的 llama.cpp 服务（docker）
- **llama_cpp_full.sh**: 完整版本 docker 容器
- **llama_cpp_light.sh**: 轻量版本 docker 容器

## 注意事项

1. 所有脚本都使用 `_SROOT` 变量来定位脚本根目录，确保可从任何位置运行
2. 配置文件和备份文件统一存放在 `presets/` 目录
3. `current` 是指向当前使用的 llama.cpp 版本的符号链接
4. 脚本会自动创建 `presets` 目录（如果不存在）

## 许可证

详见 [LICENSE](LICENSE) 文件。
