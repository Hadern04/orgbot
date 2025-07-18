document.addEventListener('DOMContentLoaded', () => {
    // --- STATE ---
    let currentCategory = 'all';
    let serverCategories = [];
    let serverContractors = [];

    // --- DOM ELEMENTS ---
    const $ = id => document.getElementById(id);
    const itemList = $('item-list');
    const addItemBtn = $('add-item-btn');
    const emptyState = $('empty-state');
    const emptyStateTitle = $('empty-state-title');
    const emptyStateText = $('empty-state-text');
    const contractorListTitle = $('contractor-list-title');
    const categoryList = $('category-list');
    const addCategoryForm = $('add-category-form');
    const newCategoryNameInput = $('new-category-name');
    const modalOverlay = $('modal-overlay');
    const modalTitle = $('modal-title');
    const itemForm = $('item-form');
    const cancelButton = $('cancel-button');
    const itemIdInput = $('item-id');
    const itemNameInput = $('item-name');
    const itemCategoryInput = $('item-category');
    const itemContactInput = $('item-contact');
    const itemUserId = $('user-id');
    const toast = $('toast');

    // --- HELPERS ---
    const showToast = (message, type = 'success') => {
        toast.textContent = message;
        toast.className = `toast show ${type}`;
        setTimeout(() => toast.classList.remove('show'), 3000);
    };

    const handleResize = () => {
        const addBtnText = document.querySelector('.add-btn-text');
        if (addBtnText) addBtnText.style.display = window.innerWidth <= 400 ? 'none' : 'inline';
    };

    const fetchCategories = async () => {
        try {
            const res = await fetch(`/api/contractor-categories?owner_id=${itemUserId.value}`);
            if (!res.ok) throw new Error('Ошибка загрузки категорий');
            const data = await res.json();
            serverCategories = data;  // [{id, title}, ...]
            renderCategories();
            populateCategorySelect();
        } catch (err) {
            console.error(err);
            showToast('Ошибка загрузки категорий', 'error');
        }
    };

    const fetchContractors = async (categoryId = 'all') => {
        console.log('Rendering contractors:', serverContractors);
        try {
            let url = `/api/contractors?owner_id=${itemUserId.value}`;
            if (categoryId !== 'all') {
                url += `&category=${encodeURIComponent(categoryId)}`;
            }
            const res = await fetch(url);
            if (!res.ok) throw new Error('Ошибка загрузки подрядчиков');
            const data = await res.json();
            serverContractors = data;
            renderItems();
        } catch (err) {
            console.error(err);
            showToast('Ошибка загрузки подрядчиков', 'error');
        }
    };

    const populateCategorySelect = () => {
        itemCategoryInput.innerHTML = serverCategories.length
            ? serverCategories.map(cat => `<option value="${cat.id}">${cat.title}</option>`).join('')
            : '<option value="">Сначала добавьте категорию</option>';
    };

    const renderCategories = () => {
        categoryList.innerHTML = [
            `<button class="category-btn ${currentCategory === 'all' ? 'active' : ''}" data-category-id="all">Все</button>`,
            ...serverCategories.map(cat => `
                <div class="category-wrapper">
                    <button class="category-btn ${currentCategory === String(cat.id) ? 'active' : ''}" data-category-id="${cat.id}">${cat.title}</button>
                    <button class="delete-category-btn" data-category-id="${cat.id}" title="Удалить категорию">✕</button>
                </div>
            `)
        ].join('');
    };

    const renderItems = () => {
        const filtered = serverContractors;

        contractorListTitle.textContent = currentCategory === 'all'
            ? 'Все подрядчики'
            : `Подрядчики: ${serverCategories.find(cat => String(cat.id) === currentCategory)?.title || ''}`;

        if (!filtered.length) {
            emptyState.style.display = 'flex';
            itemList.style.display = 'none';
            emptyStateTitle.textContent = currentCategory === 'all'
                ? 'Список подрядчиков пуст'
                : `В категории "${serverCategories.find(cat => String(cat.id) === currentCategory)?.title || ''}" нет подрядчиков`;
            emptyStateText.textContent = currentCategory === 'all'
                ? 'Добавьте нового подрядчика, чтобы начать.'
                : 'Добавьте подрядчика в эту категорию или выберите другую.';
            return;
        }

        emptyState.style.display = 'none';
        itemList.style.display = 'grid';
        itemList.innerHTML = filtered.map(c => `
            <div class="item-card" data-id="${c.id}" data-owner-id="${c.owner_id}">
                <div class="item-details">
                    <h3>${c.name}</h3>
                    <p class="item-contact">
                        <svg width="16" height="16" ...></svg>
                        <span>${c.contact}</span>
                    </p>
                </div>
                <div class="item-actions">
                    <button class="edit-btn" ${c.owner_id == itemUserId.value ? '' : 'disabled title="Только для просмотра"'}>Изменить</button>
                    <button class="delete-btn" ${c.owner_id == itemUserId.value ? '' : 'disabled title="Только для просмотра"'}>Удалить</button>
                    ${c.owner_id == itemUserId.value ? '' : '<span class="view-only-badge">Только просмотр</span>'}
                </div>
            </div>`
        ).join('');
    };

    const openModal = (type, id = null) => {
        console.log("itemForm перед reset:", itemForm);
        itemForm.reset();
        modalTitle.textContent = type === 'edit' ? 'Редактировать подрядчика' : 'Добавить подрядчика';
        itemIdInput.value = '';

        if (type === 'edit' && id !== null) {
            const item = serverContractors.find(c => c.id === id);
            if (!item) return;
            itemIdInput.value = item.id;
            itemNameInput.value = item.name;
            itemCategoryInput.value = item.category_id;
            itemContactInput.value = item.contact;
        } else if (currentCategory !== 'all') {
            itemCategoryInput.value = currentCategory;
        }

        modalOverlay.style.display = 'flex';
        setTimeout(() => modalOverlay.classList.add('visible'), 10);
    };

    const closeModal = () => {
        modalOverlay.classList.remove('visible');
        setTimeout(() => modalOverlay.style.display = 'none', 300);
    };

    const deleteContractor = async id => {
        try {
            const res = await fetch(`/api/contractors/${id}`, { method: 'DELETE' });
            if (res.ok) {
                showToast('Подрядчик удален');
                await fetchContractors(currentCategory);
            } else {
                const err = await res.json();
                showToast(err.message || 'Ошибка при удалении', 'error');
            }
        } catch {
            showToast('Ошибка сети', 'error');
        }
    };

    // --- EVENTS ---
    window.addEventListener('resize', handleResize);

    addItemBtn.onclick = () => openModal('add');
    cancelButton.onclick = closeModal;

    categoryList.onclick = async e => {
        if (e.target.classList.contains('category-btn')) {
            currentCategory = e.target.dataset.categoryId;
            renderCategories();
            await fetchContractors(currentCategory); // загрузить подрядчиков для выбранной категории
        }

        if (e.target.classList.contains('delete-category-btn')) {
            const cat = e.target.dataset.categoryId;

            try {
                // Проверка: есть ли подрядчики в этой категории
                const checkRes = await fetch(`/api/contractors?owner_id=${itemUserId.value}&category=${cat}`);
                const contractorsInCat = checkRes.ok ? await checkRes.json() : [];

                if (contractorsInCat.length > 0) {
                    return showToast('Нельзя удалить: в категории есть подрядчики', 'error');
                }

                // Удаление категории
                const url = `/api/contractor-categories/${encodeURIComponent(cat)}`;
                const response = await fetch(url, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' }
                });

                if (!response.ok) {
                    const err = await response.json();
                    return showToast(err.detail || 'Ошибка удаления категории', 'error');
                }

                showToast('Категория удалена');
                await fetchCategories();

                if (currentCategory === cat) currentCategory = 'all';
                await fetchContractors(currentCategory);

            } catch (err) {
                console.error(err);
                showToast('Ошибка удаления категории', 'error');
            }

        }
    };

    addCategoryForm.addEventListener('submit', async e => {
        e.preventDefault();
        const newCategory = newCategoryNameInput.value.trim();
        if (!newCategory) return;

        if (serverCategories.some(cat => cat.title === newCategory)) {
            showToast('Такая категория уже существует', 'error');
            return;
        }

        const payload = {
            title: newCategory,
            owner_id: parseInt(itemUserId.value)
        };

        try {
            const response = await fetch('/api/contractor-categories', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const err = await response.json();
                showToast(err.detail || 'Ошибка при создании категории', 'error');
                return;
            }

            showToast('Категория добавлена!');
            newCategoryNameInput.value = '';
            await fetchCategories();

            // Выставим текущую категорию как новую последнюю
            currentCategory = serverCategories.length ? String(serverCategories[serverCategories.length - 1].id) : 'all';
            await fetchContractors(currentCategory);

        } catch (err) {
            showToast('Ошибка сети', 'error');
        }
    });

    itemList.onclick = async e => {
        const itemCard = e.target.closest('.item-card');
        if (!itemCard) return;
        const id = Number(itemCard.dataset.id);
        if (e.target.classList.contains('edit-btn')) {
            openModal('edit', id);
        }
        if (e.target.classList.contains('delete-btn')) {
            if (confirm('Удалить подрядчика?')) {
                await deleteContractor(id);
            }
        }
    };

    document.addEventListener('submit', e => {
        console.log('Submit event пойман на документе', e.target);
    }, true);

    itemForm.addEventListener('submit', async e => {
        e.preventDefault();
        const id = itemIdInput.value;
        const name = itemNameInput.value.trim();
        const category_id = itemCategoryInput.value;
        const contact = itemContactInput.value.trim();

        const payload = {
            name: name,
            category_id: category_id,
            contact: contact,
            owner_id: parseInt(itemUserId.value)
        };

        try {
            const url = id ? `/api/contractors/${id}` : '/api/contractors';
            const method = id ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                showToast(id ? 'Подрядчик обновлен' : 'Подрядчик добавлен');
                closeModal();
                await fetchContractors(currentCategory);
            } else {
                const errorData = await response.json();
                showToast(errorData.detail || 'Ошибка при сохранении', 'error');
            }
        } catch (error) {
            console.error('Save error:', error);
            showToast('Ошибка сети', 'error');
        }
    });

    // Загрузка при старте
    (async () => {
        await fetchCategories();
        await fetchContractors(currentCategory);
        handleResize();
    })();
});
