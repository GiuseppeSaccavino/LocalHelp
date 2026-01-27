if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('static/sw.js')
        .then(reg => console.log('SW registered', reg.scope))
        .catch(err => console.error('SW failed', err));
    });
}