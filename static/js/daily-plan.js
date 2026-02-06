document.addEventListener('DOMContentLoaded', function() {
    updateWorkHourProgress();

    const ptoInput = document.getElementById('ptoHours');
    if (ptoInput) {
        ptoInput.addEventListener('change', updatePTOHours);
    }

    loadSevenDayStats();
    setupAutoSave();
    setupConflictDetection();
    updateTimeTotals();
    initTimeIndicator();
    initColorCoding();
    initRefreshTotals();
    initBlockControls();
    initRecoveryButtons();
});

function showWorkHourSettings() {
    const datePicker = document.getElementById('datePicker');
    const viewedDate = datePicker ? datePicker.value : '';
    const url = viewedDate ? `/api/work-hour-stats?date=${viewedDate}` : '/api/work-hour-stats';

    fetch(url)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('weeklyGoal').value = data.weekly_goal;
            document.getElementById('monthlyGoal').value = data.monthly_goal;
        }
    })
    .catch(error => {
        console.error('Error fetching work hour settings:', error);
    });

    const modal = new bootstrap.Modal(document.getElementById('workHourSettingsModal'));
    modal.show();
}

function saveWorkHourSettings() {
    const weeklyGoal = document.getElementById('weeklyGoal').value;
    const monthlyGoal = document.getElementById('monthlyGoal').value;

    fetch('/api/work-hour-settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            weekly_goal: parseFloat(weeklyGoal),
            monthly_goal: parseFloat(monthlyGoal)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('weeklyGoalDisplay').textContent = weeklyGoal;
            document.getElementById('monthlyGoalDisplay').textContent = monthlyGoal;
            updateWorkHourProgress();
            bootstrap.Modal.getInstance(document.getElementById('workHourSettingsModal')).hide();
        } else {
            alert('Error saving work hour settings: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error saving work hour settings');
    });
}

function updatePTOHours() {
    const ptoHours = document.getElementById('ptoHours').value;
    document.getElementById('ptoHoursDisplay').textContent = ptoHours + ' hrs';
    if (window.autoSaveData) {
        window.autoSaveData();
    }
}

function updateWorkHourProgress() {
    const datePicker = document.getElementById('datePicker');
    const viewedDate = datePicker ? datePicker.value : '';
    const url = viewedDate ? `/api/work-hour-stats?date=${viewedDate}` : '/api/work-hour-stats';

    fetch(url)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const stats = data.category_stats || {};
            const categories = ['work', 'consulting', 'church', 'personal'];

            if (data.work_week_start && data.work_week_end) {
                const startDate = new Date(data.work_week_start + 'T00:00:00');
                const endDate = new Date(data.work_week_end + 'T00:00:00');
                const dateStr = `(${startDate.toLocaleDateString('en-US', {month: 'short', day: 'numeric'})} - ${endDate.toLocaleDateString('en-US', {month: 'short', day: 'numeric'})})`;
                const workWeekDatesEl = document.getElementById('workWeekDates');
                if (workWeekDatesEl) workWeekDatesEl.textContent = dateStr;
            }

            categories.forEach(cat => {
                const catStats = stats[cat] || { seven_day: 0, thirty_day: 0, work_week: 0, color: '#6c757d' };
                const catName = cat.charAt(0).toUpperCase() + cat.slice(1);

                const sevenDayVal = (catStats.seven_day !== undefined && catStats.seven_day !== null) ? Number(catStats.seven_day) : 0;
                const thirtyDayVal = (catStats.thirty_day !== undefined && catStats.thirty_day !== null) ? Number(catStats.thirty_day) : 0;
                const workWeekVal = (catStats.work_week !== undefined && catStats.work_week !== null) ? Number(catStats.work_week) : 0;
                const color = catStats.color || '#6c757d';

                const workWeekEl = document.getElementById('workWeek' + catName);
                if (workWeekEl) workWeekEl.textContent = workWeekVal.toFixed(1) + ' hrs';
                const workWeekColorEl = document.getElementById('workWeek' + catName + 'Color');
                if (workWeekColorEl) workWeekColorEl.style.color = color;

                const sevenDayEl = document.getElementById('sevenDay' + catName);
                if (sevenDayEl) sevenDayEl.textContent = sevenDayVal.toFixed(1) + ' hrs';
                const sevenDayColorEl = document.getElementById('sevenDay' + catName + 'Color');
                if (sevenDayColorEl) sevenDayColorEl.style.color = color;

                const thirtyDayEl = document.getElementById('thirtyDay' + catName);
                if (thirtyDayEl) thirtyDayEl.textContent = thirtyDayVal.toFixed(1) + ' hrs';
                const thirtyDayColorEl = document.getElementById('thirtyDay' + catName + 'Color');
                if (thirtyDayColorEl) thirtyDayColorEl.style.color = color;
            });

            const workStats = stats.work || { seven_day: 0, thirty_day: 0, color: '#007bff' };
            const sevenDayWork = data.seven_day_work || 0;
            const thirtyDayWork = data.thirty_day_work || 0;
            const weeklyGoal = data.weekly_goal || 32;
            const monthlyGoal = data.monthly_goal || 140;

            const weeklyProgress = (sevenDayWork / weeklyGoal) * 100;
            const workProgressBar = document.getElementById('workProgressBar');
            if (workProgressBar) {
                workProgressBar.style.width = Math.min(weeklyProgress, 100) + '%';
                workProgressBar.style.backgroundColor = workStats.color || '#007bff';
                workProgressBar.setAttribute('aria-valuemax', weeklyGoal);
            }

            const monthlyProgress = (thirtyDayWork / monthlyGoal) * 100;
            const monthlyProgressBar = document.getElementById('monthlyWorkProgressBar');
            if (monthlyProgressBar) {
                monthlyProgressBar.style.width = Math.min(monthlyProgress, 100) + '%';
                monthlyProgressBar.style.backgroundColor = workStats.color || '#007bff';
                monthlyProgressBar.setAttribute('aria-valuemax', monthlyGoal);
            }

            const weeklyGoalEl = document.getElementById('weeklyGoalDisplay');
            if (weeklyGoalEl) weeklyGoalEl.textContent = weeklyGoal;
            const monthlyGoalEl = document.getElementById('monthlyGoalDisplay');
            if (monthlyGoalEl) monthlyGoalEl.textContent = monthlyGoal;
        }
    })
    .catch(error => {
        console.error('Error updating work hour progress:', error);
    });
}

function initTimeIndicator() {
    setInterval(updateTimeIndicator, 300000);
    updateTimeIndicator();

    document.getElementById('datePicker').addEventListener('change', updateTimeIndicator);
    document.getElementById('prevDay').addEventListener('click', updateTimeIndicator);
    document.getElementById('nextDay').addEventListener('click', updateTimeIndicator);
    document.getElementById('todayBtn').addEventListener('click', updateTimeIndicator);
}

function updateTimeIndicator() {
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();

    const existingIndicator = document.querySelector('.time-indicator');
    if (existingIndicator) {
        existingIndicator.remove();
    }

    const currentDate = new Date().toISOString().split('T')[0];
    const selectedDate = document.getElementById('datePicker').value;
    if (currentDate !== selectedDate) {
        return;
    }

    const timeString = `${currentHour.toString().padStart(2, '0')}:${currentMinute.toString().padStart(2, '0')}`;
    const timeBlocks = document.querySelectorAll('.time-block');

    for (let i = 0; i < timeBlocks.length; i++) {
        const block = timeBlocks[i];
        const blockTime = block.dataset.time;

        if (blockTime <= timeString) {
            const nextBlock = timeBlocks[i + 1];
            if (!nextBlock || nextBlock.dataset.time > timeString) {
                const blockTop = block.offsetTop;
                const blockHeight = block.offsetHeight;
                const minutes = currentMinute % 15;
                const percentage = (minutes / 15);

                const indicator = document.createElement('div');
                indicator.className = 'time-indicator';

                const column = block.closest('.time-block-column');
                const position = blockTop + (blockHeight * percentage);
                indicator.style.top = `${position}px`;
                indicator.style.width = '100%';

                column.appendChild(indicator);
                break;
            }
        }
    }
}

function initColorCoding() {
    document.querySelectorAll('.task-select').forEach(select => {
        updateTimeBlockColor(select);

        select.addEventListener('change', function() {
            updateTimeBlockColor(this);
        });

        select.addEventListener('dblclick', function() {
            if (this.value) {
                pushTaskDown(this);
            }
        });
    });
}

function updateTimeBlockColor(selectElement) {
    const timeContent = selectElement.closest('.time-content');
    const selectedOption = selectElement.options[selectElement.selectedIndex];

    if (selectedOption && selectedOption.value) {
        const categoryColor = selectedOption.getAttribute('data-category-color');
        const categoryName = selectedOption.getAttribute('data-category-name');

        if (categoryColor) {
            timeContent.style.backgroundColor = categoryColor;
            timeContent.style.borderLeft = `4px solid ${categoryColor}`;
            timeContent.classList.add('has-task');

            timeContent.style.color = '#ffffff';
            const select = timeContent.querySelector('.task-select');
            const notes = timeContent.querySelector('.task-notes');
            if (select) select.style.color = '#ffffff';
            if (notes) {
                notes.style.backgroundColor = 'rgba(255,255,255,0.9)';
                notes.style.color = '#333';
            }

            timeContent.title = `Category: ${categoryName}`;
        }
    } else {
        timeContent.style.backgroundColor = '#f8f9fa';
        timeContent.style.borderLeft = '3px solid #dee2e6';
        timeContent.style.color = '#333';
        timeContent.classList.remove('has-task');

        const select = timeContent.querySelector('.task-select');
        const notes = timeContent.querySelector('.task-notes');
        if (select) select.style.color = '#333';
        if (notes) {
            notes.style.backgroundColor = '#ffffff';
            notes.style.color = '#333';
        }

        timeContent.title = 'Available time slot';
    }
}

function initRefreshTotals() {
    document.getElementById('refreshTotalsBtn').addEventListener('click', function() {
        const button = this;
        const icon = button.querySelector('i');

        button.disabled = true;
        icon.classList.remove('fa-sync-alt');
        icon.classList.add('fa-spinner', 'fa-spin');

        refreshTimeStatistics();
        loadSevenDayStats();

        setTimeout(() => {
            button.disabled = false;
            icon.classList.remove('fa-spinner', 'fa-spin');
            icon.classList.add('fa-sync-alt');
        }, 1000);
    });

    document.getElementById('datePicker').addEventListener('change', () => {
        loadSevenDayStats();
    });
}

let autoSaveInterval;
let lastUpdateCheck = new Date().toISOString();

function setupAutoSave() {
    autoSaveInterval = setInterval(() => {
        autoSaveData();
    }, 120000);

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            autoSaveData();
        }
    });

    window.addEventListener('beforeunload', () => {
        autoSaveData();
    });
}

function addMinutesDP(time, minutes) {
    const [hours, mins] = time.split(':').map(Number);
    const date = new Date(2000, 0, 1, hours, mins + minutes);
    return date.toTimeString().substring(0, 5);
}

let lastConflictWarningTime = 0;
const CONFLICT_WARNING_COOLDOWN = 60 * 60 * 1000;

function setupConflictDetection() {
    setInterval(() => {
        checkForConflicts();
    }, 300000);
}

const MAX_RETRIES = 3;
const BASE_RETRY_DELAY = 2000;

async function autoSaveData() {
    let retries = 0;

    while (retries <= MAX_RETRIES) {
        try {
            const date = document.getElementById('datePicker').value;
            const priorities = [...document.querySelectorAll('.priority-input')].map((input, index) => ({
                content: input.value,
                completed: input.classList.contains('completed'),
                order: index
            })).filter(p => p.content.trim());

            const timeBlocks = [...document.querySelectorAll('.time-block')].map(block => {
                const taskSelect = block.querySelector('.task-select');
                const notesInput = block.querySelector('.task-notes');
                const checkbox = block.querySelector('.time-block-checkbox');

                return {
                    start_time: block.dataset.time,
                    end_time: addMinutesDP(block.dataset.time, 15),
                    task_id: taskSelect?.value || null,
                    notes: notesInput?.value || '',
                    completed: checkbox?.checked || false
                };
            });

            const brainDump = document.getElementById('brainDump').value;
            const ratingInputs = document.querySelectorAll('input[name="rating"]:checked');
            const productivityRating = ratingInputs.length > 0 ? parseInt(ratingInputs[0].value) : null;

            const response = await fetch('/api/daily-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date: date,
                    priorities: priorities,
                    time_blocks: timeBlocks,
                    brain_dump: brainDump,
                    productivity_rating: productivityRating,
                    last_update_check: lastUpdateCheck,
                    auto_save: true
                })
            });

            const result = await response.json();

            if (result.success) {
                lastUpdateCheck = new Date().toISOString();
                showAutoSaveIndicator('✓ Auto-saved');
                return;
            } else if (result.conflict) {
                showConflictWarning();
                return;
            } else {
                throw new Error(result.error || 'Save failed');
            }
        } catch (error) {
            retries++;
            if (retries > MAX_RETRIES) {
                console.error('Auto-save failed after retries:', error);
                showAutoSaveIndicator('⚠ Save failed', 'warning');
                return;
            }
            const delay = BASE_RETRY_DELAY * Math.pow(2, retries - 1);
            console.warn(`Auto-save retry ${retries}/${MAX_RETRIES} in ${delay}ms`);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
}
window.autoSaveData = autoSaveData;

async function checkForConflicts() {
    try {
        const now = Date.now();
        if (now - lastConflictWarningTime < CONFLICT_WARNING_COOLDOWN) {
            return;
        }

        const date = document.getElementById('datePicker').value;
        const response = await fetch(`/api/daily-plan/backup?date=${date}`);
        const result = await response.json();

        if (result.success && result.backup_data.length > 0) {
            const latestPlan = result.backup_data[0];
            const serverUpdate = new Date(latestPlan.updated_at);
            const lastCheck = new Date(lastUpdateCheck);

            const timeDifference = serverUpdate.getTime() - lastCheck.getTime();
            if (timeDifference > 300000) {
                showConflictWarning();
                lastConflictWarningTime = now;
            }
        }
    } catch (error) {
        console.error('Conflict check failed:', error);
    }
}

function showAutoSaveIndicator(message, type = 'success') {
    let indicator = document.getElementById('autoSaveIndicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'autoSaveIndicator';
        indicator.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 8px 12px;
            border-radius: 4px;
            color: white;
            font-size: 12px;
            z-index: 1000;
            transition: opacity 0.3s;
        `;
        document.body.appendChild(indicator);
    }

    indicator.textContent = message;
    indicator.style.backgroundColor = type === 'warning' ? '#ffc107' : '#28a745';
    indicator.style.opacity = '1';

    setTimeout(() => {
        indicator.style.opacity = '0';
    }, 3000);
}

function showConflictWarning() {
    if (document.getElementById('conflictWarning')) {
        return;
    }

    const warning = document.createElement('div');
    warning.id = 'conflictWarning';
    warning.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ffc107;
        color: #333;
        padding: 15px;
        border-radius: 8px;
        z-index: 2000;
        max-width: 350px;
        text-align: left;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        border-left: 4px solid #ff9800;
    `;
    warning.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-exclamation-triangle" style="color: #ff9800;"></i>
            <div style="flex: 1;">
                <strong>Data Updated Elsewhere</strong>
                <div style="font-size: 13px; margin-top: 4px;">
                    Changes detected from another session. Consider refreshing to see latest data.
                </div>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: none; 
                border: none; 
                font-size: 18px; 
                cursor: pointer; 
                color: #666;
                padding: 0;
                margin-left: 10px;
            ">&times;</button>
        </div>
        <div style="margin-top: 10px; display: flex; gap: 8px;">
            <button onclick="location.reload()" style="
                background: #ff9800; 
                color: white; 
                border: none; 
                padding: 6px 12px; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 12px;
            ">Refresh</button>
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: #6c757d; 
                color: white; 
                border: none; 
                padding: 6px 12px; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 12px;
            ">Continue</button>
        </div>
    `;

    document.body.appendChild(warning);

    setTimeout(() => {
        if (warning.parentElement) {
            warning.remove();
        }
    }, 15000);
}

function initRecoveryButtons() {
    document.getElementById('recoverDataBtn').addEventListener('click', async function() {
        const date = document.getElementById('datePicker').value;

        try {
            const response = await fetch(`/api/daily-plan/backup?date=${date}`);
            const result = await response.json();

            if (result.success && result.backup_data.length > 0) {
                showRecoveryModal(result.backup_data);
            } else {
                alert('No backup data found for recovery.');
            }
        } catch (error) {
            console.error('Recovery failed:', error);
            alert('Failed to retrieve backup data.');
        }
    });

    document.getElementById('restoreTodayBtn').addEventListener('click', async function() {
        if (confirm('Restore your daily plan from earlier today? This will overwrite any current changes.')) {
            try {
                const response = await fetch('/api/restore-today-plan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                const result = await response.json();

                if (result.success) {
                    alert(`Restored your plan with ${result.priorities_count} priorities and ${result.time_blocks_count} scheduled blocks. Refreshing page...`);
                    location.reload();
                } else {
                    alert('No previous data found to restore for today.');
                }
            } catch (error) {
                console.error('Restore failed:', error);
                alert('Failed to restore today\'s plan.');
            }
        }
    });
}

function showRecoveryModal(backupData) {
    window.recoveryBackupData = backupData;

    let recoveryOptions = '';
    backupData.forEach((backup, index) => {
        const date = new Date(backup.updated_at).toLocaleString();
        const priorityCount = backup.priorities.length;
        const blockCount = backup.time_blocks.filter(b => b.task_id).length;

        recoveryOptions += `
            <div class="list-group-item list-group-item-action" style="cursor: pointer;" onclick="restoreBackup(${index})">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${backup.date}</h6>
                    <small>${date}</small>
                </div>
                <p class="mb-1">${priorityCount} priorities, ${blockCount} scheduled blocks</p>
                ${backup.brain_dump ? `<small>Brain dump: ${backup.brain_dump.substring(0, 50)}...</small>` : ''}
            </div>
        `;
    });

    document.getElementById('recoveryModalBody').innerHTML = `
        <p>Select a backup to restore:</p>
        <div class="list-group">${recoveryOptions}</div>
    `;

    const modal = new bootstrap.Modal(document.getElementById('recoveryModal'));
    modal.show();
}

async function restoreBackup(backupIndex) {
    const backup = window.recoveryBackupData[backupIndex];

    if (confirm(`Restore data from ${backup.date} (${new Date(backup.updated_at).toLocaleString()})? This will overwrite current data.`)) {
        try {
            const priorityContainer = document.querySelector('.priorities-list');
            if (priorityContainer) {
                priorityContainer.innerHTML = '';

                backup.priorities.forEach(priority => {
                    const priorityDiv = document.createElement('div');
                    priorityDiv.className = 'input-group mb-2';
                    priorityDiv.innerHTML = `
                        <input type="text" class="form-control priority-input ${priority.completed ? 'completed' : ''}" 
                               value="${priority.content}" placeholder="Priority">
                        <button class="btn btn-outline-success complete-priority" type="button">✓</button>
                        <button class="btn btn-outline-danger remove-priority" type="button">×</button>
                    `;
                    priorityContainer.appendChild(priorityDiv);
                });
            }

            backup.time_blocks.forEach(block => {
                const timeBlock = document.querySelector(`[data-time="${block.start_time}"]`);
                if (timeBlock) {
                    const select = timeBlock.querySelector('.task-select');
                    const notesInput = timeBlock.querySelector('.task-notes');

                    if (block.task_id) {
                        select.value = block.task_id;
                        updateTimeBlockColor(select);
                        notesInput.style.display = 'inline-block';
                    }

                    if (block.notes) {
                        notesInput.value = block.notes;
                    }
                }
            });

            if (backup.brain_dump) {
                document.getElementById('brainDump').value = backup.brain_dump;
            }

            if (backup.productivity_rating) {
                const ratingInput = document.querySelector(`input[name="rating"][value="${backup.productivity_rating}"]`);
                if (ratingInput) {
                    ratingInput.checked = true;
                }
            }

            const recoveryModalEl = document.getElementById('recoveryModal');
            const recoveryModalInstance = bootstrap.Modal.getInstance(recoveryModalEl);
            if (recoveryModalInstance) recoveryModalInstance.hide();

            await autoSaveData();

            alert(`Data restored from ${backup.date}. Your plan has been automatically saved.`);

        } catch (error) {
            console.error('Restore failed:', error);
            alert('Failed to restore backup data.');
        }
    }
}

async function loadSevenDayStats() {
    try {
        const date = document.getElementById('datePicker').value;
        const response = await fetch(`/api/seven-day-stats?date=${date}`);
        const data = await response.json();

        if (data.success) {
            document.getElementById('sevenDayTotal').textContent = `${data.total_hours} hrs`;
            document.getElementById('sevenDayWork').textContent = `${data.work_hours} hrs`;

            const progressBar = document.getElementById('workProgressBar');
            progressBar.style.width = `${data.work_progress_percentage}%`;
            progressBar.setAttribute('aria-valuenow', data.work_hours);

            progressBar.className = 'progress-bar';
            if (data.work_progress_percentage >= 100) {
                progressBar.classList.add('bg-success');
            } else if (data.work_progress_percentage >= 75) {
                progressBar.classList.add('bg-warning');
            } else {
                progressBar.classList.add('bg-primary');
            }

        } else {
            console.error('Failed to load 7-day stats:', data.error);
            document.getElementById('sevenDayTotal').textContent = 'Error';
            document.getElementById('sevenDayWork').textContent = 'Error';
        }
    } catch (error) {
        console.error('Error loading 7-day stats:', error);
        document.getElementById('sevenDayTotal').textContent = 'Error';
        document.getElementById('sevenDayWork').textContent = 'Error';
    }
}

function refreshTimeStatistics() {
    const categoryStats = {};
    let totalMinutes = 0;

    document.querySelectorAll('.time-block').forEach(block => {
        const select = block.querySelector('.task-select');
        if (select && select.value) {
            const selectedOption = select.options[select.selectedIndex];
            const categoryName = selectedOption.getAttribute('data-category-name');
            const categoryColor = selectedOption.getAttribute('data-category-color');

            if (categoryName && categoryColor) {
                const minutes = 15;
                totalMinutes += minutes;

                if (!categoryStats[categoryName]) {
                    categoryStats[categoryName] = {
                        name: categoryName,
                        color: categoryColor,
                        minutes: 0
                    };
                }
                categoryStats[categoryName].minutes += minutes;
            }
        }
    });

    updateStatisticsDisplay(categoryStats, totalMinutes);
}

function initBlockControls() {
    const addEarlierBtn = document.querySelector('.add-earlier-blocks');
    if (addEarlierBtn) {
        addEarlierBtn.addEventListener('click', function() {
            const firstBlock = document.querySelector('.time-block');
            if (firstBlock) {
                const currentTime = firstBlock.dataset.time;
                const [hours, minutes] = currentTime.split(':').map(Number);

                let newMinutes = minutes - 15;
                let newHours = hours;

                if (newMinutes < 0) {
                    newMinutes = 45;
                    newHours--;
                }

                if (newHours >= 0) {
                    const newTimeString = `${String(newHours).padStart(2, '0')}:${String(newMinutes).padStart(2, '0')}`;
                    const newBlock = firstBlock.cloneNode(true);
                    newBlock.dataset.time = newTimeString;
                    newBlock.querySelector('.time-label').textContent = newTimeString;
                    const select = newBlock.querySelector('.task-select');
                    select.value = '';
                    firstBlock.parentNode.insertBefore(newBlock, firstBlock);
                    initializeTimeBlock(newBlock);
                }
            }
        });
    }

    const addLaterBtn = document.querySelector('.add-later-blocks');
    if (addLaterBtn) {
        addLaterBtn.addEventListener('click', function() {
            const dayEndTime = window.userDayEndTime || '16:30';
            const [endHours, endMinutes] = dayEndTime.split(':').map(Number);
            const lastBlock = document.querySelector('.time-block:last-child');
            let nextTime;

            if (lastBlock) {
                const currentTime = lastBlock.dataset.time;
                const [currentHours, currentMinutes] = currentTime.split(':').map(Number);
                const currentTotalMinutes = currentHours * 60 + currentMinutes;
                const endTotalMinutes = endHours * 60 + endMinutes;

                if (currentTotalMinutes < endTotalMinutes) {
                    nextTime = dayEndTime;
                } else {
                    let newMinutes = currentMinutes + 15;
                    let newHours = currentHours;
                    if (newMinutes >= 60) {
                        newMinutes = 0;
                        newHours++;
                    }
                    if (newHours >= 24) return;
                    nextTime = `${String(newHours).padStart(2, '0')}:${String(newMinutes).padStart(2, '0')}`;
                }
            } else {
                nextTime = dayEndTime;
            }

            const newBlock = createTimeBlock(nextTime);
            const afternoonColumn = document.querySelector('.col-md-6:last-child');
            if (afternoonColumn) {
                afternoonColumn.appendChild(newBlock);
            }
        });
    }

    const removeEarlierBtn = document.querySelector('.remove-earlier-blocks');
    if (removeEarlierBtn) {
        removeEarlierBtn.addEventListener('click', function() {
            const firstBlock = document.querySelector('.time-block');
            if (firstBlock) {
                const select = firstBlock.querySelector('.task-select');
                if (select.value) {
                    alert('Cannot remove block with assigned task. Please clear the task first.');
                    return;
                }
                firstBlock.remove();
            }
        });
    }

    const removeLaterBtn = document.querySelector('.remove-later-blocks');
    if (removeLaterBtn) {
        removeLaterBtn.addEventListener('click', function() {
            const lastBlock = document.querySelector('.time-block:last-child');
            if (lastBlock) {
                const select = lastBlock.querySelector('.task-select');
                if (select.value) {
                    alert('Cannot remove block with assigned task. Please clear the task first.');
                    return;
                }
                lastBlock.remove();
            }
        });
    }
}

function createTimeBlock(timeString) {
    const template = document.querySelector('.time-block');
    const newBlock = template.cloneNode(true);

    newBlock.dataset.time = timeString;
    newBlock.querySelector('.time-label').textContent = timeString;

    const select = newBlock.querySelector('.task-select');
    select.value = '';

    const notes = newBlock.querySelector('.task-notes');
    notes.value = '';
    notes.style.display = 'none';

    initializeTimeBlock(newBlock);

    return newBlock;
}

function initializeTimeBlock(block) {
    const select = block.querySelector('.task-select');
    select.addEventListener('change', function() {
        const notesInput = this.parentElement.querySelector('.task-notes');
        notesInput.style.display = this.value ? 'inline-block' : 'none';
        updateTimeBlockColor(this);
    });

    select.addEventListener('dblclick', function() {
        if (this.value) {
            pushTaskDown(this);
        }
    });

    updateTimeBlockColor(select);
}

function pushTaskDown(selectElement) {
    const currentBlock = selectElement.closest('.time-block');
    const allBlocks = Array.from(document.querySelectorAll('.time-block'));
    const currentIndex = allBlocks.indexOf(currentBlock);

    if (currentIndex === -1) return;

    const selectedTask = selectElement.value;
    const selectedOption = selectElement.options[selectElement.selectedIndex];

    if (!selectedTask) return;

    const blocksToFill = prompt(`How many time blocks (15-min each) do you want to fill with "${selectedOption.text}"?`, '4');

    if (!blocksToFill || isNaN(blocksToFill) || blocksToFill < 1) return;

    const numBlocks = parseInt(blocksToFill);

    for (let i = 1; i <= numBlocks && (currentIndex + i) < allBlocks.length; i++) {
        const nextBlock = allBlocks[currentIndex + i];
        const nextSelect = nextBlock.querySelector('.task-select');

        if (!nextSelect.value) {
            nextSelect.value = selectedTask;
            updateTimeBlockColor(nextSelect);

            const notesInput = nextBlock.querySelector('.task-notes');
            notesInput.style.display = 'inline-block';
        }
    }

    const filledBlocks = Math.min(numBlocks, allBlocks.length - currentIndex - 1);
    if (filledBlocks > 0) {
        alert(`Filled ${filledBlocks} time blocks with "${selectedOption.text}"`);
    }
}
