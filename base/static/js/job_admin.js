document.addEventListener('DOMContentLoaded', function () {
    const categorySelect = document.getElementById('id_categories');
    const subcategorySelect = document.getElementById('id_subcategories');

    const allOptions = Array.from(subcategorySelect.options);

    function filterSubcategories() {
        const selectedCategories = Array.from(categorySelect.selectedOptions).map(opt => opt.textContent.trim());

        subcategorySelect.innerHTML = '';

        allOptions.forEach(option => {
            const categoryName = option.textContent.split('(').pop().replace(')', '').trim();
            if (selectedCategories.includes(categoryName)) {
                subcategorySelect.appendChild(option);
            }
        });
    }

    categorySelect.addEventListener('change', filterSubcategories);

    // Filter on load (for edit form)
    filterSubcategories();
});
