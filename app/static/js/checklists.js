document.addEventListener('DOMContentLoaded', function() {
    // --- MOCK DATA & STATE ---
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

    // Toast element
    const toast = document.getElementById('toast');

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

    function populateEventFilters() {
        eventFilter.innerHTML = '<option value="all">Все мероприятия</option>';
        mockEvents.forEach(event => {
            const option = document.createElement('option');
            option.value = event.id;
            option.textContent = event.name;
            eventFilter.appendChild(option);
        });
    }

    function populateEventsForSelect() {
        itemEventInput.innerHTML = ''; // Clear previous options
        if (mockEvents.length === 0) {
            itemEventInput.innerHTML = '<option value="">Нет доступных мероприятий</option>';
        } else {
            mockEvents.forEach(event => {
                const option = document.createElement('option');
                option.value = event.id;
                option.textContent = event.name;
                itemEventInput.appendChild(option);
            });
        }
    }

    function renderChecklists() {
        checklistList.innerHTML = '';

        const eventId = eventFilter.value;
        const status = statusFilter.value;
        const period = periodFilter.value;

        let filteredChecklists = [...mockChecklists];

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
        } else {
            emptyState.style.display = 'none';
            checklistList.style.display = 'grid';
        }

        filteredChecklists.forEach(checklist => {
            const card = document.createElement('div');
            card.className = 'item-card';
            card.dataset.id = checklist.id;

            const completedCount = checklist.items.filter(i => i.completed).length;
            const totalCount = checklist.items.length;
            const progress = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;
            const event = mockEvents.find(e => e.id === checklist.eventId);
            const deadline = new Date(checklist.deadline).toLocaleDateString('ru-RU');

            card.innerHTML = `
                <div class="item-details">
                    <h3>${checklist.name}</h3>
                    <p class="checklist-info">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                        <span>${event ? event.name : 'Без мероприятия'}</span>
                    </p>
                    <p class="checklist-info">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                        <span>Дедлайн: ${deadline}</span>
                    </p>
                </div>
                <div class="checklist-progress">
                    <div class="progress-bar">
                        <div class="progress-bar-fill" style="width: ${progress}%"></div>
                    </div>
                    <span class="progress-text">${completedCount} / ${totalCount} выполнено</span>
                </div>
                <div class="item-actions">
                    <button class="edit-btn">Изменить</button>
                    <button class="delete-btn">Удалить</button>
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
            itemEl.className = 'checklist-item-edit';
            itemEl.dataset.itemId = item.id;
            itemEl.innerHTML = `
                <input type="checkbox" id="item-${item.id}" ${item.completed ? 'checked' : ''}>
                <label for="item-${item.id}">${item.text}</label>
                <button type="button" class="delete-item-btn">&times;</button>
            `;
            checklistItemsContainer.appendChild(itemEl);
        });
    }

    function openModal(type, checklistId = null) {
        itemForm.reset();
        populateEventsForSelect();

        if (type === 'edit') {
            const checklist = mockChecklists.find(c => c.id === checklistId);
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
    }

    function closeModal() {
        modalOverlay.classList.remove('visible');
        setTimeout(() => modalOverlay.style.display = 'none', 300);
    }

    // --- EVENT LISTENERS ---
    [eventFilter, statusFilter, periodFilter].forEach(filter => {
        filter.addEventListener('change', renderChecklists);
    });

    addItemBtn.addEventListener('click', () => {
        openModal('add');
    });

    cancelButton.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            closeModal();
        }
    });

    checklistList.addEventListener('click', (e) => {
        const card = e.target.closest('.item-card');
        if (!card) return;
        const checklistId = parseInt(card.dataset.id);

        if (e.target.classList.contains('edit-btn')) {
            openModal('edit', checklistId);
        }

        if (e.target.classList.contains('delete-btn')) {
            if (confirm('Вы уверены, что хотите удалить этот чек-лист?')) {
                mockChecklists = mockChecklists.filter(c => c.id !== checklistId);
                renderChecklists();
                showToast('Чек-лист удален', 'error');
            }
        }
    });

    itemForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = itemIdInput.value ? parseInt(itemIdInput.value) : null;

        // Collect checklist items from modal
        const items = [];
        const itemElements = checklistItemsContainer.querySelectorAll('.checklist-item-edit');
        itemElements.forEach(el => {
            const itemId = parseInt(el.dataset.itemId);
            const text = el.querySelector('label').textContent;
            const completed = el.querySelector('input[type="checkbox"]').checked;
            items.push({ id: itemId, text, completed });
        });

        const newItemData = {
            name: itemNameInput.value,
            eventId: parseInt(itemEventInput.value),
            deadline: itemDeadlineInput.value,
            items,
        };

        if (id) { // Editing existing item
            const itemIndex = mockChecklists.findIndex(c => c.id === id);
            mockChecklists[itemIndex] = { ...mockChecklists[itemIndex], ...newItemData };
            showToast('Чек-лист успешно обновлен!');
        } else { // Adding new item
            const newId = mockChecklists.length > 0 ? Math.max(...mockChecklists.map(e => e.id)) + 1 : 1;
            mockChecklists.push({ id: newId, ...newItemData });
            showToast('Чек-лист успешно добавлен!');
        }

        renderChecklists();
        closeModal();
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
        itemEl.className = 'checklist-item-edit';
        itemEl.dataset.itemId = newItemId;
        itemEl.innerHTML = `
            <input type="checkbox" id="item-${newItemId}">
            <label for="item-${newItemId}">${text}</label>
            <button type="button" class="delete-item-btn">&times;</button>
        `;
        checklistItemsContainer.appendChild(itemEl);
        newChecklistItemTextInput.value = '';
        newChecklistItemTextInput.focus();
    });

    checklistItemsContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-item-btn')) {
            e.target.closest('.checklist-item-edit').remove();
            if (checklistItemsContainer.children.length === 0) {
                checklistItemsContainer.innerHTML = '<p class="no-items-text">Нет пунктов в этом чек-листе.</p>';
            }
        }
    });

    window.addEventListener('resize', handleResize);

    // --- INITIAL RENDER ---
    populateEventFilters();
    renderChecklists();
    handleResize(); // Initial check on load
});