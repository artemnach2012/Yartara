// static/js/main.js
let allProducts = [];
let currentPage = 1;
const itemsPerPage = 20;

async function loadProducts() {
    try {
        const response = await fetch('data/products.json');
        if (!response.ok) throw new Error('Ошибка загрузки');
        allProducts = await response.json();
        applyFilters();
    } catch (err) {
        console.error(err);
        const grid = document.getElementById('catalogGrid');
        if (grid) grid.innerHTML = '<p>Не удалось загрузить каталог. Попробуйте позже.</p>';
    }
}

function applyFilters() {
    if (!allProducts.length) return;
    let filtered = [...allProducts];
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase().trim() || '';
    if (searchTerm) {
        filtered = filtered.filter(p => p.name.toLowerCase().includes(searchTerm));
    }
    renderProducts(filtered);
}

function renderProducts(products) {
    const container = document.getElementById('catalogGrid');
    if (!container) return;

    const totalPages = Math.ceil(products.length / itemsPerPage);
    const start = (currentPage - 1) * itemsPerPage;
    const paginated = products.slice(start, start + itemsPerPage);

    container.innerHTML = paginated.map(p => `
        <div class="product-card" onclick="window.location.href='product.html?id=${p.id}'">
            <img class="product-image" src="${p.image_url}" alt="${escapeHtml(p.name)}" onerror="this.src='https://via.placeholder.com/300x200?text=Фото'">
            <div class="product-info">
                <div class="product-title">${escapeHtml(p.name)}</div>
                <div class="product-details">${p.volume || ''} ${p.diameter || ''}</div>
                <div class="product-price">${p.price.toFixed(2)} ₽</div>
                <div class="product-stock">Остаток: ${p.stock} шт</div>
            </div>
        </div>
    `).join('');

    renderPagination(totalPages);
}

function renderPagination(totalPages) {
    const container = document.getElementById('pagination');
    if (!container) return;
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    let html = '';
    for (let i = 1; i <= totalPages; i++) {
        html += `<button class="${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
    }
    container.innerHTML = html;
}

function goToPage(page) {
    currentPage = page;
    applyFilters();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function escapeHtml(str) {
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('catalogGrid')) {
        loadProducts();
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                currentPage = 1;
                applyFilters();
            });
        }
    }
});