document.addEventListener('DOMContentLoaded', function() {
    // --- DATA & STATE ---
    let currentSort = 'date';
    let serverEvents = []; // Хранение списка мероприятий

    // --- DOM ELEMENTS ---
    const eventList = document.getElementById('event-list');
    const sortBy = document.getElementById('sort-by');
    const addEventBtn = document.getElementById('add-event-btn');
    const emptyState = document.getElementById('empty-state');
    const modalOverlay = document.getElementById('modal-overlay');
    const modalTitle = document.getElementById('modal-title');
    const eventForm = document.getElementById('event-form');
    const cancelButton = document.getElementById('cancel-button');
    const itemIdInput = document.getElementById('event-id');
    const eventNameInput = document.getElementById('name');
    const itemDateInput = document.getElementById('date');
    const itemLocationInput = document.getElementById('location');
    const itemUserId = document.getElementById('user-id');

    // Toast element
    const toast = document.getElementById('toast');

    // --- FLATPICKR INITIALIZATION ---
    const fp = flatpickr("#date", {
        locale: "ru",
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "j F Y г.",
        allowInput: true,
        minDate: "today",
        disable: [
            function(date) {
                return date < new Date().fp_incr(-1);
            }
        ]
    });

    // --- FUNCTIONS ---
    async function fetchEvents() {
        try {
            const response = await fetch(`/api/events?owner_id=${itemUserId.value}`); // Запрос на сервер для получения списка мероприятий
            if (!response.ok) {
                showToast('Ошибка при загрузке мероприятий', 'error');
                return;
            }
            serverEvents = await response.json();
            renderEvents(serverEvents);
        } catch (error) {
            console.error('Fetch error:', error);
            showToast('Ошибка сети', 'error');
        }
    }

    function handleResize() {
        const addBtnText = document.querySelector('.add-btn-text');
        if (!addBtnText) return;
        if (window.innerWidth <= 400) {
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

    function sortEvents(events) {
        return [...events].sort((a, b) => {
            if (currentSort === 'name') {
                return a.title.localeCompare(b.title);
            }
            return new Date(a.date) - new Date(b.date);
        });
    }

    function renderEvents(events) {
        const sortedEvents = sortEvents(events);
        eventList.innerHTML = '';

        if (sortedEvents.length === 0) {
            emptyState.style.display = 'flex';
            eventList.style.display = 'none';
        } else {
            emptyState.style.display = 'none';
            eventList.style.display = 'grid';
        }

        sortedEvents.forEach(event => {
            const eventCard = document.createElement('div');
            eventCard.className = 'event-card';
            eventCard.dataset.id = event.id;

            const eventDate = new Date(event.date);
            const formattedDate = eventDate.toLocaleDateString('ru-RU', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            });

            eventCard.innerHTML = `
                <div class="event-details">
                    <h3>${event.title}</h3>
                    <p class="event-date">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                        ${formattedDate}
                    </p>
                    ${event.location ? `
                    <p class="event-location">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                        ${event.location}
                    </p>
                    ` : ''}
                </div>
                <div class="event-actions">
                    <button class="edit-btn" data-id="${event.id}">Изменить</button>
                    <button class="delete-btn" data-id="${event.id}">Удалить</button>
                </div>
            `;
            eventList.appendChild(eventCard);
        });
    }

    function openModal(type, eventId = null) {
        eventForm.reset();
        fp.clear();

        if (type === 'edit') {
            const event = serverEvents.find(e => e.id === eventId);
            if (!event) return;

            modalTitle.textContent = 'Редактировать мероприятие';
            itemIdInput.value = event.id;
            eventNameInput.value = event.title;
            fp.setDate(event.date, true);
            itemLocationInput.value = event.location || ''
        } else {
            modalTitle.textContent = 'Добавить мероприятие';
            itemIdInput.value = '';
        }

        modalOverlay.style.display = 'flex';
        setTimeout(() => modalOverlay.classList.add('visible'), 10);
    }

    function closeModal() {
        modalOverlay.classList.remove('visible');
        setTimeout(() => modalOverlay.style.display = 'none', 300);
    }

    // --- EVENT LISTENERS ---

    sortBy.addEventListener('change', (e) => {
        currentSort = e.target.value;
        renderEvents(serverEvents);
    });

    addEventBtn.addEventListener('click', () => {
        openModal('add');
    });

    cancelButton.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            closeModal();
        }
    });

    eventList.addEventListener('click', async (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;

        const eventId = parseInt(btn.dataset.id);

        if (btn.classList.contains('edit-btn')) {
            openModal('edit', eventId);
        }

        if (btn.classList.contains('delete-btn')) {
            const deleteHandler = async (confirmed) => {
                if (!confirmed) return;

                try {
                    const response = await fetch(`/api/events/${eventId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        await fetchEvents(); // Перезагружаем список мероприятий
                    } else {
                        showToast('Ошибка при удалении', 'error');
                    }
                } catch (error) {
                    console.error('Delete error:', error);
                    showToast('Ошибка сети', 'error');
                }
            };

            if (window.Telegram && Telegram.WebApp) {
                Telegram.WebApp.showConfirm(
                    'Вы уверены, что хотите удалить это мероприятие?',
                    deleteHandler
                );
            } else {
                if (confirm('Вы уверены, что хотите удалить это мероприятие?')) {
                    await deleteHandler(true);
                }
            }
        }
    });

    eventForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = parseInt(itemIdInput.value);

        const eventData = {
            owner_id: itemUserId.value,
            title: eventNameInput.value.trim(),
            location: itemLocationInput.value.trim(),
            date: itemDateInput.value
        };

        try {
            const url = id ? `/api/events/${id}` : '/api/events';
            const method = id ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(eventData)
            });

            if (response.ok) {
                await fetchEvents(); // Перезагружаем список мероприятий после добавления/редактирования
                closeModal();
            } else {
                const errorData = await response.json();
                showToast(errorData.message || 'Ошибка при сохранении', 'error');
            }
        } catch (error) {
            console.error('Save error:', error);
            showToast('Ошибка сети', 'error');
        }
    });

    // --- INITIAL RENDER ---
    fetchEvents();
    handleResize();
});
