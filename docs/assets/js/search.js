(function () {
  // ── Search form: navigate to /search?q=… ──────────────────────────────────
  var form = document.querySelector('.search-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = form.querySelector('.search-input');
      var q = (input && input.value.trim()) ? input.value.trim() : '';
      if (q) {
        var base = document.querySelector('meta[name="baseurl"]');
        var baseUrl = base ? base.getAttribute('content') : '';
        window.location.href = baseUrl + '/search?q=' + encodeURIComponent(q);
      }
    });
  }

  // ── Search results page ───────────────────────────────────────────────────
  var container = document.getElementById('search-results-list');
  var status = document.getElementById('search-status');
  if (!container) return; // not on search page

  // Read ?q= from URL
  var params = new URLSearchParams(window.location.search);
  var query = params.get('q') || '';
  if (!query) {
    status.textContent = 'Enter a search term in the box above.';
    return;
  }
  status.textContent = 'Searching for "' + query + '"…';

  // Load the search index
  var base = document.querySelector('meta[name="baseurl"]');
  var baseUrl = base ? base.getAttribute('content') : '';
  fetch(baseUrl + '/search.json')
    .then(function (r) { return r.json(); })
    .then(function (pages) {
      // Build Lunr index
      var idx = lunr(function () {
        this.ref('url');
        this.field('title', { boost: 10 });
        this.field('content');
        pages.forEach(function (p) { this.add(p); }, this);
      });

      // Map url → page for display
      var pageMap = {};
      pages.forEach(function (p) { pageMap[p.url] = p; });

      var results = idx.search(query);
      if (results.length === 0) {
        status.textContent = 'No results for "' + query + '".';
        return;
      }
      status.textContent = results.length + ' result' + (results.length > 1 ? 's' : '') + ' for "' + query + '"';
      results.forEach(function (r) {
        var page = pageMap[r.ref];
        if (!page) return;
        var li = document.createElement('li');
        li.style.marginBottom = '1.5rem';
        li.innerHTML =
          '<a href="' + page.url + '" style="font-size:1.1rem;font-weight:bold;">' + (page.title || page.url) + '</a>' +
          '<p style="margin:0.25rem 0 0;color:#ccc;font-size:0.9rem;">' + (page.content ? page.content.substring(0, 160) + '…' : '') + '</p>';
        container.appendChild(li);
      });
    })
    .catch(function () {
      status.textContent = 'Search index could not be loaded.';
    });
})();
