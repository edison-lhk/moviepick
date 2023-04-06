const toasts = document.querySelectorAll('.toast');
const toast_btns = document.querySelectorAll('.toast-btn');

// Flash content disappear automatically after a few seconds
let toasts_count = 0;
if (toasts.length > 0) {
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.remove();
        }, 3000 + toasts_count * 500);
        toasts_count += 1;
    });
};

// Allows users to delete the flash content manually if they want
if (toast_btns.length > 0) {
    toast_btns.forEach(toast_btn => {
        toast_btn.addEventListener('click', () => {
            toast_btn.parentElement.remove();
        });
    });
};