// Main JavaScript for llama.cpp Test Report Web

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Add smooth scrolling for anchor links
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

    // Animate progress bars on scroll
    const progressBars = document.querySelectorAll('.progress-bar');
    const animateProgressBar = (bar) => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 100);
    };

    // Use Intersection Observer for scroll animations
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateProgressBar(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        progressBars.forEach(bar => observer.observe(bar));
    } else {
        // Fallback for browsers without IntersectionObserver
        progressBars.forEach(bar => animateProgressBar(bar));
    }
});

// Utility function to format numbers
function formatNumber(num, decimals = 1) {
    return parseFloat(num).toFixed(decimals);
}

// Utility function to format percentage
function formatPercent(value, total, decimals = 1) {
    if (total === 0) return '0.0%';
    return ((value / total) * 100).toFixed(decimals) + '%';
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show toast notification (if Bootstrap is available)
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toast = new bootstrap.Toast(document.getElementById('copyToast'));
            toast.show();
        }
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}
