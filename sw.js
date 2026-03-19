const CACHE_NAME = 'sereno-app-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/styles.css'
  // Se você tiver um arquivo script.js, adicione '/script.js' aqui
];

// Instala o Service Worker e salva os arquivos no cache
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

// Intercepta as requisições para carregar mais rápido
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request);
      })
  );
});