importScripts('/static/js/cache-polyfill.js');

self.addEventListener('install', function(e) {
  e.waitUntil(caches.open('WRU').then(function(cache)
  {
    return cache.addAll([
      '/Home',
      '/Staff/Login',
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
    //https://jakearchibald.com/2014/offline-cookbook/#network-falling-back-to-cache Accessed: 3/12/2017

    //New network first cache second way to load.
    //Updates navbar on login etc
    fetch(event.request).catch(function()
    {
      return caches.match(event.request)
    })

    //Old cache first network second way to load.
    //Didn't update navbar on login etc
    // caches.match(event.request).then(function(response)
    // {
    //   return response || fetch(event.request);
    // })
  );
});
