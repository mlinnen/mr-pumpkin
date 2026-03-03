// Simple search — redirects to GitHub repository search
(function () {
  var form = document.querySelector('.search-form');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    var input = form.querySelector('.search-input');
    if (input && input.value.trim()) {
      // Append "repo:mlinnen/mr-pumpkin" to scope results
      var query = input.value.trim() + ' repo:mlinnen/mr-pumpkin';
      var url = 'https://github.com/search?q=' + encodeURIComponent(query) + '&type=code';
      window.open(url, '_blank', 'noopener');
      e.preventDefault();
    }
  });
})();
