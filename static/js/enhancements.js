// Keyboard shortcuts and UI enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize keyboard shortcuts
    initKeyboardShortcuts();
    
    // Initialize drag and drop
    initDragAndDrop();
    
    // Initialize quick add
    initQuickAdd();
    
    // Initialize dark mode
    initDarkMode();
    
    // Initialize role-based color coding
    initRoleColorCoding();
});

// Keyboard shortcuts
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if (e.altKey) {
            switch (e.key.toLowerCase()) {
                case 'n':
                    e.preventDefault();
                    const newTaskBtn = document.getElementById('newTaskBtn');
                    if (newTaskBtn) newTaskBtn.click();
                    break;
                case 't':
                    e.preventDefault();
                    const newTodoBtn = document.getElementById('newTodoBtn');
                    if (newTodoBtn) newTodoBtn.click();
                    break;
                case 'q':
                    e.preventDefault();
                    const quickAddBtn = document.getElementById('quickAddBtn');
                    if (quickAddBtn) quickAddBtn.click();
                    break;
                case 's':
                    e.preventDefault();
                    const saveBtn = document.getElementById('saveBtn');
                    if (saveBtn) saveBtn.click();
                    break;
                case 'd':
                    e.preventDefault();
                    toggleDarkMode();
                    break;
            }
        }
    });
}

// Drag and drop functionality
function initDragAndDrop() {
    const timeBlocks = document.querySelectorAll('.time-block');
    const timeSlots = document.querySelectorAll('.time-slot');
    
    timeBlocks.forEach(block => {
        block.setAttribute('draggable', true);
        
        block.addEventListener('dragstart', (e) => {
            block.classList.add('dragging');
            e.dataTransfer.setData('text/plain', block.id);
        });
        
        block.addEventListener('dragend', () => {
            block.classList.remove('dragging');
            cleanupDragArtifacts();
        });
    });
    
    timeSlots.forEach(slot => {
        slot.addEventListener('dragover', (e) => {
            e.preventDefault();
            slot.classList.add('drag-over');
        });
        
        slot.addEventListener('dragleave', () => {
            slot.classList.remove('drag-over');
        });
        
        slot.addEventListener('drop', (e) => {
            e.preventDefault();
            slot.classList.remove('drag-over');
            cleanupDragArtifacts();
            const blockId = e.dataTransfer.getData('text/plain');
            const block = document.getElementById(blockId);
            const container = slot.querySelector('.time-block-container');
            
            if (block && container) {
                container.appendChild(block);
                updateTimeBlock(blockId, slot.dataset.time);
            }
        });
    });
    
    document.addEventListener('dragend', () => {
        cleanupDragArtifacts();
    });
}

function cleanupDragArtifacts() {
    document.querySelectorAll('.dragging').forEach(el => el.classList.remove('dragging'));
    document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
}

// Quick add functionality
function initQuickAdd() {
    const quickAddBtn = document.getElementById('quickAddBtn');
    const quickAddModal = document.getElementById('quickAddModal');
    const quickAddForm = document.getElementById('quickAddForm');
    
    if (quickAddBtn && quickAddModal) {
        quickAddBtn.addEventListener('click', () => {
            quickAddModal.classList.add('show');
        });
        
        quickAddModal.addEventListener('click', (e) => {
            if (e.target === quickAddModal) {
                quickAddModal.classList.remove('show');
            }
        });
        
        if (quickAddForm) {
            quickAddForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(quickAddForm);
                const data = {
                    type: formData.get('type'),
                    title: formData.get('title'),
                    description: formData.get('description'),
                    due_date: formData.get('due_date'),
                    priority: formData.get('priority')
                };
                
                try {
                    const response = await fetch(`/api/${data.type}s`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`Failed to create ${data.type}`);
                    }
                    
                    quickAddModal.classList.remove('show');
                    quickAddForm.reset();
                    showToast(`${data.type} created successfully`, 'success');
                    location.reload();
                } catch (error) {
                    console.error(`Error creating ${data.type}:`, error);
                    showToast(`Failed to create ${data.type}`, 'error');
                }
            });
        }
    }
}

// Dark mode functionality
function initDarkMode() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    }

    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'darkModeBtn';
    toggleBtn.className = 'dark-mode-toggle';
    const isDark = (localStorage.getItem('theme') || 'dark') === 'dark';
    toggleBtn.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    toggleBtn.onclick = toggleDarkMode;
    document.body.appendChild(toggleBtn);
}

function toggleDarkMode() {
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    document.documentElement.setAttribute('data-bs-theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    const btn = document.getElementById('darkModeBtn');
    if (btn) {
        btn.innerHTML = newTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    }
}

// Time block position update
async function updateTimeBlock(blockId, newTime) {
    try {
        const response = await fetch(`/api/time-blocks/${blockId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ start_time: newTime })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update time block');
        }
        
        showToast('Time block updated successfully', 'success');
    } catch (error) {
        console.error('Error updating time block:', error);
        showToast('Failed to update time block', 'error');
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

// Auto-save functionality
function initAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                clearTimeout(window.autoSaveTimeout);
                window.autoSaveTimeout = setTimeout(() => {
                    saveForm(form);
                }, 2000);
            });
        });
    });
}

async function saveForm(form) {
    try {
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            showToast('Changes saved automatically', 'success');
        }
    } catch (error) {
        console.error('Auto-save failed:', error);
    }
}

// Role-based color coding
function initRoleColorCoding() {
    document.querySelectorAll('.task-select').forEach(select => {
        select.addEventListener('change', function() {
            updateTimeBlockColor(this);
        });
        
        if (select.value) {
            updateTimeBlockColor(select);
        }
    });
}

function updateTimeBlockColor(selectElement) {
    const timeContent = selectElement.closest('.time-content');
    const selectedOption = selectElement.options[selectElement.selectedIndex];
    
    if (selectedOption && selectedOption.value) {
        const categoryColor = selectedOption.getAttribute('data-category-color');
        const categoryName = selectedOption.getAttribute('data-category-name');
        
        if (categoryColor) {
            // Apply category-based background color with transparency and solid border
            timeContent.style.backgroundColor = categoryColor + '20';
            timeContent.style.borderLeft = `4px solid ${categoryColor}`;
            timeContent.classList.add('has-task');
            
            // Add tooltip with category information
            timeContent.title = `Category: ${categoryName}`;
        }
    } else {
        // Reset to default styling
        timeContent.style.backgroundColor = '';
        timeContent.style.borderLeft = '';
        timeContent.classList.remove('has-task');
        timeContent.title = '';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initAutoSave();
});