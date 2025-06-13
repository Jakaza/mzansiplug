// js/admin_tagify_init.js
document.addEventListener('DOMContentLoaded', function() {
    const tagInputs = document.querySelectorAll('input[name="tags"]');
    
    tagInputs.forEach(input => {
        const tagify = new Tagify(input, {
            delimiters: ',',  // Only comma as delimiter
            pattern: /^[a-zA-Z0-9\s\-]+$/,  // Only letters, numbers, spaces, hyphens
            maxTags: 15,
            dropdown: {
                enabled: 1,
                maxItems: 10,
                closeOnSelect: false
            },
            originalInputValueFormat: valuesArr => valuesArr.map(item => item.value).join(',')
        });

        // Clean existing tags that might have JSON artifacts
        if (input.value) {
            const cleanedTags = input.value.split(',')
                .map(tag => tag.trim())
                .filter(tag => !['{', '}', '[', ']', ':', '"'].some(char => tag.includes(char)));
            tagify.removeAllTags();
            tagify.addTags(cleanedTags);
        }
    });
});