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
            const timeBlock = this.closest('.time-block');
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