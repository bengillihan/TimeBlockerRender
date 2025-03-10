let hasUnsavedChanges = false;
let autoSaveTimeout;
const AUTO_SAVE_DELAY = 10000; // 10-second delay after last change

// Update current time display
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
    document.getElementById('currentTime').textContent = timeString;
}

function updateLastSavedTime() {
    const now = new Date();
    document.getElementById('lastSaved').textContent =
        `Last saved: ${now.toLocaleTimeString()}`;
}

// Update time every 5 minutes instead of every minute
setInterval(updateCurrentTime, 300000); // 5 minutes
updateCurrentTime(); // Initial update

function toggleSaveButton(state) {
    document.getElementById('saveButton').disabled = !state;
}

function showSavingIndicator() {
    const lastSaved = document.getElementById('lastSaved');
    lastSaved.innerHTML = 'Saving...';
    lastSaved.style.opacity = 1;
}

function hideSavingIndicator() {
    setTimeout(() => {
        updateLastSavedTime();
        document.getElementById('lastSaved').style.opacity = 0.7;
    }, 1000);
}

function triggerAutoSave() {
    clearTimeout(autoSaveTimeout);
    if (!hasUnsavedChanges) {
        hasUnsavedChanges = true;
        toggleSaveButton(true);
        showSavingIndicator();
    }
    autoSaveTimeout = setTimeout(async () => {
        try {
            await saveData();
            hideSavingIndicator();
            hasUnsavedChanges = false;
            toggleSaveButton(false);
        } catch (error) {
            console.error('Auto-save failed:', error);
        }
    }, AUTO_SAVE_DELAY);
}

// Date navigation functions
function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function navigateToDate(dateStr) {
    window.location.href = `/?date=${dateStr}`;
}

// Add the confirmAndNavigate function
async function confirmAndNavigate(url) {
    if (hasUnsavedChanges) {
        if (confirm('You have unsaved changes. Do you want to save before leaving?')) {
            try {
                await saveData();
            } catch (error) {
                if (!confirm('Save failed. Do you still want to leave?')) {
                    return;
                }
            }
        }
    }
    window.location.href = url;
}

document.addEventListener('DOMContentLoaded', function () {
    // Initialize date picker with Pacific time
    const datePicker = document.getElementById('datePicker');
    let previousDate = datePicker.value; // Store the last confirmed date

    if (datePicker) {
        // Save button click handler
        document.getElementById('saveButton')?.addEventListener('click', async function () {
            try {
                await saveData();
                updateLastSavedTime();
                hasUnsavedChanges = false;
            } catch (error) {
                console.error('Error saving data:', error);
                alert('Failed to save. Please try again.');
            }
        });

        // Add navigation warning for date changes
        datePicker.addEventListener('change', async function (e) {
            e.preventDefault(); // Prevent default form submission
            await confirmAndNavigate(`/?date=${this.value}`);
        });

        // Date navigation handlers with improved navigation
        document.getElementById('prevDay')?.addEventListener('click', async function () {
            const currentDate = new Date(datePicker.value);
            currentDate.setDate(currentDate.getDate() - 1);
            previousDate = formatDate(currentDate);
            await confirmAndNavigate(`/?date=${previousDate}`);
        });

        document.getElementById('nextDay')?.addEventListener('click', async function () {
            const currentDate = new Date(datePicker.value);
            currentDate.setDate(currentDate.getDate() + 1);
            previousDate = formatDate(currentDate);
            await confirmAndNavigate(`/?date=${previousDate}`);
        });

        document.getElementById('todayBtn')?.addEventListener('click', async function () {
            const today = new Date();
            const pacificToday = new Date(today.toLocaleString("en-US", { timeZone: "America/Los_Angeles" }));
            previousDate = formatDate(pacificToday);
            await confirmAndNavigate(`/?date=${previousDate}`);
        });


        const today = new Date();
        const pacificDate = new Date(today.toLocaleString("en-US", { timeZone: "America/Los_Angeles" }));
        if (!datePicker.value) {
            datePicker.value = pacificDate.toISOString().split('T')[0];
        }

        // Date navigation handlers with unsaved changes check

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
                chosenClass: 'sortable-chosen',
                onEnd: function (evt) {
                    updateTimeOrder(evt.to);
                    saveData();
                }
            });
        });

        // Function to update time order after drag and drop
        function updateTimeOrder(column) {
            const timeBlocks = [...column.querySelectorAll('.time-block')];
            const isMorning = column.querySelector('h6').textContent === 'Morning';
            const baseHour = isMorning ? 6 : 12;

            timeBlocks.forEach((block, index) => {
                // Calculate new time based on position
                const blocksPerHour = 4; // 15-minute intervals
                const hour = Math.floor(baseHour + (index / blocksPerHour));
                const minute = (index % blocksPerHour) * 15;
                const newTime = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;

                // Update the block's time label and dataset
                block.dataset.time = newTime;
                block.querySelector('.time-label').textContent = newTime;
            });
        }


        // Add copy up/down functionality
        document.addEventListener('click', function (e) {
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

        // Initialize time block colors
        document.querySelectorAll('.task-select').forEach(select => {
            const timeContent = select.closest('.time-content');
            if (select.value && timeContent) {
                const selectedOption = select.options[select.selectedIndex];
                const categoryColor = selectedOption.dataset.categoryColor;
                if (categoryColor) {
                    timeContent.classList.add('has-task');
                    timeContent.style.borderLeftColor = categoryColor;
                    timeContent.querySelector('.task-notes').style.display = 'inline-block';
                }
            }
        });

        // Handle task selection changes
        document.querySelectorAll('.task-select').forEach(select => {
            select.addEventListener('change', function () {
                const timeContent = this.closest('.time-content');
                const notesInput = timeContent.querySelector('.task-notes');

                if (this.value === "new") {
                    // Store the current select element for later use
                    window.activeTimeBlockSelect = this;

                    // Clear the form
                    document.getElementById('taskTitle').value = '';
                    document.getElementById('taskDescription').value = '';
                    document.getElementById('taskCategory').selectedIndex = 0;

                    // Show the modal
                    const modal = new bootstrap.Modal(document.getElementById('addTaskModal'));
                    modal.show();

                    // Reset the select back to empty until a new task is created
                    this.value = "";
                    return;
                }

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

                saveData(); // Save changes
            });
        });

        // Initialize checkboxes
        document.querySelectorAll('.priority-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', function () {
                const input = this.closest('.input-group').querySelector('.priority-input');
                input.classList.toggle('completed', this.checked);
                saveData();
            });
        });

        // Handle quick task creation
        document.getElementById('saveQuickTask')?.addEventListener('click', function () {
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
        document.getElementById('closeDay')?.addEventListener('click', async function () {
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

                // Then fetch next day's existing data (if any)
                const nextDayResponse = await fetch('/api/daily-plan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        date: nextDateStr,
                        priorities: [], // Initially empty to just check if the day exists
                        time_blocks: [],
                        productivity_rating: 0,
                        brain_dump: ''
                    })
                });

                if (!nextDayResponse.ok) {
                    throw new Error('Failed to check next day\'s data');
                }

                // Get incomplete priorities from current day
                const incompletePriorities = priorities.filter(p => !p.completed && p.content.trim());

                // Prepare data for the next day, keeping any existing data
                const nextDayData = {
                    date: nextDateStr,
                    priorities: incompletePriorities, // Only add incomplete priorities
                    time_blocks: [], // Don't modify existing time blocks
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


        // Update the updateTimeTotals function with correct category tracking
        function updateTimeTotals() {
            const timeBlocks = document.querySelectorAll('.time-block');
            const categoryStats = {};
            let totalMinutes = 0;

            timeBlocks.forEach(block => {
                const select = block.querySelector('.task-select');
                if (select.value && select.value !== 'new') {
                    const selectedOption = select.options[select.selectedIndex];
                    const categoryOptgroup = selectedOption.closest('optgroup');
                    if (categoryOptgroup) {
                        const categoryId = categoryOptgroup.getAttribute('data-category-id');
                        const categoryName = categoryOptgroup.label;
                        const categoryColor = categoryOptgroup.getAttribute('data-color');

                        // Each block is 15 minutes
                        const minutes = 15;
                        totalMinutes += minutes;

                        if (!categoryStats[categoryId]) {
                            categoryStats[categoryId] = {
                                name: categoryName,
                                color: categoryColor,
                                minutes: 0
                            };
                        }
                        categoryStats[categoryId].minutes += minutes;
                    }
                }
            });

            // Update the stats display
            const statsContainer = document.querySelector('.card-body');
            if (statsContainer) {
                // Update total time if it exists
                const totalTimeElement = statsContainer.querySelector('.mb-0');
                if (totalTimeElement) {
                    totalTimeElement.textContent = `${(totalMinutes / 60).toFixed(1)} hrs`;
                }

                // Update individual category stats
                Object.values(categoryStats).forEach(stat => {
                    const categoryElement = statsContainer.querySelector(`[style*="color: ${stat.color}"]`);
                    if (categoryElement) {
                        const timeElement = categoryElement.closest('.mb-3').querySelector('small:last-child');
                        if (timeElement) {
                            timeElement.textContent = `${(stat.minutes / 60).toFixed(1)} hrs`;
                        }
                    }
                });
            }
        }

        // Update the existing saveData function to properly call updateTimeTotals
        async function saveData() {
            const date = document.getElementById('datePicker').value;
            const priorities = [...document.querySelectorAll('.priority-input')].map(input => ({
                content: input.value,
                completed: input.classList.contains('completed')
            }));

            const timeBlocks = [...document.querySelectorAll('.time-block')].map(block => {
                const taskSelect = block.querySelector('.task-select');
                const taskId = taskSelect.value;

                // Only skip if task_id is explicitly "new"
                // Keep blocks that have no task (null/empty) or valid task_id
                if (taskId === "new") {
                    console.log('Skipping block with "new" task_id:', block.dataset.time);
                    return null;
                }

                // Preserve the block if it has a valid task_id or is empty
                const blockData = {
                    start_time: block.dataset.time,
                    end_time: addMinutes(block.dataset.time, 15),
                    task_id: taskId || null, // Convert empty string to null
                    notes: block.querySelector('.task-notes')?.value || '',
                    completed: block.querySelector('.time-block-checkbox')?.checked || false
                };
                console.log('Saving block:', blockData);
                return blockData;
            }).filter(block => block !== null); // Remove only null blocks

            const rating = document.querySelector('input[name="rating"]:checked')?.value || 0;
            const brainDump = document.getElementById('brainDump')?.value || '';

            try {
                const response = await fetch('/api/daily-plan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        date,
                        priorities,
                        time_blocks: timeBlocks,
                        productivity_rating: rating,
                        brain_dump: brainDump
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    console.error('Error saving:', errorData.error);
                    alert(`Save failed: ${errorData.error || "Unknown error"}`);
                    return;
                }

                const result = await response.json();
                if (result.status === 'success') {
                    updateLastSavedTime();
                    hasUnsavedChanges = false;
                    toggleSaveButton(false);
                    updateTimeTotals(); // Call updateTimeTotals after successful save
                }

                return result;
            } catch (error) {
                console.error('Save error:', error);
                alert('Failed to save due to network issues.');
                throw error;
            }
        }

        function updateLastSavedTime() {
            const now = new Date();
            document.getElementById('lastSaved').textContent =
                `Last saved: ${now.toLocaleTimeString()}`;
        }

        // Add auto-save triggers to all interactive elements
        document.querySelectorAll('input, textarea, select').forEach(el => {
            el.addEventListener('change', triggerAutoSave);
            if (el.tagName.toLowerCase() === 'textarea' ||
                (el.tagName.toLowerCase() === 'input' && el.type === 'text')) {
                el.addEventListener('input', triggerAutoSave);
            }
        });

        // Warning before leaving page with unsaved changes
        window.addEventListener('beforeunload', (event) => {
            if (hasUnsavedChanges) {
                event.preventDefault();
                event.returnValue = "You have unsaved changes. Do you really want to leave?";
                return event.returnValue;
            }
        });

        // Backup auto-save every 2 minutes instead of 30 seconds
        setInterval(async () => {
            try {
                await saveData();
            } catch (error) {
                console.error('Periodic auto-save failed:', error);
            }
        }, 120000);

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
        document.getElementById('saveTemplateBtn').addEventListener('click', async function () {
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
        document.getElementById('applyTemplateBtn').addEventListener('click', async function () {
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
        document.getElementById('deleteTemplateBtn').addEventListener('click', async function () {
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
    }

});

function addMinutes(time, minutes) {
    const [hours, mins] = time.split(':').map(Number);
    const date = new Date(2000, 0, 1, hours, mins + minutes);
    return date.toTimeString().substring(0, 5);
}