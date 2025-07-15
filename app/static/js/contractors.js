document.addEventListener('DOMContentLoaded', function() {
    // --- STATE ---
    let currentCategory = 'Все';

    // --- DOM ELEMENTS ---
    const itemList = document.getElementById('item-list');
    const addItemBtn = document.getElementById('add-item-btn');
    const emptyState = document.getElementById('empty-state');
    const emptyStateTitle = document.getElementById('empty-state-title');
    const emptyStateText = document.getElementById('empty-state-text');
    const contractorListTitle = document.getElementById('contractor-list-title');
    const categoryList = document.getElementById('category-list');
    const addCategoryForm = document.getElementById('add-category-form');
    const newCategoryNameInput = document.getElementById('new-category-name');
    const modalOverlay = document.getElementById('modal-overlay');
    const modalTitle = document.getElementById('modal-title');
    const itemForm = document.getElementById('item-form');
    const cancelButton = document.getElementById('cancel-button');
    const itemIdInput = document.getElementById('item-id');
    const itemNameInput = document.getElementById('item-name');
    const itemCategoryInput = document.getElementById('item-category');
    const itemContactInput = document.getElementById('item-contact');
    const itemUserId = document.getElementById('user_id');

    // Toast element
    const toast = document.getElementById('toast');

    // --- FUNCTIONS ---
    function handleResize() {
        const addBtnText = document.querySelector('.add-btn-text');
        if (addBtnText) {
            addBtnText.style.display = window.innerWidth <= 400 ? 'none' : 'inline';
        }
    }

    function showToast(message, type = 'success') {
        toast.textContent = message;
        toast.className = `toast show ${type}`;
        setTimeout(() => toast.className = toast.className.replace("show", ""), 3000);
    }

    function populateCategoriesForSelect() {
        itemCategoryInput.innerHTML = serverCategories.length === 0
            ? '<option value="">Сначала добавьте категорию</option>'
            : serverCategories.map(cat => `<option value="${cat}">${cat}</option>`).join('');
    }

    function renderCategories() {
        categoryList.innerHTML = `
            <button class="category-btn ${currentCategory === 'Все' ? 'active' : ''}" data-category="Все">Все</button>
            ${serverCategories.map(cat => `
                <button class="category-btn ${currentCategory === cat ? 'active' : ''}" data-category="${cat}">${cat}</button>
            `).join('')}
        `;
        populateCategoriesForSelect();
    }

    function renderItems() {
        const filteredItems = currentCategory === 'Все'
            ? serverContractors
            : serverContractors.filter(item => item.contractor_category === currentCategory);

        contractorListTitle.textContent = currentCategory === 'Все'
            ? 'Все подрядчики'
            : `Подрядчики: ${currentCategory}`;

        if (filteredItems.length === 0) {
            emptyState.style.display = 'flex';
            itemList.style.display = 'none';
            emptyStateTitle.textContent = currentCategory === 'Все'
                ? 'Список подрядчиков пуст'
                : `В категории "${currentCategory}" нет подрядчиков`;
            emptyStateText.textContent = currentCategory === 'Все'
                ? 'Добавьте нового подрядчика, чтобы начать.'
                : 'Добавьте подрядчика в эту категорию или выберите другую.';
        } else {
            emptyState.style.display = 'none';
            itemList.style.display = 'grid';
            itemList.innerHTML = filteredItems.map(contractor => `
                <div class="item-card"
                     data-id="${contractor.id}"
                     data-owner-id="${contractor.contractor_owner_id}">
                    <div class="item-details">
                        <h3>${contractor.contractor_name}</h3>
                        <p class="item-contact">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                            </svg>
                            <span>${contractor.contractor_contact}</span>
                        </p>
                    </div>
                    <div class="item-actions">
                        <button class="edit-btn" ${contractor.contractor_owner_id == itemUserId.value ? '' : 'disabled title="Только для просмотра"'}>
                            Изменить
                        </button>
                        <button class="delete-btn" ${contractor.contractor_owner_id == itemUserId.value ? '' : 'disabled title="Только для просмотра"'}>
                            Удалить
                        </button>
                        ${contractor.contractor_owner_id == itemUserId.value ? '' : '<span class="view-only-badge">Только просмотр</span>'}
                    </div>
                </div>
            </div>
        `).join('');
        }
    }

    function openModal(type, itemId = null) {
        itemForm.reset();

        if (type === 'edit') {
            const item = serverContractors.find(e => e.id === itemId);
            if (item) {
                modalTitle.textContent = 'Редактировать подрядчика';
                itemIdInput.value = item.id;
                itemNameInput.value = item.contractor_name;
                itemCategoryInput.value = item.contractor_category;
                itemContactInput.value = item.contractor_contact
            }
        } else {
            modalTitle.textContent = 'Добавить подрядчика';
            itemIdInput.value = '';
            if (currentCategory !== 'Все') {
                itemCategoryInput.value = currentCategory;
            }
        }

        modalOverlay.style.display = 'flex';
        setTimeout(() => modalOverlay.classList.add('visible'), 10);
    }

    function closeModal() {
        modalOverlay.classList.remove('visible');
        setTimeout(() => modalOverlay.style.display = 'none', 300);
    }

    // --- EVENT LISTENERS ---
    categoryList.addEventListener('click', (e) => {
        if (e.target.classList.contains('category-btn')) {
            currentCategory = e.target.dataset.category;
            renderCategories();
            renderItems();
        }
    });

    addCategoryForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const newCategory = newCategoryNameInput.value.trim();
        if (!newCategory) return;

        if (!serverCategories.includes(newCategory)) {
            serverCategories.push(newCategory);
            serverCategories.sort();
            currentCategory = newCategory;
            renderCategories();
            renderItems();
            newCategoryNameInput.value = '';
            showToast('Категория добавлена!');
        } else {
            showToast('Такая категория уже существует', 'error');
        }
    });

    addItemBtn.addEventListener('click', () => openModal('add'));
    cancelButton.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => e.target === modalOverlay && closeModal());

    itemList.addEventListener('click', async (e) => {
        const card = e.target.closest('.item-card');
        if (!card) return;

        const itemId = parseInt(card.dataset.id);

        if (e.target.classList.contains('edit-btn')) {
            openModal('edit', itemId);
        }

        if (e.target.classList.contains('delete-btn')) {
            const deleteContractor = async (confirmed) => {
                if (!confirmed) return;

                try {
                    const response = await fetch(`/api/contractor/${itemId}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });

                    if (response.ok) {
                        // Обновляем список без перезагрузки страницы
                        const index = serverContractors.findIndex(c => c.id === itemId);
                        if (index !== -1) {
                            serverContractors.splice(index, 1);
                            renderItems();
                        }
                        showToast('Подрядчик удален', 'success');
                    } else {
                        const error = await response.json();
                        showToast(error.message || 'Ошибка при удалении', 'error');
                    }
                } catch (error) {
                    console.error('Delete error:', error);
                    showToast('Ошибка сети', 'error');
                }
            };

            // Проверяем, запущено ли в Telegram WebApp
            if (window.Telegram?.WebApp?.platform !== 'unknown') {
                Telegram.WebApp.showConfirm(
                    'Вы уверены, что хотите удалить этого подрядчика?',
                    deleteContractor
                );
            } else {
                if (confirm('Вы уверены, что хотите удалить этого подрядчика?')) {
                    await deleteContractor(true);
                }
            }
        }
    });

    itemForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitButton = itemForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        const id = parseInt(itemIdInput.value);

        const ownerId = itemUserId.value;
        if (!ownerId) {
            showToast('Не удалось определить владельца', 'error');
            return;
        }

        const contractorData = {
            name: itemNameInput.value,
            category: itemCategoryInput.value,
            contact: itemContactInput.value,
            owner_id: itemUserId.value
        };

        try {
            const response = await fetch(id ? `/api/contractor/${id}` : '/api/contractor', {
                method: id ? 'PUT' : 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(contractorData)
            });

            if (response.ok) {
                showToast(id ? 'Изменения сохранены' : 'Подрядчик добавлен');
                closeModal();
                renderItems();
            } else {
                const errorData = await response.json();
                showToast(errorData.message || 'Ошибка при сохранении', 'error');
            }
        } catch (error) {
            console.error('Save error:', error);
            showToast('Ошибка сети', 'error');
        } finally {
            submitButton.disabled = false;
        }
    });

    window.addEventListener('resize', handleResize);

    // --- INITIAL RENDER ---
    renderCategories();
    renderItems();
    handleResize();
});