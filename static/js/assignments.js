/* Assignments JavaScript functionality */

// Date and time utilities for assignments
function setMinimumDateTime() {
    const deadlineInput = document.getElementById('deadline');
    if (deadlineInput) {
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        deadlineInput.min = now.toISOString().slice(0, 16);
    }
}

// File upload validation
function validateAssignmentFile(input) {
    const file = input.files[0];
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['.pdf', '.doc', '.docx', '.txt', '.zip'];
    
    if (file) {
        // Check file size
        if (file.size > maxSize) {
            showNotification('File size must be less than 10MB', 'error');
            input.value = '';
            return false;
        }
        
        // Check file type
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileExtension)) {
            showNotification('File type not allowed. Please upload: ' + allowedTypes.join(', '), 'error');
            input.value = '';
            return false;
        }
        
        // Show file preview
        const preview = document.getElementById('filePreview');
        if (preview) {
            preview.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-file-earmark"></i> ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)
                </div>
            `;
        }
        
        return true;
    }
    return false;
}

// Assignment form validation
function validateAssignmentForm() {
    const title = document.getElementById('title');
    const description = document.getElementById('description');
    const deadline = document.getElementById('deadline');
    let isValid = true;
    
    // Clear previous errors
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    
    // Title validation
    if (!title.value.trim()) {
        title.classList.add('is-invalid');
        isValid = false;
    }
    
    // Description validation
    if (!description.value.trim()) {
        description.classList.add('is-invalid');
        isValid = false;
    }
    
    // Deadline validation
    if (!deadline.value) {
        deadline.classList.add('is-invalid');
        isValid = false;
    } else {
        const selectedDate = new Date(deadline.value);
        const now = new Date();
        if (selectedDate <= now) {
            deadline.classList.add('is-invalid');
            showNotification('Deadline must be in the future', 'error');
            isValid = false;
        }
    }
    
    return isValid;
}

// Assignment submission handling
function submitAssignment(formId) {
    if (!validateAssignmentForm()) {
        return false;
    }
    
    const form = document.getElementById(formId);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating...';
    }
    
    return true;
}

// Auto-save draft functionality
let autoSaveTimer;
function setupAutoSave() {
    const form = document.getElementById('assignmentForm');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(autoSaveTimer);
            autoSaveTimer = setTimeout(saveDraft, 2000); // Save after 2 seconds of inactivity
        });
    });
}

function saveDraft() {
    const form = document.getElementById('assignmentForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const draftData = {};
    
    for (let [key, value] of formData.entries()) {
        draftData[key] = value;
    }
    
    // Save to localStorage
    localStorage.setItem('assignmentDraft_' + (form.dataset.classroomId || 'new'), JSON.stringify(draftData));
    
    // Show draft saved indicator
    const indicator = document.getElementById('draftIndicator');
    if (indicator) {
        indicator.textContent = 'Draft saved at ' + new Date().toLocaleTimeString();
        indicator.style.display = 'block';
        setTimeout(() => {
            indicator.style.display = 'none';
        }, 3000);
    }
}

function loadDraft() {
    const form = document.getElementById('assignmentForm');
    if (!form) return;
    
    const draftKey = 'assignmentDraft_' + (form.dataset.classroomId || 'new');
    const savedDraft = localStorage.getItem(draftKey);
    
    if (savedDraft) {
        const draftData = JSON.parse(savedDraft);
        
        for (let [key, value] of Object.entries(draftData)) {
            const field = form.querySelector(`[name="${key}"]`);
            if (field && field.type !== 'file') {
                field.value = value;
            }
        }
        
        showNotification('Draft loaded', 'info', 2000);
    }
}

function clearDraft() {
    const form = document.getElementById('assignmentForm');
    if (!form) return;
    
    const draftKey = 'assignmentDraft_' + (form.dataset.classroomId || 'new');
    localStorage.removeItem(draftKey);
}

// Initialize assignment functionality
document.addEventListener('DOMContentLoaded', function() {
    // Set minimum date/time
    setMinimumDateTime();
    
    // Setup auto-save if creating/editing assignment
    setupAutoSave();
    
    // Load draft if available
    loadDraft();
    
    // Add file validation to file inputs
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            validateAssignmentFile(this);
        });
    });
    
    // Add form validation to assignment forms
    const assignmentForm = document.getElementById('assignmentForm');
    if (assignmentForm) {
        assignmentForm.addEventListener('submit', function(e) {
            if (!validateAssignmentForm()) {
                e.preventDefault();
                return false;
            }
            
            // Clear draft on successful submission
            clearDraft();
        });
    }
});

// Export functions for global use
window.assignmentUtils = {
    setMinimumDateTime,
    validateAssignmentFile,
    validateAssignmentForm,
    submitAssignment,
    saveDraft,
    loadDraft,
    clearDraft
};