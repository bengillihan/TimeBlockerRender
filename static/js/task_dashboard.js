// Enhanced Task Dashboard JavaScript
let currentTasks = [];
let currentRoles = [];
let currentCategories = [];
let selectedTaskId = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    loadCategories();
    loadRoles();
    loadTasks();
    loadAnalytics();
    
    // Set up event listeners
    setupEventListeners();
    
    // Auto-refresh analytics every 30 seconds
    setInterval(loadAnalytics, 30000);
});

function setupEventListeners() {
    // Filter change handlers
    document.getElementById('status-filter').addEventListener('change', filterTasks);
    document.getElementById('priority-filter').addEventListener('change', filterTasks);
    document.getElementById('role-filter').addEventListener('change', filterTasks);
    document.getElementById('overdue-filter').addEventListener('change', filterTasks);
    
    // Modal form handlers
    document.getElementById('save-task-btn').addEventListener('click', saveTask);
    document.getElementById('save-role-btn').addEventListener('click', saveRole);
    document.getElementById('save-category-btn').addEventListener('click', saveCategory);
    
    // Progress slider
    const progressSlider = document.getElementById('progress-slider');
    const progressValue = document.getElementById('progress-value');
    
    progressSlider.addEventListener('input', function() {
        progressValue.textContent = this.value;
    });
    
    document.getElementById('update-progress-btn').addEventListener('click', updateTaskProgress);
    document.getElementById('add-comment-btn').addEventListener('click', addTaskComment);
    document.getElementById('edit-task-btn').addEventListener('click', editTask);
    document.getElementById('delete-task-btn').addEventListener('click', deleteTask);
}

async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        if (response.ok) {
            currentCategories = await response.json();
            populateCategorySelects();
        }
    } catch (error) {
        console.error('Error loading categories:', error);
        showAlert('Error loading categories', 'danger');
    }
}

async function loadRoles() {
    try {
        const response = await fetch('/api/roles');
        if (response.ok) {
            currentRoles = await response.json();
            populateRoleSelects();
        }
    } catch (error) {
        console.error('Error loading roles:', error);
        showAlert('Error loading roles', 'danger');
    }
}

async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        if (response.ok) {
            currentTasks = await response.json();
            displayTasks(currentTasks);
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
        showAlert('Error loading tasks', 'danger');
    }
}

async function loadAnalytics() {
    try {
        const response = await fetch('/api/tasks/analytics');
        if (response.ok) {
            const analytics = await response.json();
            updateAnalyticsCards(analytics);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function populateCategorySelects() {
    const selects = ['task-category'];
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            // Clear existing options except the first one
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }
            
            currentCategories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                select.appendChild(option);
            });
        }
    });
}

function populateRoleSelects() {
    const selects = ['task-role', 'role-filter'];
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            // Clear existing options except the first one
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }
            
            currentRoles.forEach(role => {
                const option = document.createElement('option');
                option.value = role.id;
                option.textContent = role.name;
                select.appendChild(option);
            });
        }
    });
}

function updateAnalyticsCards(analytics) {
    document.getElementById('total-tasks').textContent = analytics.total_tasks;
    document.getElementById('completed-tasks').textContent = analytics.completed_tasks;
    document.getElementById('in-progress-tasks').textContent = analytics.in_progress_tasks;
    document.getElementById('overdue-tasks').textContent = analytics.overdue_tasks;
}

function displayTasks(tasks) {
    const tbody = document.getElementById('tasks-tbody');
    tbody.innerHTML = '';
    
    tasks.forEach(task => {
        const row = createTaskRow(task);
        tbody.appendChild(row);
    });
}

function createTaskRow(task) {
    const row = document.createElement('tr');
    if (task.is_overdue) {
        row.classList.add('table-danger');
    }
    
    const dueDateFormatted = task.due_date ? 
        new Date(task.due_date).toLocaleDateString() : '-';
    
    const progressBar = `
        <div class="progress" style="height: 20px;">
            <div class="progress-bar bg-${task.status_color}" 
                 role="progressbar" 
                 style="width: ${task.progress_percentage}%"
                 aria-valuenow="${task.progress_percentage}" 
                 aria-valuemin="0" 
                 aria-valuemax="100">
                ${task.progress_percentage}%
            </div>
        </div>
    `;
    
    row.innerHTML = `
        <td>
            <div class="d-flex align-items-center">
                <div>
                    <h6 class="mb-0">${escapeHtml(task.title)}</h6>
                    <small class="text-muted">${escapeHtml(task.description || '')}</small>
                    ${task.tags && task.tags.length > 0 ? 
                        '<div class="mt-1">' + task.tags.map(tag => 
                            `<span class="badge bg-secondary me-1">${escapeHtml(tag)}</span>`
                        ).join('') + '</div>' : ''}
                </div>
            </div>
        </td>
        <td>
            <span class="badge" style="background-color: ${task.category_color}; color: white;">
                ${escapeHtml(task.category_name)}
            </span>
        </td>
        <td>
            ${task.role_name ? 
                `<span class="badge bg-info">${escapeHtml(task.role_name)}</span>` : 
                '<span class="text-muted">-</span>'}
        </td>
        <td>
            <span class="badge bg-${task.priority_color}">
                ${task.priority.toUpperCase()}
            </span>
        </td>
        <td>
            <span class="badge bg-${task.status_color}">
                ${task.status.replace('_', ' ').toUpperCase()}
            </span>
        </td>
        <td style="width: 120px;">
            ${progressBar}
        </td>
        <td>
            ${dueDateFormatted}
            ${task.is_overdue ? '<i class="fas fa-exclamation-triangle text-danger ms-1"></i>' : ''}
        </td>
        <td>
            <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-primary" onclick="viewTaskDetails(${task.id})" title="View Details">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-outline-success" onclick="toggleTaskComplete(${task.id}, ${!task.completed})" title="${task.completed ? 'Mark Incomplete' : 'Mark Complete'}">
                    <i class="fas fa-${task.completed ? 'undo' : 'check'}"></i>
                </button>
            </div>
        </td>
    `;
    
    return row;
}

function filterTasks() {
    const statusFilter = document.getElementById('status-filter').value;
    const priorityFilter = document.getElementById('priority-filter').value;
    const roleFilter = document.getElementById('role-filter').value;
    const overdueFilter = document.getElementById('overdue-filter').checked;
    
    let filteredTasks = currentTasks.filter(task => {
        if (statusFilter && task.status !== statusFilter) return false;
        if (priorityFilter && task.priority !== priorityFilter) return false;
        if (roleFilter && task.role_id != roleFilter) return false;
        if (overdueFilter && !task.is_overdue) return false;
        return true;
    });
    
    displayTasks(filteredTasks);
}

async function saveTask() {
    const formData = {
        title: document.getElementById('task-title').value,
        description: document.getElementById('task-description').value,
        category_id: parseInt(document.getElementById('task-category').value),
        role_id: document.getElementById('task-role').value ? 
            parseInt(document.getElementById('task-role').value) : null,
        priority: document.getElementById('task-priority').value,
        due_date: document.getElementById('task-due-date').value || null,
        estimated_minutes: document.getElementById('task-estimated-hours').value ? 
            parseFloat(document.getElementById('task-estimated-hours').value) * 60 : null,
        tags: document.getElementById('task-tags').value ? 
            document.getElementById('task-tags').value.split(',').map(tag => tag.trim()) : [],
        is_recurring: document.getElementById('task-recurring').checked,
        notes: document.getElementById('task-notes').value || null
    };
    
    if (!formData.title || !formData.category_id) {
        showAlert('Please fill in all required fields', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const task = await response.json();
            showAlert('Task created successfully', 'success');
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('addTaskModal'));
            modal.hide();
            document.getElementById('task-form').reset();
            
            // Reload tasks and analytics
            loadTasks();
            loadAnalytics();
        } else {
            const error = await response.json();
            showAlert(error.error || 'Failed to create task', 'danger');
        }
    } catch (error) {
        console.error('Error creating task:', error);
        showAlert('Error creating task', 'danger');
    }
}

async function saveRole() {
    const formData = {
        name: document.getElementById('role-name').value,
        color: document.getElementById('role-color').value,
        description: document.getElementById('role-description').value
    };
    
    if (!formData.name) {
        showAlert('Please enter a role name', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/roles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const role = await response.json();
            showAlert('Role created successfully', 'success');
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('addRoleModal'));
            modal.hide();
            document.getElementById('role-form').reset();
            
            // Reload roles
            loadRoles();
        } else {
            const error = await response.json();
            showAlert(error.error || 'Failed to create role', 'danger');
        }
    } catch (error) {
        console.error('Error creating role:', error);
        showAlert('Error creating role', 'danger');
    }
}

async function saveCategory() {
    const formData = {
        name: document.getElementById('category-name').value,
        color: document.getElementById('category-color').value
    };
    
    if (!formData.name) {
        showAlert('Please enter a category name', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const category = await response.json();
            showAlert('Category created successfully', 'success');
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('addCategoryModal'));
            modal.hide();
            document.getElementById('category-form').reset();
            
            // Reload categories
            loadCategories();
        } else {
            const error = await response.json();
            showAlert(error.error || 'Failed to create category', 'danger');
        }
    } catch (error) {
        console.error('Error creating category:', error);
        showAlert('Error creating category', 'danger');
    }
}

async function viewTaskDetails(taskId) {
    selectedTaskId = taskId;
    const task = currentTasks.find(t => t.id === taskId);
    
    if (!task) {
        showAlert('Task not found', 'danger');
        return;
    }
    
    // Update modal title
    document.getElementById('task-detail-title').textContent = task.title;
    
    // Update task info
    const taskInfoContent = document.getElementById('task-info-content');
    taskInfoContent.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <p><strong>Description:</strong> ${escapeHtml(task.description || 'No description')}</p>
                <p><strong>Category:</strong> 
                    <span class="badge" style="background-color: ${task.category_color}; color: white;">
                        ${escapeHtml(task.category_name)}
                    </span>
                </p>
                <p><strong>Priority:</strong> 
                    <span class="badge bg-${task.priority_color}">
                        ${task.priority.toUpperCase()}
                    </span>
                </p>
                <p><strong>Status:</strong> 
                    <span class="badge bg-${task.status_color}">
                        ${task.status.replace('_', ' ').toUpperCase()}
                    </span>
                </p>
            </div>
            <div class="col-md-6">
                <p><strong>Role:</strong> ${task.role_name || 'None assigned'}</p>
                <p><strong>Due Date:</strong> ${task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}</p>
                <p><strong>Created:</strong> ${new Date(task.created_at).toLocaleDateString()}</p>
                <p><strong>Tags:</strong> 
                    ${task.tags && task.tags.length > 0 ? 
                        task.tags.map(tag => `<span class="badge bg-secondary me-1">${escapeHtml(tag)}</span>`).join('') : 
                        'No tags'}
                </p>
            </div>
        </div>
        ${task.notes ? `
        <div class="row mt-3">
            <div class="col-12">
                <p><strong>Notes:</strong></p>
                <div class="p-2 bg-light rounded">${escapeHtml(task.notes)}</div>
            </div>
        </div>
        ` : ''}
    `;
    
    // Update progress slider
    const progressSlider = document.getElementById('progress-slider');
    const progressValue = document.getElementById('progress-value');
    progressSlider.value = task.progress_percentage;
    progressValue.textContent = task.progress_percentage;
    
    // Update time tracking
    document.getElementById('estimated-time').textContent = task.estimated_minutes ? (task.estimated_minutes / 60).toFixed(1) : '-';
    document.getElementById('time-spent').textContent = (task.total_time_spent / 60).toFixed(1);
    document.getElementById('last-worked').textContent = task.last_worked_on ? new Date(task.last_worked_on).toLocaleDateString() : 'Never';
    
    // Load comments
    loadTaskComments(taskId);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('taskDetailModal'));
    modal.show();
}

async function loadTaskComments(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/comments`);
        if (response.ok) {
            const comments = await response.json();
            const commentsList = document.getElementById('comments-list');
            
            if (comments.length === 0) {
                commentsList.innerHTML = '<p class="text-muted">No comments yet.</p>';
            } else {
                commentsList.innerHTML = comments.map(comment => `
                    <div class="mb-2 p-2 bg-light rounded">
                        <small class="text-muted">${new Date(comment.created_at).toLocaleDateString()}</small>
                        <p class="mb-0">${escapeHtml(comment.content)}</p>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Error loading comments:', error);
    }
}

async function addTaskComment() {
    const content = document.getElementById('new-comment').value.trim();
    if (!content) {
        showAlert('Please enter a comment', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${selectedTaskId}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content })
        });
        
        if (response.ok) {
            document.getElementById('new-comment').value = '';
            loadTaskComments(selectedTaskId);
            showAlert('Comment added successfully', 'success');
        } else {
            const error = await response.json();
            showAlert(error.error || 'Failed to add comment', 'danger');
        }
    } catch (error) {
        console.error('Error adding comment:', error);
        showAlert('Error adding comment', 'danger');
    }
}

async function updateTaskProgress() {
    const progress = parseInt(document.getElementById('progress-slider').value);
    
    try {
        const response = await fetch(`/api/tasks/${selectedTaskId}/progress`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ progress_percentage: progress })
        });
        
        if (response.ok) {
            showAlert('Progress updated successfully', 'success');
            loadTasks();
            loadAnalytics();
        } else {
            const error = await response.json();
            showAlert(error.error || 'Failed to update progress', 'danger');
        }
    } catch (error) {
        console.error('Error updating progress:', error);
        showAlert('Error updating progress', 'danger');
    }
}

async function toggleTaskComplete(taskId, completed) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ completed })
        });
        
        if (response.ok) {
            showAlert(`Task marked as ${completed ? 'completed' : 'incomplete'}`, 'success');
            loadTasks();
            loadAnalytics();
        } else {
            const error = await response.json();
            showAlert(error.error || 'Failed to update task', 'danger');
        }
    } catch (error) {
        console.error('Error updating task:', error);
        showAlert('Error updating task', 'danger');
    }
}

function editTask() {
    // This would open the task form in edit mode
    // For now, just close the detail modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('taskDetailModal'));
    modal.hide();
    showAlert('Edit functionality will be available soon', 'info');
}

async function deleteTask() {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${selectedTaskId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Task deleted successfully', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('taskDetailModal'));
            modal.hide();
            loadTasks();
            loadAnalytics();
        } else {
            showAlert('Failed to delete task', 'danger');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showAlert('Error deleting task', 'danger');
    }
}

function showAlert(message, type) {
    // Create and show Bootstrap alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}