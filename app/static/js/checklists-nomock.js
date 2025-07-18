document.addEventListener('DOMContentLoaded', function() {
    // --- MOCK DATA & STATE ---
    let events = [];
    let checklists = [];

    let mockEvents = [
        { id: 1, name: 'Свадьба Ивановых', date: '2024-08-15' },
        { id: 2, name: 'Юбилей Петрова', date: '2024-09-20' },
        { id: 3, name: 'Конференция "WebDev 2024"', date: '2024-11-01' },
    ];
    let mockChecklists = [
        {
            id: 1,
            name: 'Подготовка к свадьбе',
            eventId: 1,
            deadline: '2024-08-10',
            items: [
                { id: 1, text: 'Заказать торт', completed: true },
                { id: 2, text: 'Выбрать фотографа', completed: true },
                { id: 3, text: 'Разослать приглашения', completed: false },
            ]
        },
        {
            id: 2,
            name: 'Организация юбилея',
            eventId: 2,
            deadline: '2024-09-15',
            items: [
                { id: 1, text: 'Арендовать зал', completed: true },
                { id: 2, text: 'Составить меню', completed: true },
                { id: 3, text: 'Найти ведущего', completed: true },
            ]
        },
        {
            id: 3,
            name: 'Подготовка к конференции',
            eventId: 3,
            deadline: '2024-10-25',
            items: [
                { id: 1, text: 'Подготовить доклад', completed: false },
                { id: 2, text: 'Сделать презентацию', completed: false },
            ]
        }
    ];

    // --- DOM ELEMENTS ---
    const checklistList = document.getElementById('checklist-list');
    const addItemBtn = document.getElementById('add-item-btn');
    const emptyState = document.getElementById('empty-state');
    const emptyStateTitle = document.getElementById('empty-state-title');
    const emptyStateText = document.getElementById('empty-state-text');
    const createFirstBtn = document.getElementById('create-first-btn');

    // Filter elements
    const eventFilter = document.getElementById('event-filter');
    const statusFilter = document.getElementById('status-filter');
    const periodFilter = document.getElementById('period-filter');

    // Modal elements
    const modalOverlay = document.getElementById('modal-overlay');
    const modalTitle = document.getElementById('modal-title');
    const itemForm = document.getElementById('item-form');
    const cancelButton = document.getElementById('cancel-button');
    const itemIdInput = document.getElementById('item-id');
    const itemNameInput = document.getElementById('item-name');
    const itemEventInput = document.getElementById('item-event');
    const itemDeadlineInput = document.getElementById('item-deadline');
    const checklistItemsContainer = document.getElementById('checklist-items-container');
    const newChecklistItemTextInput = document.getElementById('new-checklist-item-text');
    const addChecklistItemBtn = document.getElementById('add-checklist-item-btn');
    const userId = document.getElementById('user-id');

    // Action buttons
    const exportBtn = document.getElementById('export-btn');
    const sendToChatBtn = document.getElementById('send-to-chat-btn');

    // Toast element
    const toast = document.getElementById('toast');

    // --- API FUNCTIONS ---

    async function fetchEvents() {
        try {
            const response = await fetch(`api/events?owner_id=${userId}`); // userId должен быть определен
            if (!response.ok) throw new Error('Ошибка загрузки мероприятий');
            events = await response.json();
            return events;
        } catch (error) {
            console.error('Failed to fetch events:', error);
            showToast('Не удалось загрузить мероприятия', 'error');
            return [];
        }
    }

    async function fetchChecklists() {
        try {
            const response = await fetch(`api/checklists?owner_id=${userId}`);
            if (!response.ok) throw new Error('Ошибка загрузки чек-листов');
            checklists = await response.json();
            return checklists;
        } catch (error) {
            console.error('Failed to fetch checklists:', error);
            showToast('Не удалось загрузить чек-листы', 'error');
            return [];
        }
    }

    async function fetchChecklistById(id) {
        try {
            const response = await fetch(`api/checklists/${id}`);
            if (!response.ok) throw new Error('Ошибка загрузки чек-листа');
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch checklist:', error);
            showToast('Не удалось загрузить чек-лист', 'error');
            return null;
        }
    }

    async function saveChecklist(checklistData) {
        try {
            const method = checklistData.id ? 'PUT' : 'POST';
            const url = checklistData.id
                ? `api/checklists/${checklistData.id}`
                : `api/checklists`;

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(checklistData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Ошибка сохранения');
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to save checklist:', error);
            throw error;
        }
    }

    async function deleteChecklist(id) {
        try {
            const response = await fetch(`api/checklists/${id}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Ошибка удаления');
            }

            return true;
        } catch (error) {
            console.error('Failed to delete checklist:', error);
            throw error;
        }
    }

    // --- FUNCTIONS ---

    function handleResize() {
        const addBtnText = document.querySelector('.add-btn-text');
        if (!addBtnText) return;
        if (window.innerWidth <= 600) {
            addBtnText.style.display = 'none';
        } else {
            addBtnText.style.display = 'inline';
        }
    }

    function showToast(message, type = 'success') {
        toast.textContent = message;
        toast.className = `toast show ${type}`;
        setTimeout(() => {
            toast.className = toast.className.replace("show", "");
        }, 3000);
    }

    async function populateEventFilters() {
        try {
            await fetchEvents();
            eventFilter.innerHTML = '<option value="all">Все мероприятия</option>';
            events.forEach(event => {
                const option = document.createElement('option');
                option.value = event.id;
                option.textContent = event.name;
                eventFilter.appendChild(option);
            });
        } catch (error) {
            console.error('Error populating event filters:', error);
        }
    }

    async function populateEventsForSelect() {
        try {
            await fetchEvents();
            itemEventInput.innerHTML = '';
            if (events.length === 0) {
                itemEventInput.innerHTML = '<option value="">Нет доступных мероприятий</option>';
            } else {
                events.forEach(event => {
                    const option = document.createElement('option');
                    option.value = event.id;
                    option.textContent = event.name;
                    itemEventInput.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error populating events select:', error);
        }
    }

    async function renderChecklists() {
        try {
            checklistList.innerHTML = '';
            await fetchChecklists();

            const eventId = eventFilter.value;
            const status = statusFilter.value;
            const period = periodFilter.value;

            let filteredChecklists = [...checklists];

            // Filter by event
            if (eventId !== 'all') {
                filteredChecklists = filteredChecklists.filter(c => c.eventId == eventId);
            }

            // Filter by status
            if (status !== 'all') {
                filteredChecklists = filteredChecklists.filter(c => {
                    const isComplete = c.items.length > 0 && c.items.every(item => item.completed);
                    return status === 'complete' ? isComplete : !isComplete;
                });
            }

            // Filter by period
            if (period !== 'all') {
                const now = new Date();
                const months = parseInt(period);
                const periodStartDate = new Date(now.setMonth(now.getMonth() - months));

                filteredChecklists = filteredChecklists.filter(c => {
                     const deadlineDate = new Date(c.deadline);
                     // We want checklists with deadline in the future but within the period from now
                     const futureLimit = new Date();
                     futureLimit.setMonth(futureLimit.getMonth() + months);
                     return deadlineDate >= new Date() && deadlineDate <= futureLimit;
                });
            }

            if (filteredChecklists.length === 0) {
                emptyState.style.display = 'flex';
                checklistList.style.display = 'none';

                // Update empty state text based on filters
                if (eventId !== 'all' || status !== 'all' || period !== 'all') {
                    emptyStateTitle.textContent = 'Чек-листов не найдено';
                    emptyStateText.textContent = 'Попробуйте изменить параметры фильтрации';
                    createFirstBtn.style.display = 'none';
                } else {
                    for (const checklist of filteredChecklists) {
                        const event = events.find(e => e.id === checklist.eventId);
                    }
                    emptyStateTitle.textContent = 'Чек-листов пока нет';
                    emptyStateText.textContent = 'Создайте новый чек-лист, чтобы начать планирование';
                    createFirstBtn.style.display = 'block';
                }
            } else {
                emptyState.style.display = 'none';
                checklistList.style.display = 'grid';
            } catch (error) {
            console.error('Error rendering checklists:', error);
            showToast('Ошибка загрузки данных', 'error');
        }

        filteredChecklists.forEach(checklist => {
            const card = document.createElement('div');
            card.className = 'checklist-card';
            card.dataset.id = checklist.id;

            const completedCount = checklist.items.filter(i => i.completed).length;
            const totalCount = checklist.items.length;
            const progress = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;
            const event = mockEvents.find(e => e.id === checklist.eventId);
            const deadline = new Date(checklist.deadline).toLocaleDateString('ru-RU');
            const isComplete = completedCount === totalCount && totalCount > 0;

            card.innerHTML = `
                <div class="card-header">
                    <h3>${checklist.name}</h3>
                    <span class="badge ${isComplete ? 'complete' : 'incomplete'}">
                        ${isComplete ? 'Завершено' : 'В работе'}
                    </span>
                </div>
                <div class="card-body">
                    <div class="meta-info">
                        <span class="event-link">${event ? event.name : 'Без мероприятия'}</span>
                        <span class="deadline">До: ${deadline}</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress}%"></div>
                        </div>
                        <span class="progress-text">${completedCount}/${totalCount}</span>
                    </div>
                </div>
                <div class="card-footer">
                    <button class="icon-btn edit-btn" title="Редактировать">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                    </button>
                    <button class="icon-btn delete-btn" title="Удалить">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                </div>
            `;
            checklistList.appendChild(card);
        });
    }

    function renderModalChecklistItems(items) {
        checklistItemsContainer.innerHTML = '';
        if (!items || items.length === 0) {
            checklistItemsContainer.innerHTML = '<p class="no-items-text">Нет пунктов в этом чек-листе.</p>';
            return;
        }

        items.forEach(item => {
            const itemEl = document.createElement('div');
            itemEl.className = 'checklist-item';
            itemEl.dataset.itemId = item.id;
            itemEl.innerHTML = `
                <label>
                    <input type="checkbox" ${item.completed ? 'checked' : ''}>
                    <span class="checkmark"></span>
                    <input type="text" class="item-text" value="${item.text}">
                </label>
                <button type="button" class="delete-item-btn" title="Удалить пункт">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
            `;
            checklistItemsContainer.appendChild(itemEl);
        });
    }

    async function openModal(type, checklistId = null) {
        try {
            itemForm.reset();
            await populateEventsForSelect();

            if (type === 'edit' && checklistId) {
                const checklist = await fetchChecklistById(checklistId);
                if (!checklist) return;

                modalTitle.textContent = 'Редактировать чек-лист';
                itemIdInput.value = checklist.id;
                itemNameInput.value = checklist.name;
                itemEventInput.value = checklist.eventId;
                itemDeadlineInput.value = checklist.deadline;
                renderModalChecklistItems(checklist.items);
            } else {
                modalTitle.textContent = 'Создать чек-лист';
                itemIdInput.value = '';
                itemDeadlineInput.valueAsDate = new Date();
                renderModalChecklistItems([]);
            }

            modalOverlay.style.display = 'flex';
            setTimeout(() => modalOverlay.classList.add('visible'), 10);
        } catch (error) {
            console.error('Error opening modal:', error);
            showToast('Ошибка загрузки данных', 'error');
        }
    }

    function closeModal() {
        modalOverlay.classList.remove('visible');
        setTimeout(() => modalOverlay.style.display = 'none', 300);
    }

    function exportChecklists() {
        // Simple export to console for demo
        console.log('Exporting checklists:', mockChecklists);
        showToast('Чек-листы экспортированы (см. консоль)', 'info');
    }

    function sendToChat() {
        // Simple chat send simulation
        showToast('Чек-лист отправлен в чат', 'info');
    }

    // --- EVENT LISTENERS ---
    [eventFilter, statusFilter, periodFilter].forEach(filter => {
        filter.addEventListener('change', renderChecklists);
    });

    addItemBtn.addEventListener('click', () => {
        openModal('add');
    });

    createFirstBtn.addEventListener('click', () => {
        openModal('add');
    });

    cancelButton.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            closeModal();
        }
    });

    checklistList.addEventListener('click', (e) => {
        const card = e.target.closest('.checklist-card');
        if (!card) return;
        const checklistId = parseInt(card.dataset.id);

        if (e.target.closest('.edit-btn')) {
            openModal('edit', checklistId);
        }

        if (e.target.closest('.delete-btn')) {
            if (confirm('Вы уверены, что хотите удалить этот чек-лист?')) {
                mockChecklists = mockChecklists.filter(c => c.id !== checklistId);
                renderChecklists();
                showToast('Чек-лист удален', 'error');
            }
        }
    });

    itemForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = itemIdInput.value ? parseInt(itemIdInput.value) : null;
        const checklistData = {
            name: itemNameInput.value.trim(),
            event_id: parseInt(itemEventInput.value),
            deadline: itemDeadlineInput.value,
            items: getChecklistItemsFromModal(),
            owner_id: userId
        };

        try {
            const savedChecklist = await saveChecklist(checklistData);
            showToast(id ? 'Чек-лист обновлен!' : 'Чек-лист создан!');
            await renderChecklists();
            closeModal();
        } catch (error) {
            console.error('Error saving checklist:', error);
            showToast(error.message || 'Ошибка сохранения', 'error');
        }
    });

    addChecklistItemBtn.addEventListener('click', () => {
        const text = newChecklistItemTextInput.value.trim();
        if (!text) {
            showToast('Введите название пункта', 'error');
            return;
        }

        const noItemsText = checklistItemsContainer.querySelector('.no-items-text');
        if (noItemsText) {
            noItemsText.remove();
        }

        const newItemId = Date.now(); // Temp ID
        const itemEl = document.createElement('div');
        itemEl.className = 'checklist-item';
        itemEl.dataset.itemId = newItemId;
        itemEl.innerHTML = `
            <label>
                <input type="checkbox">
                <span class="checkmark"></span>
                <input type="text" class="item-text" value="${text}">
            </label>
            <button type="button" class="delete-item-btn" title="Удалить пункт">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
        `;
        checklistItemsContainer.appendChild(itemEl);
        newChecklistItemTextInput.value = '';
        newChecklistItemTextInput.focus();
    });

    checklistItemsContainer.addEventListener('click', (e) => {
        if (e.target.closest('.delete-item-btn')) {
            e.target.closest('.checklist-item').remove();
            if (checklistItemsContainer.children.length === 0) {
                checklistItemsContainer.innerHTML = '<p class="no-items-text">Нет пунктов в этом чек-листе.</p>';
            }
        }
    });

    exportBtn.addEventListener('click', exportChecklists);
    sendToChatBtn.addEventListener('click', sendToChat);

    window.addEventListener('resize', handleResize);

    // --- INITIAL RENDER ---
    populateEventFilters();
    renderChecklists();
    handleResize(); // Initial check on load
});