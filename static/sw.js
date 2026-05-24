// Zeus Client App — Service Worker for offline support & caching

const CACHE_NAME = 'zeus-client-v1';
const PRECACHE = [
    '/',
    '/static/style.css',
    '/manifest.json',
];

// Install — precache shell
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(PRECACHE))
            .then(() => self.skipWaiting())
    );
});

// Activate — clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        ).then(() => self.clients.claim())
    );
});

// Fetch — network first, fallback to cache
self.addEventListener('fetch', (event) => {
    const { request } = event;

    // Skip SSE and API calls
    if (request.url.includes('/api/') || request.url.includes('/api/events')) {
        return;
    }

    event.respondWith(
        fetch(request)
            .then(response => {
                // Cache successful responses for static assets
                if (response.ok && (request.url.includes('/static/') || request.url === self.location.origin + '/')) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
                }
                return response;
            })
            .catch(() => caches.match(request))
    );
});
