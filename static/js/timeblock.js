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

    // Save functionality
    function saveData() {
        const date = document.getElementById('datePicker').value;
        const priorities = [...document.querySelectorAll('.priority-input')].map(input => ({
            content: input.value,
            completed: input.classList.contains('completed')
        }));

        const timeBlocks = [...document.querySelectorAll('.time-block')].map(block => ({
            start_time: block.dataset.time,
            end_time: addMinutes(block.dataset.time, 15),
            task_id: block.querySelector('.task-select').value || null,
            notes: block.querySelector('.task-notes')?.value || '',  // Ensure notes are included
            completed: false
        }));

        const rating = document.querySelector('input[name="rating"]:checked')?.value || 0;
        const brainDump = document.getElementById('brainDump')?.value || '';

        fetch('/api/daily-plan', {
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
        }).catch(error => console.error('Error saving data:', error));
    }

    // Initialize auto-save
    setInterval(saveData, 30000);  // Save every 30 seconds
    document.querySelectorAll('input, textarea, select').forEach(el => {
        el.addEventListener('change', saveData);
    });
});

function addMinutes(time, minutes) {
    const [hours, mins] = time.split(':').map(Number);
    const date = new Date(2000, 0, 1, hours, mins + minutes);
    return date.toTimeString().substring(0, 5);
}