#!/bin/bash
# RuvLTRA Agent 路由测试脚本 - 使用系统提示词
# 为 ole-teams 中的 28 个 Agent 角色各测试 5 个任务（简化版）

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
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Agent 列表
AGENTS=(
    "architect" "backend-dev" "frontend-dev" "fullstack-dev" "mobile-dev"
    "devops-engineer" "sre" "dba" "data-engineer" "ml-engineer"
    "test-engineer" "ui-test-engineer" "code-reviewer" "security-reviewer"
    "performance-expert" "product-manager" "scrum-master" "tech-lead"
    "technical-writer" "researcher" "ux-designer" "prompt-engineer"
    "quant-researcher" "crypto-trader" "financial-analyst" "market-monitor" "skeptic"
)

# 每个 Agent 的 5 个测试任务
declare -A TASKS
TASKS=(
    ["architect"]="设计微服务架构|评估 PostgreSQL 还是 MongoDB|规划水平扩展策略|设计事件驱动架构|选择消息队列"
    ["backend-dev"]="实现用户认证 API|设计 RESTful API|实现数据库事务|编写数据验证逻辑|实现 WebSocket 通信"
    ["frontend-dev"]="实现响应式导航组件|优化页面加载性能|实现表单验证|设计 UI 组件库|优化 bundle 体积"
    ["fullstack-dev"]="实现用户管理系统|开发博客平台|实现实时聊天|开发任务管理工具|实现文件共享平台"
    ["mobile-dev"]="实现 React Native 导航|开发离线数据同步|实现推送通知|优化移动端性能|实现相机功能"
    ["devops-engineer"]="配置 CI/CD 流水线|编写 Docker 构建|设计 K8s 部署|配置监控告警|编写 Terraform"
    ["sre"]="设计 SLO/SLI 指标|配置错误预算告警|实施混沌工程|设计容量规划|配置分布式追踪"
    ["dba"]="设计数据库范式|优化慢查询|配置主从复制|设计索引策略|实施数据库备份"
    ["data-engineer"]="设计数据仓库模型|构建 ETL 管道|实现实时数据流|设计数据湖|配置数据质量检查"
    ["ml-engineer"]="训练文本分类模型|部署机器学习模型|优化模型推理|设计特征工程|构建推荐系统"
    ["test-engineer"]="编写单元测试|设计集成测试|实现 TDD 流程|配置自动化测试|设计测试数据工厂"
    ["ui-test-engineer"]="编写 Playwright 测试|实现视觉回归|设计 UI 组件测试|配置 Cypress|实现表单测试"
    ["code-reviewer"]="审查代码规范|检查命名约定|评估可维护性|识别重复代码|检查错误处理"
    ["security-reviewer"]="检查 SQL 注入|审查 XSS 防护|验证 CSRF 保护|检查认证逻辑|审查授权机制"
    ["performance-expert"]="分析响应延迟|识别内存泄漏|优化数据库查询|分析 CPU 使用|优化缓存命中率"
    ["product-manager"]="定义产品路线图|编写用户故事|确定功能优先级|分析用户需求|设计产品指标"
    ["scrum-master"]="组织每日站会|移除团队障碍|促进回顾会议|跟踪迭代进度|协调跨团队合作"
    ["tech-lead"]="制定技术路线图|评审架构设计|指导初级工程师|决策技术选型|协调代码审查"
    ["technical-writer"]="编写 API 文档|撰写用户指南|创建教程文档|编写安装手册|设计文档结构"
    ["researcher"]="调研技术选型|对比竞品功能|检索相关论文|分析行业趋势|调研开源方案"
    ["ux-designer"]="设计用户流程|创建线框图|设计交互原型|优化导航结构|设计表单体验"
    ["prompt-engineer"]="设计系统提示词|优化 Few-shot 示例|设计思维链提示|创建角色扮演|优化输出格式"
    ["quant-researcher"]="挖掘 Alpha 因子|回测交易策略|分析因子 IC|优化投资组合|设计风险管理"
    ["crypto-trader"]="执行套利交易|监控链上数据|分析资金费率|执行网格交易|监控流动性"
    ["financial-analyst"]="分析财务报表|评估公司估值|分析现金流|预测营收增长|评估盈利能力"
    ["market-monitor"]="监控异常交易|检测价格异动|监控成交量|检测市场操纵|监控资金流向"
    ["skeptic"]="挑战技术方案假设|识别潜在风险|提出替代方案|质疑需求合理性|识别依赖风险"
)

# 系统提示词
SYSTEM_PROMPT="Assign tasks to agents. Output only agent name. Agents: ${AGENTS[*]}"

# 测试路由
test_route() {
    local task=$1
    local response

    response=$(curl -s -X POST "$SERVER/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d "{
            \"messages\":[
                {\"role\":\"system\",\"content\":\"$SYSTEM_PROMPT\"},
                {\"role\":\"user\",\"content\":\"Assign: $task\"}
            ],
            \"max_tokens\": 3,
            \"temperature\": 0.0
        }" 2>/dev/null)

    echo "$response" | jq -r '.choices[0].message.content // "error"'
}

# 测试单个 Agent
test_agent() {
    local agent=$1
    local agent_tasks="${TASKS[$agent]}"
    local results_file="$OUTPUT_DIR/${agent}_results.jsonl"

    log_info "测试 Agent: $agent"
    > "$results_file"

    local success=0
    local total=0

    IFS='|' read -ra task_array <<< "$agent_tasks"
    for task in "${task_array[@]}"; do
        actual=$(test_route "$task")
        ((total++))

        # 检查是否匹配（部分匹配）
        matched=false
        if [[ "$actual" == *"$agent"* ]] || [[ "$agent" == *"$actual"* ]]; then
            matched=true
            ((success++))
            echo -e "  ${GREEN}✓${NC} $task -> $actual"
        else
            echo -e "  ${RED}✗${NC} $task -> 期望：$agent, 实际：$actual"
        fi

        echo "{\"task\":\"$task\",\"expected\":\"$agent\",\"actual\":\"$actual\",\"matched\":$matched}" >> "$results_file"
    done

    local accuracy=0
    if [[ $total -gt 0 ]]; then
        accuracy=$(echo "scale=1; $success * 100 / $total" | bc)
    fi

    log_success "Agent [$agent] 准确率：$success/$total ($accuracy%)"
    echo "{\"agent\":\"$agent\",\"total\":$total,\"success\":$success,\"accuracy\":$accuracy}" >> "$OUTPUT_DIR/summary.jsonl"
}

# 生成汇总报告
generate_summary() {
    local summary_file="$OUTPUT_DIR/summary_report_$TIMESTAMP.md"

    {
        echo "# RuvLTRA Agent 路由测试报告"
        echo ""
        echo "## 测试概述"
        echo "- **测试日期**: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "- **服务器**: $SERVER"
        echo "- **系统提示词**: $SYSTEM_PROMPT"
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
        overall_accuracy=$(echo "scale=1; $success_all * 100 / $total_all" | bc)
    fi

    {
        echo ""
        echo "**总体准确率**: ${success_all}/${total_all} (${overall_accuracy}%)"
    } >> "$summary_file"

    log_success "汇总报告：$summary_file"
}

# 主函数
main() {
    echo "========================================"
    echo "  RuvLTRA Agent 路由测试"
    echo "========================================"

    # 检查服务器
    if ! curl -s "$SERVER/health" > /dev/null; then
        log_error "无法连接到服务器"
        exit 1
    fi
    log_success "服务器连接正常"

    > "$OUTPUT_DIR/summary.jsonl"

    # 测试每个 Agent
    for agent in "${AGENTS[@]}"; do
        test_agent "$agent"
        echo ""
    done

    generate_summary

    echo ""
    echo "========================================"
    echo "  测试完成"
    echo "========================================"
    echo "结果保存在：$OUTPUT_DIR/"
}

main
