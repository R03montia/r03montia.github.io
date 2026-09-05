// 离线 PWA：静态资源缓存优先（_astro / images / models / pagefind / 图标），
// 页面导航网络优先、断网时回退缓存。发版后靠 CACHE_NAME  bump 整体换血。
const CACHE_NAME = 'r03montia-v1';
const CORE = ['/', '/manifest.webmanifest', '/icon-512.png', '/apple-touch-icon.png', '/favicon-32.png'];
const STATIC_PREFIXES = ['/_astro/', '/images/', '/models/', '/pagefind/', '/tags.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE)).then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

const isStatic = (pathname) =>
  STATIC_PREFIXES.some((prefix) => pathname.startsWith(prefix)) ||
  /\.(png|jpg|jpeg|webp|avif|gif|svg|ico|woff2?|css|js)$/.test(pathname);

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate' || !isStatic(url.pathname)) {
    // 页面与其他资源：网络优先，拿到就更新缓存；断网回退缓存，再不行回首页。
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return response;
        })
        .catch(() => caches.match(request).then((hit) => hit ?? caches.match('/'))),
    );
    return;
  }

  // 静态资源：缓存优先，命中直接用；未命中走网络并顺手入库。
  event.respondWith(
    caches.match(request).then(
      (hit) =>
        hit ??
        fetch(request).then((response) => {
          if (response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return response;
        }),
    ),
  );
});
