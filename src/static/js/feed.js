function feedLoader() {
    const items = document.querySelectorAll('#feed > .item');

    function handleMenuButtonClick(event) {
        const item = event.currentTarget.closest('.item');
        const contextMenu = item.querySelector('.context-menu');
        const options = item.querySelector('.options');

        if (contextMenu) {
            contextMenu.toggleAttribute('data-hidden');
            options.toggleAttribute('data-force-opacity');
        }
    }

    function handleClickOutside(event) {

        items.forEach(item => {
            const contextMenu = item.querySelector('.context-menu');
            const options = item.querySelector('.options');

            if (!item.contains(event.target) && contextMenu && !contextMenu.hasAttribute('data-hidden')) {
                contextMenu.setAttribute('data-hidden', '');
                options.removeAttribute('data-force-opacity');

            }
        });
    }

    items.forEach(item => {
        const dataId = item.getAttribute('data-id');
        const btnMenu = item.querySelector('.btn-menu');
        if (btnMenu) {
            btnMenu.addEventListener('click', handleMenuButtonClick);
            const deleteButton = item.querySelector('[data-delete]');

            deleteButton.addEventListener('click', () => {
                item.remove();
                const formData = new FormData();
                formData.append('id', item.dataset.id);
                fetch('/posts/delete', {
                    'method': 'POST',
                    'body': formData
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(response.status);
                        }
                    })
                    .catch(error => {
                        console.log(error);
                    }); 
            });
        }

    });

    document.addEventListener('click', handleClickOutside);
}