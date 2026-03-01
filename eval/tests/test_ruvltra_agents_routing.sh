#!/bin/bash
# RuvLTRA Agent 路由测试脚本 - 使用 llama.cpp API
# 为 ole-teams 中的 28 个 Agent 角色各生成 20 个测试任务并测试路由

# 移除 set -e 以便脚本在遇到错误时继续执行

# 服务器地址
SERVER="${1:-http://localhost:8402}"
OUTPUT_DIR="/mnt/volume3/llama_cpp/tests/agent_routing_test_results"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
mkdir -p "$OUTPUT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Agent 角色列表
AGENTS=(
    "architect"
    "backend-dev"
    "frontend-dev"
    "fullstack-dev"
    "mobile-dev"
    "devops-engineer"
    "sre"
    "dba"
    "data-engineer"
    "ml-engineer"
    "test-engineer"
    "ui-test-engineer"
    "code-reviewer"
    "security-reviewer"
    "performance-expert"
    "product-manager"
    "scrum-master"
    "tech-lead"
    "technical-writer"
    "researcher"
    "ux-designer"
    "prompt-engineer"
    "quant-researcher"
    "crypto-trader"
    "financial-analyst"
    "market-monitor"
    "skeptic"
)

# 生成测试任务
generate_tasks() {
    local agent=$1
    local output_file="$OUTPUT_DIR/${agent}_tasks.jsonl"
    > "$output_file"

    case $agent in
        "architect") tasks=(
            "设计一个支持百万用户的微服务架构" "评估使用 PostgreSQL 还是 MongoDB" "规划系统的水平扩展策略"
            "设计事件驱动的架构模式" "选择合适的消息队列：Kafka vs RabbitMQ" "设计多租户 SaaS 架构"
            "评估使用 monorepo 还是多仓库" "设计 CQRS 模式的数据流" "选择适合高并发的缓存策略"
            "设计服务网格架构" "评估 Serverless 架构的适用场景" "设计领域驱动驱动的架构"
            "规划技术债务的偿还策略" "设计 API 网关的架构" "选择合适的服务发现方案"
            "设计容错和降级机制" "评估使用 gRPC 还是 REST" "设计数据一致性保障方案"
            "规划多云部署架构" "设计可观测性架构"
        ) ;;
        "backend-dev") tasks=(
            "实现用户认证和授权 API" "设计 RESTful API 接口" "实现数据库事务处理"
            "编写数据验证逻辑" "实现文件上传功能" "设计数据库 Schema"
            "实现 WebSocket 实时通信" "编写批量数据处理脚本" "实现定时任务调度"
            "设计数据库索引优化查询" "实现 OAuth2 第三方登录" "编写数据迁移脚本"
            "实现邮件发送服务" "设计分页和过滤 API" "实现分布式锁机制"
            "编写数据聚合查询" "实现 API 限流功能" "设计软删除功能"
            "实现审计日志记录" "编写数据库存储过程"
        ) ;;
        "frontend-dev") tasks=(
            "实现响应式导航组件" "优化页面加载性能" "实现暗色模式切换"
            "设计可复用的 UI 组件库" "实现表单验证逻辑" "优化首屏渲染时间"
            "实现无限滚动列表" "设计状态管理方案" "实现拖拽上传功能"
            "优化 bundle 体积" "实现国际化支持" "设计无障碍访问功能"
            "实现实时搜索功能" "优化列表渲染性能" "实现图片懒加载"
            "设计错误边界处理" "实现 PWA 离线功能" "优化动画性能"
            "实现富文本编辑器" "设计组件文档系统"
        ) ;;
        "fullstack-dev") tasks=(
            "实现完整的用户管理系统" "开发博客平台前后端" "实现实时聊天应用"
            "开发任务管理工具" "实现文件共享平台" "开发数据分析看板"
            "实现电商平台购物车" "开发社交网络功能" "实现在线支付流程"
            "开发内容管理系统" "实现用户反馈系统" "开发 API 文档平台"
            "实现代码评审工具" "开发项目管理应用" "实现在线考试系统"
            "开发预约预订系统" "实现通知推送服务" "开发用户仪表盘"
            "实现数据导入导出" "开发协作编辑功能"
        ) ;;
        "mobile-dev") tasks=(
            "实现 React Native 导航" "开发跨平台登录界面" "实现移动端手势识别"
            "开发离线数据同步" "实现推送通知功能" "设计移动端动画"
            "实现相机拍照功能" "开发位置服务功能" "实现生物识别登录"
            "优化移动端性能" "实现深色模式支持" "开发多语言支持"
            "实现本地数据存储" "优化 App 启动速度" "实现图片缓存策略"
            "开发分享功能" "实现内购支付" "优化包体积大小"
            "实现错误上报" "开发应用更新检查"
        ) ;;
        "devops-engineer") tasks=(
            "配置 CI/CD 流水线" "编写 Docker 多阶段构建" "设计 Kubernetes 部署配置"
            "实现自动回滚机制" "配置监控告警系统" "编写 Terraform 基础设施"
            "设计服务网格配置" "实现蓝绿部署策略" "配置日志收集系统"
            "编写 Ansible 部署脚本" "设计容器镜像仓库" "实现自动化测试流程"
            "配置负载均衡器" "编写 Helm Chart 配置" "设计 GitOps 流程"
            "实现密钥管理系统" "配置网络策略" "编写备份恢复脚本"
            "设计灾备方案" "实现资源配额管理"
        ) ;;
        "sre") tasks=(
            "设计 SLO/SLI 指标" "配置错误预算告警" "实施混沌工程测试"
            "设计容量规划方案" "配置分布式追踪" "实现自动扩容策略"
            "设计灾难恢复流程" "配置事件响应流程" "实施变更管理流程"
            "设计健康检查端点" "配置指标收集系统" "实现故障自动切换"
            "设计降级预案" "配置日志分析告警" "实施发布检查清单"
            "设计压测方案" "配置 APM 监控" "实现值班轮换系统"
            "设计事后分析流程" "配置依赖健康检查"
        ) ;;
        "dba") tasks=(
            "设计数据库范式" "优化慢查询性能" "配置主从复制"
            "设计数据归档策略" "实施数据库备份" "配置连接池参数"
            "设计分区表方案" "实施权限管理" "配置审计日志"
            "设计索引策略" "实施数据脱敏" "配置故障转移"
            "设计数据迁移方案" "优化存储引擎参数" "实施查询限流"
            "配置监控指标" "设计分库分表" "实施数据清理"
            "配置只读副本" "设计数据恢复流程"
        ) ;;
        "data-engineer") tasks=(
            "设计数据仓库模型" "构建 ETL 数据管道" "实现实时数据流处理"
            "设计数据湖架构" "配置数据质量检查" "实施数据血缘追踪"
            "设计维度建模" "构建特征存储" "实现数据同步任务"
            "设计数据治理框架" "配置数据目录服务" "实施数据标准化"
            "设计 CDC 数据捕获" "构建数据 API 服务" "实现数据脱敏处理"
            "设计数据分层存储" "配置调度系统" "实施数据监控"
            "设计 OLAP 查询优化" "构建实时数仓"
        ) ;;
        "ml-engineer") tasks=(
            "训练文本分类模型" "部署机器学习模型" "优化模型推理性能"
            "设计特征工程流程" "实现模型版本管理" "配置模型监控告警"
            "实施 A/B 测试框架" "设计训练数据管道" "构建推荐系统"
            "优化超参数配置" "实现模型蒸馏" "配置 GPU 训练资源"
            "设计在线学习系统" "实施模型量化" "构建嵌入向量服务"
            "实现迁移学习" "配置实验追踪" "设计模型服务 API"
            "实施数据标注流程" "构建异常检测模型"
        ) ;;
        "test-engineer") tasks=(
            "编写单元测试用例" "设计集成测试方案" "实现 TDD 开发流程"
            "配置自动化测试" "设计测试数据工厂" "编写端到端测试"
            "实施测试覆盖率检查" "设计 Mock 测试策略" "配置 CI 测试流水线"
            "实现性能基准测试" "设计回归测试套件" "编写契约测试"
            "实施视觉回归测试" "配置测试环境" "设计模糊测试方案"
            "实现错误注入测试" "设计负载测试" "编写安全测试用例"
            "实施并行测试" "配置测试报告生成"
        ) ;;
        "ui-test-engineer") tasks=(
            "编写 Playwright E2E 测试" "实现视觉回归测试" "设计 UI 组件测试"
            "配置 Cypress 测试" "实现表单交互测试" "设计导航流程测试"
            "编写辅助功能测试" "实现响应式布局测试" "配置截图对比测试"
            "设计动画测试" "实现拖拽功能测试" "编写模态框测试"
            "设计表格交互测试" "配置移动端测试" "实现多浏览器测试"
            "设计无障碍测试" "编写性能测试" "实现国际化测试"
            "配置暗色模式测试" "设计 PWA 测试"
        ) ;;
        "code-reviewer") tasks=(
            "审查代码规范符合性" "检查命名约定" "评估代码可维护性"
            "识别重复代码" "检查注释质量" "评估函数复杂度"
            "检查错误处理" "审查代码格式" "评估模块耦合度"
            "检查类型安全性" "审查导入组织" "评估代码复用性"
            "检查魔法数字" "审查日志记录" "评估异常处理"
            "检查代码组织" "审查变量作用域" "评估接口设计"
            "检查边界条件" "审查代码风格一致性"
        ) ;;
        "security-reviewer") tasks=(
            "检查 SQL 注入漏洞" "审查 XSS 防护" "验证 CSRF 保护"
            "检查认证逻辑" "审查授权机制" "识别敏感数据泄露"
            "检查输入验证" "审查密码存储" "验证 JWT 实现"
            "检查会话管理" "审查 API 限流" "识别路径遍历"
            "检查命令注入" "审查反序列化" "验证 CORS 配置"
            "检查安全头配置" "审查依赖漏洞" "识别硬编码密钥"
            "检查日志脱敏" "审查文件上传安全"
        ) ;;
        "performance-expert") tasks=(
            "分析接口响应延迟" "识别内存泄漏" "优化数据库查询"
            "分析 CPU 使用率" "优化缓存命中率" "识别 N+1 查询"
            "分析网络请求" "优化序列化性能" "识别瓶颈代码"
            "优化并发处理" "分析 GC 行为" "优化 I/O 操作"
            "识别资源争用" "优化连接池" "分析线程使用"
            "优化批处理" "识别慢查询" "优化数据加载"
            "分析队列积压" "优化异步处理"
        ) ;;
        "product-manager") tasks=(
            "定义产品路线图" "编写用户故事" "确定功能优先级"
            "分析用户需求" "设计产品指标" "规划发布计划"
            "编写 PRD 文档" "分析竞品功能" "定义 MVP 范围"
            "收集用户反馈" "设计增长策略" "分析转化漏斗"
            "规划 A/B 测试" "定义成功指标" "分析市场趋势"
            "设计用户旅程" "编写产品简报" "分析留存数据"
            "规划功能迭代" "定义产品愿景"
        ) ;;
        "scrum-master") tasks=(
            "组织每日站会" "移除团队障碍" "促进回顾会议"
            "跟踪迭代进度" "协调跨团队合作" "促进需求澄清"
            "管理技术债务" "组织计划会议" "跟踪燃尽图"
            "促进持续改进" "管理团队容量" "协调依赖关系"
            "促进知识分享" "管理风险日志" "组织演示会议"
            "跟踪行动项" "促进团队健康" "管理干系人期望"
            "组织培训工作坊" "跟踪团队指标"
        ) ;;
        "tech-lead") tasks=(
            "制定技术路线图" "评审架构设计" "指导初级工程师"
            "决策技术选型" "协调代码审查" "制定编码规范"
            "管理技术债务" "规划能力建设" "评估技术方案"
            "协调跨团队项目" "制定质量标准" "组织技术分享"
            "管理项目风险" "制定发布计划" "评估团队能力"
            "协调资源分配" "制定工程目标" "管理干系人沟通"
            "组织设计评审" "跟踪项目进度"
        ) ;;
        "technical-writer") tasks=(
            "编写 API 文档" "撰写用户指南" "创建教程文档"
            "编写安装手册" "设计文档结构" "撰写发布说明"
            "创建 FAQ 文档" "编写迁移指南" "设计文档模板"
            "撰写最佳实践" "创建快速入门" "编写参考手册"
            "设计文档站点" "撰写技术博客" "创建示例代码"
            "编写变更日志" "设计文档流程" "撰写内部文档"
            "创建演示文稿" "编写培训材料"
        ) ;;
        "researcher") tasks=(
            "调研技术选型方案" "对比竞品功能" "检索相关论文"
            "分析行业趋势" "调研开源方案" "对比云服务提供商"
            "检索技术文档" "分析最佳实践" "调研新兴技术"
            "对比数据库性能" "检索安全报告" "分析用户研究"
            "调研框架特性" "对比 API 设计" "检索性能基准"
            "分析技术风险" "调研工具链" "对比开发效率"
            "检索案例研究" "分析技术社区"
        ) ;;
        "ux-designer") tasks=(
            "设计用户流程" "创建线框图" "设计交互原型"
            "优化导航结构" "设计表单体验" "创建设计规范"
            "设计空状态" "优化加载体验" "设计错误提示"
            "创建图标系统" "设计颜色系统" "优化移动端体验"
            "设计搜索体验" "创建动效设计" "设计通知系统"
            "优化无障碍设计" "设计暗黑模式" "创建组件库"
            "设计数据可视化" "优化表单验证"
        ) ;;
        "prompt-engineer") tasks=(
            "设计系统提示词" "优化 Few-shot 示例" "设计思维链提示"
            "创建角色扮演 prompt" "优化输出格式" "设计多轮对话"
            "创建评估 prompt" "设计自一致性提示" "优化 token 使用"
            "设计 ReAct 模式" "创建代码生成 prompt" "设计分析 prompt"
            "优化摘要 prompt" "设计翻译 prompt" "创建分类 prompt"
            "设计提取 prompt" "优化创意写作 prompt" "设计 debugging prompt"
            "创建教学 prompt" "设计研究 prompt"
        ) ;;
        "quant-researcher") tasks=(
            "挖掘 Alpha 因子" "回测交易策略" "分析因子 IC"
            "优化投资组合" "设计风险管理" "分析市场微观结构"
            "构建多因子模型" "优化执行算法" "分析统计套利"
            "设计事件驱动策略" "构建机器学习模型" "优化参数敏感性"
            "分析因子衰减" "设计对冲策略" "构建波动率模型"
            "优化交易成本" "分析动量效应" "设计均值回归策略"
            "构建神经网络模型" "优化夏普比率"
        ) ;;
        "crypto-trader") tasks=(
            "执行套利交易" "监控链上数据" "分析资金费率"
            "执行网格交易" "监控流动性" "分析市场情绪"
            "执行趋势跟踪" "监控鲸鱼地址" "分析交易量"
            "执行做市策略" "监控 DeFi 协议" "分析持仓分布"
            "执行波段交易" "监控交易所流量" "分析恐慌贪婪指数"
            "执行现货交易" "监控 NFT 市场" "分析社交媒体情绪"
            "执行杠杆交易" "监控稳定币流动"
        ) ;;
        "financial-analyst") tasks=(
            "分析财务报表" "评估公司估值" "分析现金流"
            "预测营收增长" "评估盈利能力" "分析负债结构"
            "预测每股收益" "评估资产质量" "分析运营效率"
            "预测利润率" "评估管理团队" "分析竞争优势"
            "预测自由现金流" "评估行业地位" "分析市场空间"
            "预测投资回报" "评估风险因素" "分析商业模式"
            "预测股价目标" "评估投资建议"
        ) ;;
        "market-monitor") tasks=(
            "监控异常交易" "检测价格异动" "监控成交量突增"
            "检测市场操纵" "监控资金流向" "检测内幕交易"
            "监控订单簿异常" "检测洗盘行为" "监控大宗交易"
            "检测市场情绪" "监控相关新闻" "检测技术信号"
            "监控板块轮动" "检测市场宽度" "监控波动率变化"
            "检测趋势反转" "监控相关性变化" "检测流动性风险"
            "监控系统性风险" "检测黑天鹅事件"
        ) ;;
        "skeptic") tasks=(
            "挑战技术方案假设" "识别潜在风险" "提出替代方案"
            "质疑需求合理性" "识别依赖风险" "挑战架构决策"
            "识别扩展瓶颈" "质疑技术选型" "识别安全风险"
            "挑战性能假设" "识别成本问题" "质疑时间估算"
            "识别团队能力缺口" "挑战用户假设" "识别竞争威胁"
            "质疑商业模式" "识别法规风险" "挑战增长预测"
            "识别技术债务" "质疑项目优先级"
        ) ;;
        *)
            log_warn "未知 Agent: $agent"
            return 1
            ;;
    esac

    for task in "${tasks[@]}"; do
        echo "{\"task\":\"$task\",\"expected_agent\":\"$agent\"}" >> "$output_file"
    done
    log_success "已生成 20 个任务到 $output_file"
}

# 测试单个任务的路由 - 使用 llama.cpp chat API
test_route() {
    local task=$1
    local response

    # 使用 llama.cpp 的 chat/completions API
    response=$(curl -s -X POST "$SERVER/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Route: $task\"}],\"max_tokens\":50}" \
        2>/dev/null)

    echo "$response"
}

# 从响应中提取 Agent
extract_agent() {
    local response=$1
    local content
    content=$(echo "$response" | jq -r '.choices[0].message.content // "error"' 2>/dev/null)

    # 从响应内容中提取 Agent 类型
    # 尝试匹配常见的 Agent 名称
    local agent_patterns=(
        "architect" "backend" "frontend" "fullstack" "mobile"
        "devops" "sre" "dba" "data" "ml" "machine.learning"
        "test" "ui.test" "code" "security" "performance"
        "product" "scrum" "tech.lead" "technical.writer" "research"
        "ux" "designer" "prompt" "quant" "crypto"
        "financial" "market" "skeptic"
    )

    for pattern in "${agent_patterns[@]}"; do
        if echo "$content" | grep -qi "$pattern"; then
            echo "$pattern"
            return
        fi
    done

    echo "unknown"
}

# 测试一个 Agent 的所有任务
test_agent() {
    local agent=$1
    local tasks_file="$OUTPUT_DIR/${agent}_tasks.jsonl"
    local results_file="$OUTPUT_DIR/${agent}_results.jsonl"

    if [[ ! -f "$tasks_file" ]]; then
        log_error "任务文件不存在：$tasks_file"
        return 1
    fi

    log_info "测试 Agent: $agent"
    > "$results_file"

    local success=0
    local total=0

    while IFS= read -r line; do
        task=$(echo "$line" | jq -r '.task')
        expected=$(echo "$line" | jq -r '.expected_agent')

        response=$(test_route "$task")
        if [[ $? -ne 0 ]] || [[ -z "$response" ]]; then
            log_error "路由失败：$task"
            continue
        fi

        content=$(echo "$response" | jq -r '.choices[0].message.content // "error"')
        prompt_tokens=$(echo "$response" | jq -r '.usage.prompt_tokens // 0')
        completion_tokens=$(echo "$response" | jq -r '.usage.completion_tokens // 0')

        ((total++))

        # 简单判断：检查响应是否包含预期的 Agent 关键词
        matched=false
        if echo "$content" | grep -qi "$expected"; then
            matched=true
            ((success++))
        fi

        # 记录结果
        echo "{\"task\":\"$task\",\"expected\":\"$expected\",\"content\":\"${content:0:200}\",\"prompt_tokens\":$prompt_tokens,\"completion_tokens\":$completion_tokens,\"matched\":$matched}" >> "$results_file"

        if $matched; then
            echo -e "  ${GREEN}✓${NC} [$total] $expected"
        else
            echo -e "  ${RED}✗${NC} [$total] $expected -> ${content:0:80}..."
        fi

    done < "$tasks_file"

    local accuracy=0
    if [[ $total -gt 0 ]]; then
        accuracy=$(echo "scale=2; $success * 100 / $total" | bc)
    fi

    log_success "Agent [$agent] 测试完成：$success/$total ($accuracy%)"
    echo "{\"agent\":\"$agent\",\"total\":$total,\"success\":$success,\"accuracy\":$accuracy}" >> "$OUTPUT_DIR/summary.jsonl"
}

# 生成汇总报告
generate_summary() {
    local summary_file="$OUTPUT_DIR/summary_report_$TIMESTAMP.md"

    {
        echo "# RuvLTRA Agent 路由测试报告"
        echo ""
        echo "## 测试概述"
        echo ""
        echo "- **测试日期**: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "- **服务器**: $SERVER"
        echo ""
        echo "## 测试结果汇总"
        echo ""
        echo "| Agent | 任务数 | 成功 | 准确率 |"
        echo "|-------|--------|------|--------|"
    } > "$summary_file"

    local total_all=0
    local success_all=0

    while IFS= read -r line; do
        agent=$(echo "$line" | jq -r '.agent')
        total=$(echo "$line" | jq -r '.total')
        success=$(echo "$line" | jq -r '.success')
        accuracy=$(echo "$line" | jq -r '.accuracy')
        echo "| $agent | $total | $success | ${accuracy}% |" >> "$summary_file"
        total_all=$((total_all + total))
        success_all=$((success_all + success))
    done < "$OUTPUT_DIR/summary.jsonl"

    local overall_accuracy=0
    if [[ $total_all -gt 0 ]]; then
        overall_accuracy=$(echo "scale=2; $success_all * 100 / $total_all" | bc)
    fi

    {
        echo ""
        echo "**总体准确率**: ${success_all}/${total_all} (${overall_accuracy}%)"
        echo ""
        echo "## 输出文件"
        echo ""
        echo "- 任务文件：$OUTPUT_DIR/*_tasks.jsonl"
        echo "- 结果文件：$OUTPUT_DIR/*_results.jsonl"
        echo "- 汇总数据：$OUTPUT_DIR/summary.jsonl"
    } >> "$summary_file"

    log_success "汇总报告已保存到：$summary_file"
}

# 主函数
main() {
    echo "========================================"
    echo "  RuvLTRA Agent 路由测试"
    echo "========================================"
    echo ""

    # 检查服务器连接
    log_info "检查服务器连接：$SERVER"
    if ! curl -s "$SERVER/health" > /dev/null 2>&1; then
        log_error "无法连接到服务器：$SERVER"
        echo "请先启动服务器"
        exit 1
    fi
    log_success "服务器连接正常"

    local health
    health=$(curl -s "$SERVER/health")
    log_info "服务器状态：$(echo "$health" | jq -r '.status // "unknown"')"

    echo ""
    echo "========================================"
    echo "  开始生成测试任务"
    echo "========================================"

    # 生成所有 Agent 的任务
    for agent in "${AGENTS[@]}"; do
        log_info "生成 [$agent] 的任务..."
        generate_tasks "$agent"
    done

    echo ""
    echo "========================================"
    echo "  开始路由测试"
    echo "========================================"

    # 测试每个 Agent
    for agent in "${AGENTS[@]}"; do
        test_agent "$agent"
        echo ""
    done

    echo ""
    echo "========================================"
    echo "  生成汇总报告"
    echo "========================================"

    generate_summary

    echo ""
    echo "========================================"
    echo "  测试完成"
    echo "========================================"
    echo ""
    echo "结果保存在：$OUTPUT_DIR/"
}

main
