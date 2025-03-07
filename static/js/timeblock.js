// Date navigation functions
function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function navigateToDate(dateStr) {
    window.location.href = `/?date=${dateStr}`;
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date picker with Pacific time
    const datePicker = document.getElementById('datePicker');
    if (datePicker) {
        // Set the timezone for the date picker
        const today = new Date();
        const pacificDate = new Date(today.toLocaleString("en-US", {timeZone: "America/Los_Angeles"}));
        if (!datePicker.value) {
            datePicker.value = pacificDate.toISOString().split('T')[0];
        }

        // Date navigation handlers
        document.getElementById('prevDay')?.addEventListener('click', function() {
            const currentDate = new Date(datePicker.value);
            currentDate.setDate(currentDate.getDate() - 1);
            navigateToDate(formatDate(currentDate));
        });

        document.getElementById('nextDay')?.addEventListener('click', function() {
            const currentDate = new Date(datePicker.value);
            currentDate.setDate(currentDate.getDate() + 1);
            navigateToDate(formatDate(currentDate));
        });

        document.getElementById('todayBtn')?.addEventListener('click', function() {
            const today = new Date();
            const pacificToday = new Date(today.toLocaleString("en-US", {timeZone: "America/Los_Angeles"}));
            navigateToDate(formatDate(pacificToday));
        });

        datePicker.addEventListener('change', function() {
            navigateToDate(this.value);
        });
    }

    // Initialize priorities
    const prioritiesList = document.getElementById('prioritiesList');
    if (prioritiesList) {
        new Sortable(prioritiesList, {
            animation: 150,
            handle: '.priority-input'
        });
    }

    // Initialize Sortable for morning and afternoon columns
    const columns = document.querySelectorAll('.time-block-column');
    columns.forEach(column => {
        new Sortable(column, {
            animation: 150,
            handle: '.drag-handle',
            ghostClass: 'sortable-ghost',
            onEnd: function(evt) {
                const timeBlocks = [...evt.to.querySelectorAll('.time-block')];

                // Update times for all blocks in the column to maintain chronological order
                timeBlocks.forEach((block, index) => {
                    // Get the base time from the column (morning or afternoon)
                    const isMorning = block.closest('.time-block-column').querySelector('h6').textContent === 'Morning';
                    const baseHour = isMorning ? 6 : 12;

                    // Calculate new time based on position
                    const blocksPerHour = 4; // 15-minute intervals
                    const hour = Math.floor(baseHour + (index / blocksPerHour));
                    const minute = (index % blocksPerHour) * 15;
                    const newTime = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;

                    // Update the block's time label and dataset
                    block.dataset.time = newTime;
                    block.querySelector('.time-label').textContent = newTime;
                });

                // Save the updated order and times
                saveData();
            }
        });
    });

    // Add copy up/down functionality
    document.addEventListener('click', function(e) {
        const copyUpBtn = e.target.closest('.copy-up');
        const copyDownBtn = e.target.closest('.copy-down');

        if (copyUpBtn || copyDownBtn) {
            const timeBlock = e.target.closest('.time-block');
            const select = timeBlock.querySelector('.task-select');
            const direction = copyUpBtn ? 'up' : 'down';

            if (select.value) {
                const targetBlock = direction === 'up'
                    ? timeBlock.previousElementSibling
                    : timeBlock.nextElementSibling;

                if (targetBlock) {
                    const targetSelect = targetBlock.querySelector('.task-select');
                    const selectedOption = select.options[select.selectedIndex];
                    targetSelect.value = select.value;

                    // Update visual style
                    const timeContent = targetSelect.closest('.time-content');
                    timeContent.classList.add('has-task');
                    timeContent.style.borderLeftColor = selectedOption.dataset.categoryColor;

                    // Copy notes as well
                    const sourceNotes = timeBlock.querySelector('.task-notes').value;
                    const targetNotes = targetBlock.querySelector('.task-notes');
                    targetNotes.value = sourceNotes;
                    targetNotes.style.display = 'inline-block';

                    // Save changes
                    saveData();
                }
            }
        }
    });

    // Initialize task colors for existing selections
    document.querySelectorAll('.task-select').forEach(select => {
        if (select.value) {
            const selectedOption = select.options[select.selectedIndex];
            const categoryColor = selectedOption.dataset.categoryColor;
            const timeContent = select.closest('.time-content');
            if (categoryColor) {
                timeContent.classList.add('has-task');
                timeContent.style.borderLeftColor = categoryColor;
            }
        }
    });

    // Initialize checkboxes
    document.querySelectorAll('.priority-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const input = this.closest('.input-group').querySelector('.priority-input');
            input.classList.toggle('completed', this.checked);
            saveData();
        });
    });

    // Handle task selection changes
    document.querySelectorAll('.task-select').forEach(select => {
        select.addEventListener('change', function() {
            if (this.value === 'new') {
                // Reset form
                document.getElementById('quickTaskForm').reset();
                // Store the select element that triggered the modal
                window.activeTimeBlockSelect = this;
                // Show modal
                new bootstrap.Modal(document.getElementById('addTaskModal')).show();
                return;
            }

            const timeContent = this.closest('.time-content');
            const notesInput = timeContent.querySelector('.task-notes');

            if (this.value) {
                const selectedOption = this.options[this.selectedIndex];
                const categoryColor = selectedOption.dataset.categoryColor;
                timeContent.classList.add('has-task');
                timeContent.style.borderLeftColor = categoryColor;
                notesInput.style.display = 'inline-block';
            } else {
                timeContent.classList.remove('has-task');
                timeContent.style.borderLeftColor = '';
                notesInput.style.display = 'none';
                notesInput.value = '';
            }

            saveData();
        });
    });

    // Add real-time notes update handling
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('task-notes')) {
            saveData();  // Save immediately when notes are updated
        }
    });

    // Handle quick task creation
    document.getElementById('saveQuickTask')?.addEventListener('click', function() {
        const taskTitle = document.getElementById('taskTitle');
        const taskDescription = document.getElementById('taskDescription');
        const taskCategory = document.getElementById('taskCategory');

        if (!taskTitle || !taskTitle.value || !taskCategory || !taskCategory.value) return;

        fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: taskTitle.value,
                description: taskDescription?.value || '',
                category_id: taskCategory.value
            })
        })
            .then(response => response.json())
            .then(task => {
                // Add the new task to all task select dropdowns
                document.querySelectorAll('.task-select').forEach(select => {
                    const categoryName = taskCategory.options[taskCategory.selectedIndex].text;
                    const optgroup = select.querySelector(`optgroup[label="${categoryName}"]`);
                    const categoryColor = optgroup.dataset.color;

                    if (optgroup) {
                        const option = document.createElement('option');
                        option.value = task.id;
                        option.textContent = task.title;
                        option.dataset.categoryColor = categoryColor;
                        optgroup.appendChild(option);
                    }
                });

                // Set the newly created task as the selected option
                if (window.activeTimeBlockSelect) {
                    const timeContent = window.activeTimeBlockSelect.closest('.time-content');
                    window.activeTimeBlockSelect.value = task.id;
                    const categoryColor = taskCategory.options[taskCategory.selectedIndex].parentElement.dataset.color;
                    timeContent.classList.add('has-task');
                    timeContent.style.borderLeftColor = categoryColor;
                    window.activeTimeBlockSelect = null;
                }

                // Hide modal
                bootstrap.Modal.getInstance(document.getElementById('addTaskModal')).hide();

                // Save the updated time block data
                saveData();
            });
    });

    // Handle close day functionality
    document.getElementById('closeDay')?.addEventListener('click', async function() {
        const currentDate = document.getElementById('datePicker').value;
        const priorities = [...document.querySelectorAll('.priority-input')].map(input => ({
            content: input.value,
            completed: input.classList.contains('completed')
        }));

        // Get the next day's date
        const nextDate = new Date(currentDate);
        nextDate.setDate(nextDate.getDate() + 1);
        const nextDateStr = nextDate.toISOString().split('T')[0];

        try {
            // First, save current day's data
            await saveData();

            // Then create next day's plan with carried over priorities
            const incompletePriorities = priorities.filter(p => !p.completed && p.content.trim());

            // Prepare data for the next day
            const nextDayData = {
                date: nextDateStr,
                priorities: incompletePriorities,
                time_blocks: [],
                productivity_rating: 0,
                brain_dump: ''
            };

            // Save the next day's data
            const response = await fetch('/api/daily-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(nextDayData)
            });

            if (response.ok) {
                // Navigate to the next day
                window.location.href = `/?date=${nextDateStr}`;
            } else {
                throw new Error('Failed to create next day\'s plan');
            }
        } catch (error) {
            console.error('Error closing day:', error);
            alert('Failed to close day and create next day\'s plan. Please try again.');
        }
    });

    // Add Last Saved display
    const lastSavedDisplay = document.createElement('p');
    lastSavedDisplay.id = 'lastSaved';
    lastSavedDisplay.style.marginTop = '10px';
    lastSavedDisplay.style.fontSize = '14px';
    lastSavedDisplay.style.color = 'gray';
    lastSavedDisplay.textContent = 'Last saved: Never';

    // Add Save button
    const saveButton = document.createElement('button');
    saveButton.id = 'saveButton';
    saveButton.className = 'btn btn-primary';
    saveButton.textContent = 'Save';

    // Add template management UI elements
    const templateControls = document.createElement('div');
    templateControls.className = 'template-controls mt-3 mb-3';
    templateControls.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="input-group">
                    <input type="text" id="templateName" class="form-control" placeholder="Template Name">
                    <button id="saveTemplateBtn" class="btn btn-success">Save as Template</button>
                </div>
            </div>
            <div class="col-md-6">
                <div class="input-group">
                    <select id="templateSelect" class="form-control">
                        <option value="">Select a Template</option>
                    </select>
                    <button id="applyTemplateBtn" class="btn btn-primary">Apply Template</button>
                    <button id="deleteTemplateBtn" class="btn btn-danger">Delete</button>
                </div>
            </div>
        </div>
    `;

    // Insert elements into the DOM
    const container = document.querySelector('.container');
    container.insertBefore(templateControls, lastSavedDisplay);
    container.insertBefore(saveButton, templateControls);
    container.insertBefore(lastSavedDisplay, saveButton);

    // Save button click handler
    saveButton.addEventListener('click', async function() {
        try {
            await saveData();
            updateLastSavedTime();
        } catch (error) {
            console.error('Error saving data:', error);
            alert('Failed to save. Please try again.');
        }
    });


    // Save functionality
    async function saveData() {
        const date = document.getElementById('datePicker').value;
        const priorities = [...document.querySelectorAll('.priority-input')].map(input => ({
            content: input.value,
            completed: input.classList.contains('completed')
        }));

        const timeBlocks = [...document.querySelectorAll('.time-block')].map(block => ({
            start_time: block.dataset.time,
            end_time: addMinutes(block.dataset.time, 15),
            task_id: block.querySelector('.task-select').value || null,
            notes: block.querySelector('.task-notes')?.value || '',
            completed: block.querySelector('.time-block-checkbox')?.checked || false
        }));

        const rating = document.querySelector('input[name="rating"]:checked')?.value || 0;
        const brainDump = document.getElementById('brainDump')?.value || '';

        try {
            const response = await fetch('/api/daily-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date,
                    priorities,
                    time_blocks: timeBlocks,
                    productivity_rating: rating,
                    brain_dump: brainDump
                })
            });

            if (!response.ok) {
                throw new Error('Failed to save data');
            }

            const result = await response.json();
            if (result.status === 'success') {
                updateLastSavedTime();
            }

            return result;
        } catch (error) {
            console.error('Error saving data:', error);
            throw error;
        }
    }

    function updateLastSavedTime() {
        const now = new Date();
        document.getElementById('lastSaved').textContent =
            `Last saved: ${now.toLocaleTimeString()}`;
    }

    // Auto-save setup
    let autoSaveTimeout;
    const AUTO_SAVE_DELAY = 2000; // 2 seconds delay after last change

    function triggerAutoSave() {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(async () => {
            try {
                await saveData();
            } catch (error) {
                console.error('Auto-save failed:', error);
            }
        }, AUTO_SAVE_DELAY);
    }

    // Add auto-save triggers to all interactive elements
    document.querySelectorAll('input, textarea, select').forEach(el => {
        el.addEventListener('change', triggerAutoSave);
        if (el.tagName.toLowerCase() === 'textarea' ||
            (el.tagName.toLowerCase() === 'input' && el.type === 'text')) {
            el.addEventListener('input', triggerAutoSave);
        }
    });

    // Backup auto-save every 30 seconds
    setInterval(async () => {
        try {
            await saveData();
        } catch (error) {
            console.error('Periodic auto-save failed:', error);
        }
    }, 30000);

    // Load existing templates
    async function loadTemplates() {
        try {
            const response = await fetch('/api/templates');
            const templates = await response.json();
            const templateSelect = document.getElementById('templateSelect');

            // Clear existing options except the placeholder
            while (templateSelect.options.length > 1) {
                templateSelect.remove(1);
            }

            // Add templates to select
            templates.forEach(template => {
                const option = document.createElement('option');
                option.value = template.id;
                option.textContent = template.name;
                templateSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    }

    // Initial load of templates
    loadTemplates();

    // Save template handler
    document.getElementById('saveTemplateBtn').addEventListener('click', async function() {
        const templateName = document.getElementById('templateName').value;
        if (!templateName) {
            alert('Please enter a template name');
            return;
        }

        try {
            const data = {
                name: templateName,
                priorities: [...document.querySelectorAll('.priority-input')].map(input => ({
                    content: input.value,
                    completed: input.classList.contains('completed')
                })),
                time_blocks: [...document.querySelectorAll('.time-block')].map(block => ({
                    start_time: block.dataset.time,
                    end_time: addMinutes(block.dataset.time, 15),
                    task_id: block.querySelector('.task-select').value || null,
                    notes: block.querySelector('.task-notes')?.value || ''
                }))
            };

            const response = await fetch('/api/templates', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                alert('Template saved successfully!');
                document.getElementById('templateName').value = '';
                await loadTemplates();
            } else {
                throw new Error(result.error || 'Failed to save template');
            }
        } catch (error) {
            console.error('Error saving template:', error);
            alert(error.message || 'Failed to save template. Please try again.');
        }
    });

    // Apply template handler
    document.getElementById('applyTemplateBtn').addEventListener('click', async function() {
        const templateId = document.getElementById('templateSelect').value;
        if (!templateId) {
            alert('Please select a template to apply');
            return;
        }

        if (!confirm('This will replace your current plan. Are you sure?')) {
            return;
        }

        try {
            const response = await fetch('/api/apply-template', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_id: templateId,
                    date: document.getElementById('datePicker').value
                })
            });

            const result = await response.json();

            if (response.ok) {
                alert('Template applied successfully!');
                location.reload();
            } else {
                throw new Error(result.error || 'Failed to apply template');
            }
        } catch (error) {
            console.error('Error applying template:', error);
            alert(error.message || 'Failed to apply template. Please try again.');
        }
    });

    // Delete template handler
    document.getElementById('deleteTemplateBtn').addEventListener('click', async function() {
        const templateSelect = document.getElementById('templateSelect');
        const templateId = templateSelect.value;

        if (!templateId) {
            alert('Please select a template to delete');
            return;
        }

        const templateName = templateSelect.options[templateSelect.selectedIndex].text;
        if (!confirm(`Are you sure you want to delete the template "${templateName}"?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/templates/${templateId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                alert('Template deleted successfully!');
                await loadTemplates();
            } else {
                const result = await response.json();
                throw new Error(result.error || 'Failed to delete template');
            }
        } catch (error) {
            console.error('Error deleting template:', error);
            alert(error.message || 'Failed to delete template. Please try again.');
        }
    });
});

function addMinutes(time, minutes) {
    const [hours, mins] = time.split(':').map(Number);
    const date = new Date(2000, 0, 1, hours, mins + minutes);
    return date.toTimeString().substring(0, 5);
}