document.addEventListener('DOMContentLoaded', () => {
    const tabStudent = document.getElementById('tab-student');
    const tabFaculty = document.getElementById('tab-faculty');
    const labelUserId = document.getElementById('label-user-id');
    const inputUserId = document.getElementById('user-id');
    const form = document.getElementById('schedule-form');
    const errorMsg = document.getElementById('error-message');
    const submitBtn = document.getElementById('submit-btn');
    const loader = document.getElementById('loader');
    const btnText = submitBtn.querySelector('span');
    
    const card = document.querySelector('.card');
    const resultsSection = document.getElementById('results-section');
    const welcomeText = document.getElementById('welcome-text');
    const scheduleBody = document.getElementById('schedule-body');
    const newSearchBtn = document.getElementById('new-search-btn');
    const noScheduleMsg = document.getElementById('no-schedule-msg');
    const tableContainer = document.querySelector('.table-container');
    const thFaculty = document.getElementById('th-faculty');

    const groupInputContainer = document.getElementById('group-input-container');
    const inputGroupId = document.getElementById('group-id');

    let currentRole = 'student';

    // Days mapping (0=Monday, 4=Friday)
    const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    // Time slots mapping (assuming 8 slots per day, e.g., 8am to 5pm)
    // 0 = 8:00 AM, 1 = 9:00 AM, ... 4 = 1:00 PM (lunch), etc.
    const getSlotTime = (slot) => {
        const hour = 8 + (slot % 8);
        return `${hour > 12 ? hour - 12 : hour}:00 ${hour >= 12 ? 'PM' : 'AM'} - ${hour + 1 > 12 ? (hour + 1) - 12 : hour + 1}:00 ${hour + 1 >= 12 ? 'PM' : 'AM'}`;
    };

    const getDayName = (slot) => {
        const dayIdx = Math.floor(slot / 8);
        return DAYS[dayIdx] || `Day ${dayIdx + 1}`;
    };

    // Tab switching logic
    const switchTab = (role) => {
        currentRole = role;
        errorMsg.classList.add('hidden');
        inputUserId.value = '';
        inputGroupId.value = '';
        
        if (role === 'student') {
            tabStudent.classList.add('active');
            tabFaculty.classList.remove('active');
            labelUserId.textContent = 'Roll Number';
            inputUserId.placeholder = 'e.g., 2512CS01';
            groupInputContainer.style.display = 'none';
            thFaculty.textContent = 'Faculty ID';
        } else {
            tabFaculty.classList.add('active');
            tabStudent.classList.remove('active');
            labelUserId.textContent = 'Faculty ID';
            inputUserId.placeholder = 'e.g., CS015';
            groupInputContainer.style.display = 'none';
            thFaculty.textContent = 'Faculty ID';
        }
    };

    inputUserId.addEventListener('input', () => {
        if (currentRole === 'student') {
            const val = inputUserId.value.trim().toUpperCase();
            if (val.startsWith('25') || val === '') {
                groupInputContainer.style.display = 'block';
            } else {
                groupInputContainer.style.display = 'none';
                inputGroupId.value = '';
            }
        }
    });

    tabStudent.addEventListener('click', () => switchTab('student'));
    tabFaculty.addEventListener('click', () => switchTab('faculty'));

    newSearchBtn.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        card.classList.remove('hidden');
        inputUserId.value = '';
        inputUserId.focus();
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const userId = inputUserId.value.trim();
        const groupId = inputGroupId.value.trim();
        
        if (currentRole === 'faculty' && !userId) {
            errorMsg.textContent = 'Please enter a faculty ID.';
            errorMsg.classList.remove('hidden');
            return;
        }
        
        if (currentRole === 'student') {
            const val = userId.toUpperCase();
            if (val.startsWith('25') || val === '') {
                if (!groupId) {
                    errorMsg.textContent = 'Please enter a group number.';
                    errorMsg.classList.remove('hidden');
                    return;
                }
            } else if (!userId) {
                errorMsg.textContent = 'Please enter your roll number.';
                errorMsg.classList.remove('hidden');
                return;
            }
        }

        // UI Loading state
        errorMsg.classList.add('hidden');
        btnText.style.display = 'none';
        loader.classList.remove('hidden');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/schedule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    role: currentRole,
                    id: userId,
                    group: groupId
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch schedule');
            }

            displaySchedule(data);
        } catch (err) {
            errorMsg.textContent = err.message;
            errorMsg.classList.remove('hidden');
        } finally {
            btnText.style.display = 'inline';
            loader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });

    const displaySchedule = (data) => {
        card.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        if (currentRole === 'student') {
            welcomeText.textContent = `Schedule for ${data.student.name} (${data.student.level})`;
        } else {
            welcomeText.textContent = `Schedule for Professor ${inputUserId.value.trim()}`;
        }

        const schedule = data.schedule;
        scheduleBody.innerHTML = '';

        if (!schedule || schedule.length === 0) {
            tableContainer.classList.add('hidden');
            noScheduleMsg.classList.remove('hidden');
            return;
        }

        tableContainer.classList.remove('hidden');
        noScheduleMsg.classList.add('hidden');

        // Create 5x8 grid (5 days, 8 slots)
        const grid = Array(5).fill(null).map(() => Array(8).fill(null));

        schedule.forEach(event => {
            const dayIdx = Math.floor(event.Start_Slot / 8);
            const slotIdx = event.Start_Slot % 8;
            if (dayIdx >= 0 && dayIdx < 5 && slotIdx >= 0 && slotIdx < 8) {
                grid[dayIdx][slotIdx] = event;
                for (let i = 1; i < event.Duration; i++) {
                    if (slotIdx + i < 8) {
                        grid[dayIdx][slotIdx + i] = 'SPAN';
                    }
                }
            }
        });

        DAYS.forEach((dayName, dayIdx) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<th>${dayName}</th>`;
            
            for (let slot = 0; slot < 8; slot++) {
                // Insert Lunch Break visually before slot 4 (2:00 PM)
                if (slot === 4) {
                    if (dayIdx === 0) {
                        tr.innerHTML += `<td rowspan="5" class="lunch-break-cell"><div class="lunch-text">LUNCH BREAK</div></td>`;
                    }
                }

                const item = grid[dayIdx][slot];
                if (item === 'SPAN') {
                    continue;
                }
                if (!item) {
                    tr.innerHTML += `<td></td>`;
                } else {
                    const colspanAttr = item.Duration > 1 ? ` colspan="${item.Duration}"` : '';
                    const isLab = item.Type === 'LAB';
                    const typeClass = isLab ? 'type-lab' : 'type-lec';
                    const cardClass = isLab ? 'event-card lab-card' : 'event-card';
                    const bottomText = currentRole === 'student' ? item.Fac_ID : item.Groups;
                    
                    tr.innerHTML += `
                        <td${colspanAttr}>
                            <div class="${cardClass}">
                                <div class="event-course">
                                    <span>${item.Course_ID}</span>
                                    <span class="${typeClass}">${item.Type}</span>
                                </div>
                                <div class="event-room">${item.Room_name}</div>
                                <div class="event-bottom">${bottomText}</div>
                            </div>
                        </td>
                    `;
                }
            }
            scheduleBody.appendChild(tr);
        });
    };
});
