// llama.cpp 评测报告网站脚本

// 导航菜单激活状态
document.addEventListener('DOMContentLoaded', function() {
    // 获取当前页面路径
    const currentPath = window.location.pathname;
    const currentPage = currentPath.split('/').pop() || 'index.html';

    // 设置导航激活状态
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // 初始化图表（如果页面有图表）
    initCharts();
});

// 图表初始化函数
function initCharts() {
    // 检查是否存在图表容器
    const chartContainers = document.querySelectorAll('canvas');
    if (chartContainers.length === 0) return;

    // Chart.js 配置
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
    Chart.defaults.color = '#64748b';
}

// 表格排序功能
function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();

        // 尝试数字排序
        const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return bNum - aNum; // 降序
        }

        return aValue.localeCompare(bValue);
    });

    rows.forEach(row => tbody.appendChild(row));
}

// 搜索过滤功能
function filterTable(tableId, searchTerm) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}

// 导出表格为 CSV
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];

        cols.forEach(col => {
            let data = col.textContent.replace(/"/g, '""').trim();
            rowData.push('"' + data + '"');
        });

        csv.push(rowData.join(','));
    });

    const csvContent = '\uFEFF' + csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

// 平滑滚动到锚点
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// 响应式侧边栏切换
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('open');
}

// 添加移动端菜单按钮
if (window.innerWidth <= 768) {
    const menuButton = document.createElement('button');
    menuButton.innerHTML = '☰';
    menuButton.className = 'mobile-menu-btn';
    menuButton.style.cssText = `
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 101;
        background: var(--primary-color);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 1.25rem;
        cursor: pointer;
    `;
    menuButton.onclick = toggleSidebar;
    document.body.appendChild(menuButton);
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 添加表格行悬停效果
    const tables = document.querySelectorAll('.data-table');
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#f8fafc';
            });
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
    });

    // 添加卡片悬停动画
    const cards = document.querySelectorAll('.stage-card, .rec-card, .backend-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
});

// 打印功能
function printReport() {
    window.print();
}

// 复制代码到剪贴板
function copyCode(button) {
    const codeBlock = button.nextElementSibling;
    const code = codeBlock.textContent;

    navigator.clipboard.writeText(code).then(() => {
        const originalText = button.textContent;
        button.textContent = '已复制!';
        setTimeout(() => {
            button.textContent = originalText;
        }, 2000);
    });
}

// 添加代码复制按钮
document.addEventListener('DOMContentLoaded', function() {
    const codeBlocks = document.querySelectorAll('.code-block');
    codeBlocks.forEach(block => {
        const button = document.createElement('button');
        button.textContent = '复制';
        button.className = 'copy-btn';
        button.style.cssText = `
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: rgba(255,255,255,0.1);
            color: #e2e8f0;
            border: 1px solid rgba(255,255,255,0.2);
            padding: 0.25rem 0.75rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
        `;
        button.onclick = function() {
            navigator.clipboard.writeText(block.textContent).then(() => {
                this.textContent = '已复制!';
                setTimeout(() => {
                    this.textContent = '复制';
                }, 2000);
            });
        };

        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        block.parentNode.insertBefore(wrapper, block);
        wrapper.appendChild(button);
        wrapper.appendChild(block);
    });
});

// 暗黑模式切换（可选）
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// 初始化暗黑模式
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}
