importScripts('/static/js/cache-polyfill.js');

self.addEventListener('install', function(e)
{
  e.waitUntil(caches.open('WRUv1').then(function(cache)
  {
    return cache.addAll([
      '/',
      '/Home',
      '/Staff/Login',
      '/Staff/EventForm',
      '/Staff/TournamentForm',
      '/static/css/style.css',
      '/static/css/slider.css',
      '/static/js/formhandling.js',
      '/static/resources/images/favicon.ico',
      '/static/resources/images/logo.png'
    ]);
  })
  );
});

self.addEventListener('activate', function(event)
{
  console.log('SW now ready to handle fetches!');
});

self.addEventListener('fetch', function(event)
{
  //https://jakearchibald.com/2014/offline-cookbook/#network-falling-back-to-cache Accessed: 3/12/2017
  console.log(event.request.url);
  event.respondWith(fetch(event.request).catch(function()
    {
      return caches.match(event.request)
    })
  );
});
