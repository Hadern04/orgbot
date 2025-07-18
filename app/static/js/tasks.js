import { Calendar } from 'fullcalendar';

document.addEventListener('DOMContentLoaded', function() {
    // --- STATE ---
    let isLoading = false;
    let events = [];
    let currentEventId = null;

    // --- DOM ELEMENTS ---
    const $ = id => document.getElementById(id);
    const calendarEl = $('calendar');
    const addItemBtn = $('add-item-btn');
    const emptyState = $('empty-state');
    const modalOverlay = $('modal-overlay');
    const itemForm = $('item-form');
    const itemIdInput = $('item-id');
    const eventTitleInput = $('event-title');
    const eventDatetimeInput = $('event-datetime');
    const eventProjectInput = $('event-project');
    const eventDescriptionInput = $('event-description');
    const eventNotificationInput = $('event-notification');
    const checklistContainer = $('checklist-container');
    const addChecklistItemBtn = $('add-checklist-item-btn');
    const deleteButton = $('delete-button');
    const notifyNowButton = $('notify-now-button');
    const cancelButton = $('cancel-button');
    const toast = $('toast');
    const viewSwitcher = $('view-switcher');

    // --- FULLCALENDAR INIT ---
    const calendar = new FullCalendar.Calendar(calendarEl, {
        plugins: [FullCalendar.DayGrid, FullCalendar.TimeGrid, FullCalendar.List, FullCalendar.Interaction],
        initialView: 'dayGridMonth',
        headerToolbar: false,
        locale: 'ru',
        events: [],
        eventClick: function(info) {
            openModal('edit', info.event);
        },
        dateClick: function(info) {
            openModal('add', { dateStr: info.dateStr });
        }
    });

    // --- FUNCTIONS ---
    const showToast = (message, type = 'success') => {
        toast.textContent = message;
        toast.className = `toast show ${type}`;
        setTimeout(() => toast.classList.remove('show'), 3000);
    };

    const setLoading = (loading) => {
        isLoading = loading;
        document.querySelectorAll('button').forEach(btn => {
            if (btn.id !== 'cancel-button') {
                btn.disabled = loading;
            }
        });
    };

    const fetchEvents = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/events');
            if (!response.ok) throw new Error('Ошибка загрузки событий');
            events = await response.json();
            calendar.removeAllEvents();
            calendar.addEventSource(events);
            updateEmptyState();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    const updateEmptyState = () => {
        const hasEvents = calendar.getEvents().length > 0;
        emptyState.style.display = hasEvents ? 'none' : 'flex';
    };

    const renderChecklist = (items = []) => {
        checklistContainer.innerHTML = '';
        items.forEach((item, index) => addChecklistItem(item.text, item.done, index));
        if (items.length === 0) addChecklistItem();
    };

    const addChecklistItem = (text = '', done = false) => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'checklist-item';
        itemDiv.innerHTML = `
            <input type="checkbox" ${done ? 'checked' : ''}>
            <input type="text" placeholder="Новый пункт..." value="${text}">
            <button type="button" class="delete-checklist-item">&times;</button>
        `;
        checklistContainer.appendChild(itemDiv);

        itemDiv.querySelector('.delete-checklist-item').addEventListener('click', () => {
            itemDiv.remove();
        });
    };

    const getChecklistData = () => {
        return Array.from(checklistContainer.querySelectorAll('.checklist-item')).map(itemDiv => ({
            text: itemDiv.querySelector('input[type="text"]').value.trim(),
            done: itemDiv.querySelector('input[type="checkbox"]').checked
        })).filter(item => item.text);
    };

    const openModal = (type, data = null) => {
        itemForm.reset();
        deleteButton.style.display = 'none';
        notifyNowButton.style.display = 'none';

        if (type === 'edit') {
            const event = data;
            modalTitle.textContent = 'Редактировать событие';
            itemIdInput.value = event.id;
            eventTitleInput.value = event.title;

            const eventDate = new Date(event.start);
            eventDate.setMinutes(eventDate.getMinutes() - eventDate.getTimezoneOffset());
            eventDatetimeInput.value = eventDate.toISOString().slice(0,16);

            const props = event.extendedProps;
            eventProjectInput.value = props.project || '';
            eventDescriptionInput.value = props.description || '';
            eventNotificationInput.value = props.notification || 'none';
            renderChecklist(props.checklist);

            deleteButton.style.display = 'block';
            notifyNowButton.style.display = 'block';
        } else {
            modalTitle.textContent = 'Создать событие';
            if (data?.dateStr) {
                const clickedDate = new Date(data.dateStr);
                clickedDate.setHours(12, 0);
                clickedDate.setMinutes(clickedDate.getMinutes() - clickedDate.getTimezoneOffset());
                eventDatetimeInput.value = clickedDate.toISOString().slice(0,16);
            }
            renderChecklist();
        }

        modalOverlay.style.display = 'flex';
        setTimeout(() => modalOverlay.classList.add('visible'), 10);
    };

    const closeModal = () => {
        modalOverlay.classList.remove('visible');
        setTimeout(() => modalOverlay.style.display = 'none', 300);
    };

    const saveEvent = async (eventData) => {
        setLoading(true);
        try {
            const method = eventData.id ? 'PUT' : 'POST';
            const url = eventData.id ? `/api/events/${eventData.id}` : '/api/events';

            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(eventData)
            });

            if (!response.ok) throw new Error('Ошибка сохранения события');

            await fetchEvents();
            showToast(eventData.id ? 'Событие обновлено' : 'Событие создано');
            closeModal();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    const deleteEvent = async (id) => {
        if (!confirm('Вы уверены, что хотите удалить это событие?')) return;

        setLoading(true);
        try {
            const response = await fetch(`/api/events/${id}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Ошибка удаления события');

            await fetchEvents();
            showToast('Событие удалено', 'error');
            closeModal();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    const sendNotification = async () => {
        setLoading(true);
        try {
            const response = await fetch(`/api/events/${itemIdInput.value}/notify`, {
                method: 'POST'
            });
            if (!response.ok) throw new Error('Ошибка отправки уведомления');
            showToast('Уведомление отправлено');
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    // --- EVENT LISTENERS ---
    viewSwitcher.addEventListener('click', (e) => {
        if (e.target.classList.contains('view-btn')) {
            calendar.changeView(e.target.dataset.view);
            viewSwitcher.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
        }
    });

    addItemBtn.addEventListener('click', () => openModal('add'));
    cancelButton.addEventListener('click', closeModal);
    addChecklistItemBtn.addEventListener('click', () => addChecklistItem());
    modalOverlay.addEventListener('click', (e) => e.target === modalOverlay && closeModal());

    deleteButton.addEventListener('click', () => {
        if (itemIdInput.value) deleteEvent(itemIdInput.value);
    });

    notifyNowButton.addEventListener('click', sendNotification);

    itemForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const eventData = {
            id: itemIdInput.value || null,
            title: eventTitleInput.value,
            start: eventDatetimeInput.value,
            extendedProps: {
                project: eventProjectInput.value,
                description: eventDescriptionInput.value,
                checklist: getChecklistData(),
                notification: eventNotificationInput.value,
            }
        };
        saveEvent(eventData);
    });

    // --- INIT ---
    calendar.render();
    fetchEvents();
});