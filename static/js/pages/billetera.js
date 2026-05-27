/* billetera.js — FairBet Lab */
(function () {
  'use strict';

  /* ── Tabs de movimientos ── */
  const tabs = document.querySelectorAll('.movements-tab');
  const rows = document.querySelectorAll('.movement-row');

  function applyMovFilter(filter) {
    rows.forEach(function (row) {
      const type = row.dataset.type || '';
      row.style.display = (filter === 'all' || type === filter) ? '' : 'none';
    });
  }

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');
      applyMovFilter(tab.dataset.filter || 'all');
    });
  });

  /* ── Botones de acción simulados ── */
  function showToast(msg) {
    const existing = document.getElementById('walletToast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'walletToast';
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    toast.style.cssText = [
      'position:fixed', 'bottom:28px', 'right:28px',
      'background:#1e1b4b', 'color:#fff',
      'padding:12px 20px', 'border-radius:10px',
      'font-size:0.875rem', 'font-weight:600',
      'box-shadow:0 8px 32px rgba(15,23,42,0.25)',
      'z-index:9999', 'opacity:0',
      'transform:translateY(8px)',
      'transition:opacity 0.2s ease, transform 0.2s ease',
      'max-width:320px', 'line-height:1.4'
    ].join(';');
    toast.textContent = msg;
    document.body.appendChild(toast);

    requestAnimationFrame(function () {
      toast.style.opacity  = '1';
      toast.style.transform = 'translateY(0)';
    });

    setTimeout(function () {
      toast.style.opacity   = '0';
      toast.style.transform = 'translateY(8px)';
      setTimeout(function () { toast.remove(); }, 250);
    }, 3200);
  }

  const btnRecarga  = document.getElementById('btnRecarga');
  const btnRetiro   = document.getElementById('btnRetiro');
  const btnMovs     = document.getElementById('btnMovimientos');

  if (btnRecarga) {
    btnRecarga.addEventListener('click', function () {
      showToast('Recarga simulada: esta función requiere integración con el backend.');
    });
  }

  if (btnRetiro) {
    btnRetiro.addEventListener('click', function () {
      showToast('Retiro simulado: las fichas virtuales no tienen valor monetario real.');
    });
  }

  if (btnMovs) {
    btnMovs.addEventListener('click', function () {
      const card = document.getElementById('movementsCard');
      if (card) card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }
})();
