importScripts('/static/js/cache-polyfill.js');

self.addEventListener('install', function(e)
{
  e.waitUntil(caches.open('WRU').then(function(cache)
  {
    return cache.addAll([
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

self.addEventListener('fetch', function(event)
{
  console.log(event.request.url);
  event.respondWith(
    //https://jakearchibald.com/2014/offline-cookbook/#network-falling-back-to-cache Accessed: 3/12/2017
    fetch(event.request).catch(function()
    {
      return caches.match(event.request)
    })
  );
});
