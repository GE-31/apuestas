/* mis_apuestas.js — FairBet Lab */
(function () {
  'use strict';

  const tabs  = document.querySelectorAll('.bets-filter-tab');
  const rows  = document.querySelectorAll('.bet-row');
  const count = document.getElementById('betsVisibleCount');

  function updateCount(n) {
    if (count) count.textContent = n;
  }

  function applyFilter(filter) {
    let visible = 0;
    rows.forEach(function (row) {
      const status = row.dataset.status || '';
      const show   = filter === 'all' || status === filter;
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    updateCount(visible);

    const empty = document.getElementById('betsTableEmpty');
    if (empty) empty.hidden = visible > 0;
  }

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');
      applyFilter(tab.dataset.filter || 'all');
    });
  });

  updateCount(rows.length);
})();
