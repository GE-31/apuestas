/* FairBet Lab — events.js */

(function () {
  'use strict';

  var grid       = document.getElementById('eventsGrid');
  var emptyMsg   = document.getElementById('eventsEmpty');
  var filterBtns = document.querySelectorAll('.filter-tab');
  var searchInput = document.getElementById('eventSearch');

  if (!grid) return;

  var cards = Array.from(grid.querySelectorAll('.event-card-full'));
  var activeFilter = 'all';
  var searchQuery  = '';

  function applyFilters() {
    var visible = 0;

    cards.forEach(function (card) {
      var sport  = card.dataset.sport   || '';
      var status = card.dataset.status  || '';
      var text   = card.textContent.toLowerCase();

      var matchFilter =
        activeFilter === 'all'        ||
        activeFilter === sport        ||
        (activeFilter === 'live' && status === 'live');

      var matchSearch = searchQuery === '' || text.indexOf(searchQuery) !== -1;

      var show = matchFilter && matchSearch;
      card.hidden = !show;
      if (show) visible++;
    });

    if (emptyMsg) emptyMsg.hidden = visible > 0;
  }

  /* Filtros por tabs */
  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      filterBtns.forEach(function (b) {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      activeFilter = btn.dataset.filter || 'all';
      applyFilters();
    });
  });

  /* Búsqueda */
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      searchQuery = searchInput.value.trim().toLowerCase();
      applyFilters();
    });
  }

})();
