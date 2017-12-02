importScripts('/static/js/cache-polyfill.js');

self.addEventListener('install', function(e) {
  e.waitUntil(caches.open('test').then(function(cache)
  {
    return cache.addAll([
      '/Home',
      '/Staff/Login',
      '/Logout',
      '/Staff/EventForm',
      '/Staff/TournamentForm',
      '/static/css/style.css',
      '/static/css/nouislider.css',
      '/static/css/nouislider.min.css',
      '/static/js/formhandling.js',
      '/static/resources/images/favicon.ico',
      '/static/resources/images/logo.png'
    ]);
  })
  );
});

self.addEventListener('fetch', function(event)
{
  console.log(event.request.url);
  event.respondWith(
    caches.match(event.request).then(function(response)
    {
      return response || fetch(event.request);
    })
  );
});
