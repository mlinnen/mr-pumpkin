// Development service worker (minimal caching)
self.addEventListener('fetch', event => {
    // Let network handle all requests in dev mode
    event.respondWith(fetch(event.request));
});
