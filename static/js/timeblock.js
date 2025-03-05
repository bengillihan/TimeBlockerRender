document.addEventListener('DOMContentLoaded', function() {
    // Initialize date picker
    const datePicker = document.getElementById('datePicker');
    datePicker.addEventListener('change', function() {
        window.location.href = `/?date=${this.value}`;
    });

    // Initialize priorities
    const prioritiesList = document.getElementById('prioritiesList');
    new Sortable(prioritiesList, {
        animation: 150,
        handle: '.priority-input'
    });

    // Initialize checkboxes
    document.querySelectorAll('.priority-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const input = this.closest('.input-group').querySelector('.priority-input');
            input.classList.toggle('completed', this.checked);
        });
    });

    // Initialize task selects
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
            saveData();
        });
    });

    // Handle quick task creation
    document.getElementById('saveQuickTask')?.addEventListener('click', function() {
        const title = document.getElementById('taskTitle').value;
        const description = document.getElementById('taskDescription').value;
        const categoryId = document.getElementById('taskCategory').value;

        if (!title || !categoryId) return;

        fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title,
                description,
                category_id: categoryId
            })
        })
        .then(response => response.json())
        .then(task => {
            // Add the new task to all task select dropdowns
            document.querySelectorAll('.task-select').forEach(select => {
                const optgroup = select.querySelector(`optgroup[label="${
                    document.getElementById('taskCategory').options[
                        document.getElementById('taskCategory').selectedIndex
                    ].text
                }"]`);

                if (optgroup) {
                    const option = document.createElement('option');
                    option.value = task.id;
                    option.textContent = task.title;
                    optgroup.appendChild(option);
                }
            });

            // Set the newly created task as the selected option
            if (window.activeTimeBlockSelect) {
                window.activeTimeBlockSelect.value = task.id;
                window.activeTimeBlockSelect = null;
            }

            // Hide modal
            bootstrap.Modal.getInstance(document.getElementById('addTaskModal')).hide();

            // Save the updated time block data
            saveData();
        });
    });

    function setupAutoSave() {
        const saveData = () => {
            const date = document.getElementById('datePicker').value;
            const priorities = [...document.querySelectorAll('.priority-input')].map(input => ({
                content: input.value,
                completed: input.classList.contains('completed')
            }));

            const timeBlocks = [...document.querySelectorAll('.time-block')].map(block => ({
                start_time: block.dataset.time,
                end_time: addMinutes(block.dataset.time, 15),
                task_id: block.querySelector('.task-select').value || null,
                completed: false
            }));

            const rating = document.querySelector('input[name="rating"]:checked')?.value || 0;
            const brainDump = document.getElementById('brainDump').value;

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
            });
        };

        // Save every 30 seconds and on form changes
        setInterval(saveData, 30000);
        document.querySelectorAll('input, textarea, select').forEach(el => {
            el.addEventListener('change', saveData);
        });
    }

    // Initialize auto-save
    setupAutoSave();
});

function addMinutes(time, minutes) {
    const [hours, mins] = time.split(':').map(Number);
    const date = new Date(2000, 0, 1, hours, mins + minutes);
    return date.toTimeString().substring(0, 5);
}