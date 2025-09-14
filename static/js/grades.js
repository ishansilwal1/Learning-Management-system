/* Grades JavaScript functionality */

// Global variables
let currentStudentId = null;

// Grade Modal Functions
function openGradeModal(studentId, studentName, currentPercentage) {
    currentStudentId = studentId;
    document.getElementById('studentId').value = studentId;
    document.getElementById('studentName').textContent = studentName;
    document.getElementById('percentage').value = currentPercentage;
    
    updateGradePreview();
    
    const modal = new bootstrap.Modal(document.getElementById('gradeModal'));
    modal.show();
}

function updateGradePreview() {
    const percentage = parseFloat(document.getElementById('percentage').value);
    if (isNaN(percentage)) return;
    
    let letterGrade, passStatus;
    
    // Grade calculation logic
    if (percentage >= 90) letterGrade = 'A+';
    else if (percentage >= 85) letterGrade = 'A';
    else if (percentage >= 80) letterGrade = 'A-';
    else if (percentage >= 75) letterGrade = 'B+';
    else if (percentage >= 70) letterGrade = 'B';
    else if (percentage >= 65) letterGrade = 'B-';
    else if (percentage >= 60) letterGrade = 'C+';
    else if (percentage >= 55) letterGrade = 'C';
    else if (percentage >= 50) letterGrade = 'C-';
    else if (percentage >= 45) letterGrade = 'D+';
    else if (percentage >= 40) letterGrade = 'D';
    else letterGrade = 'F';
    
    passStatus = percentage >= 40 ? 'Pass' : 'Fail';
    
    // Update preview elements
    document.getElementById('letterGrade').textContent = letterGrade;
    document.getElementById('passStatus').textContent = passStatus;
    document.getElementById('passStatus').className = percentage >= 40 ? 'text-success' : 'text-danger';
    document.getElementById('gradePreview').style.display = 'block';
}

function submitGrade() {
    const form = document.getElementById('gradeForm');
    const formData = new FormData(form);
    
    // Get the URL from the form action or a data attribute
    const submitUrl = form.getAttribute('action') || form.dataset.submitUrl;
    
    fetch(submitUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('gradeModal'));
            modal.hide();
            
            // Show success message
            showNotification('Grade saved successfully!', 'success');
            
            // Reload page to show updated grade
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while saving the grade.', 'error');
    });
}

// Utility Functions
function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function formatPercentage(value) {
    return Math.round(value * 100) / 100;
}

function getGradeColor(percentage) {
    if (percentage >= 90) return '#10b981'; // Green
    else if (percentage >= 80) return '#06b6d4'; // Blue
    else if (percentage >= 70) return '#8b5cf6'; // Purple
    else if (percentage >= 60) return '#f59e0b'; // Yellow
    else if (percentage >= 40) return '#f97316'; // Orange
    else return '#dc2626'; // Red
}

function animateProgressBars() {
    const progressBars = document.querySelectorAll('.grade-progress-bar');
    progressBars.forEach(bar => {
        const percentage = bar.dataset.percentage;
        if (percentage) {
            setTimeout(() => {
                bar.style.width = percentage + '%';
                bar.style.backgroundColor = getGradeColor(percentage);
            }, 100);
        }
    });
}

// Grade Chart Functions (if Chart.js is available)
function createGradeDistributionChart(canvasId, gradeData) {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded, skipping chart creation');
        return;
    }
    
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const labels = Object.keys(gradeData);
    const data = Object.values(gradeData);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#10b981', // A+ range
                    '#06b6d4', // B range
                    '#8b5cf6', // C range
                    '#f59e0b', // D range
                    '#dc2626'  // F
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} students (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Initialize functions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for percentage input
    const percentageInput = document.getElementById('percentage');
    if (percentageInput) {
        percentageInput.addEventListener('input', updateGradePreview);
    }
    
    // Animate progress bars
    animateProgressBars();
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// Export functions for global use
window.gradeUtils = {
    openGradeModal,
    updateGradePreview,
    submitGrade,
    showNotification,
    formatPercentage,
    getGradeColor,
    createGradeDistributionChart
};