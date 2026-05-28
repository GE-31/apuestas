/* dashboard.js — Sportsbook · Apuesta24/7 */
(function () {
  'use strict';

  var cfg     = window.APUESTA_CONFIG || {};
  var userId  = cfg.userId   || 0;
  var apiBase = cfg.apiBase  || '/api/apuestas/operaciones/';
  var csrf    = cfg.csrfToken || '';

  /* ─── State ─── */
  var selection    = null;
  var activeLeague = null;

  /* ─── Bet slip elements ─── */
  var betSlip   = document.getElementById('betSlip');
  var bsEvent   = document.getElementById('bsEvent');
  var bsMarket  = document.getElementById('bsMarket');
  var bsSelName = document.getElementById('bsSelName');
  var bsOdd     = document.getElementById('bsOdd');
  var bsPayout  = document.getElementById('bsPayout');
  var bsStake   = document.getElementById('bsStake');
  var bsSubmit  = document.getElementById('bsSubmit');
  var bsMsg     = document.getElementById('bsMsg');
  var bsClose   = document.getElementById('betSlipClose');
  var bsRemove  = document.getElementById('bsRemove');

  /* ─── All league groups in main ─── */
  var allGroups = document.querySelectorAll('.sb-group');

  /* ═══════════════════════════════════════
     SIDEBAR — Sport collapse toggle
  ═══════════════════════════════════════ */
  document.querySelectorAll('.sb-sport-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var sport  = btn.closest('.sb-sport');
      var list   = sport ? sport.querySelector('.sb-league-list') : null;
      var isOpen = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
      if (list) list.hidden = isOpen;
    });
  });

  /* ═══════════════════════════════════════
     SIDEBAR — League filter (click to filter main)
  ═══════════════════════════════════════ */
  function filterByLeague(ligaKey) {
    activeLeague = ligaKey;
    allGroups.forEach(function (g) {
      g.style.display = (!ligaKey || g.id === 'liga-' + ligaKey) ? '' : 'none';
    });
  }

  function clearLeagueFilter() {
    activeLeague = null;
    allGroups.forEach(function (g) { g.style.display = ''; });
    document.querySelectorAll('.sb-league-link').forEach(function (l) {
      l.classList.remove('is-active');
    });
  }

  document.querySelectorAll('.sb-league-link').forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      var ligaKey  = link.dataset.liga;
      var isActive = link.classList.contains('is-active');

      /* Clear all active states */
      document.querySelectorAll('.sb-league-link').forEach(function (l) {
        l.classList.remove('is-active');
      });

      if (isActive) {
        /* Toggle off — show all leagues */
        clearLeagueFilter();
        return;
      }

      link.classList.add('is-active');
      filterByLeague(ligaKey);

      /* Scroll main to top */
      var main = document.querySelector('.sb-main');
      if (main) main.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  /* ═══════════════════════════════════════
     ODDS — Click to open bet slip
  ═══════════════════════════════════════ */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.sb-odd');
    if (!btn || btn.disabled) return;

    var wasSel = btn.classList.contains('is-selected');

    document.querySelectorAll('.sb-odd.is-selected').forEach(function (b) {
      b.classList.remove('is-selected');
      b.setAttribute('aria-pressed', 'false');
    });

    if (wasSel) {
      closeBetSlip();
      selection = null;
      return;
    }

    btn.classList.add('is-selected');
    btn.setAttribute('aria-pressed', 'true');

    selection = {
      eventoId:  btn.dataset.eventoId,
      evento:    btn.dataset.evento,
      mercado:   btn.dataset.mercado,
      mercadoId: btn.dataset.mercadoId,
      selId:     btn.dataset.selId,
      sel:       btn.dataset.sel,
      oddId:     btn.dataset.oddId,
      odd:       parseFloat(btn.dataset.odd) || 0,
    };

    openBetSlip();
    updateBetSlip();
  });

  /* ═══════════════════════════════════════
     BET SLIP — Open / Close
  ═══════════════════════════════════════ */
  function openBetSlip() {
    if (betSlip) {
      betSlip.classList.add('is-open');
      betSlip.setAttribute('aria-hidden', 'false');
    }
  }

  function closeBetSlip() {
    if (betSlip) {
      betSlip.classList.remove('is-open');
      betSlip.setAttribute('aria-hidden', 'true');
    }
    clearMsg();
  }

  if (bsClose) {
    bsClose.addEventListener('click', function (e) {
      e.stopPropagation();
      deselectAll();
      closeBetSlip();
      selection = null;
    });
  }

  if (bsRemove) {
    bsRemove.addEventListener('click', function () {
      deselectAll();
      closeBetSlip();
      selection = null;
    });
  }

  function deselectAll() {
    document.querySelectorAll('.sb-odd.is-selected').forEach(function (b) {
      b.classList.remove('is-selected');
      b.setAttribute('aria-pressed', 'false');
    });
  }

  /* ═══════════════════════════════════════
     BET SLIP — Populate & payout
  ═══════════════════════════════════════ */
  function updateBetSlip() {
    if (!selection) return;
    if (bsEvent)   bsEvent.textContent   = selection.evento  || '—';
    if (bsMarket)  bsMarket.textContent  = selection.mercado || '—';
    if (bsSelName) bsSelName.textContent = selection.sel     || '—';
    if (bsOdd)     bsOdd.textContent     = '× ' + (selection.odd || '—');
    updatePayout();
  }

  function updatePayout() {
    if (!bsStake || !bsPayout || !selection) return;
    var stake  = parseFloat(bsStake.value) || 0;
    var payout = stake > 0 ? (stake * selection.odd).toFixed(2) : '0.00';
    bsPayout.textContent = 'S/ ' + payout;
    if (bsSubmit) bsSubmit.disabled = stake <= 0;
  }

  if (bsStake) bsStake.addEventListener('input', updatePayout);

  /* Quick amounts */
  document.querySelectorAll('.betslip-qa').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (bsStake && btn.dataset.amount) {
        bsStake.value = btn.dataset.amount;
        updatePayout();
      }
    });
  });

  /* ═══════════════════════════════════════
     BET SLIP — Submit
  ═══════════════════════════════════════ */
  if (bsSubmit) {
    bsSubmit.addEventListener('click', function () {
      if (!selection) return;
      var stake = parseFloat(bsStake ? bsStake.value : 0);
      if (!stake || stake <= 0) { showMsg('Ingresa un monto válido.', 'error'); return; }
      if (!selection.oddId)     { showMsg('Error: cuota no encontrada.', 'error'); return; }

      bsSubmit.disabled     = true;
      bsSubmit.textContent  = 'Procesando…';
      clearMsg();

      var key = 'ap247-' + Date.now() + '-' + Math.random().toString(36).slice(2, 7);

      fetch(apiBase + 'crear_simple/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
        body: JSON.stringify({
          usuario_id:      userId,
          odd_id:          parseInt(selection.oddId, 10),
          stake:           stake.toFixed(4),
          idempotency_key: key,
        }),
      })
      .then(function (res) {
        return res.json().then(function (data) { return { ok: res.ok, data: data }; });
      })
      .then(function (r) {
        if (r.ok) {
          showMsg('¡Apuesta registrada! ID #' + r.data.id, 'success');
          bsStake.value = '';
          bsPayout.textContent = 'S/ 0.00';
          deselectAll();
          selection = null;
          setTimeout(closeBetSlip, 2200);
        } else {
          var msg = (r.data && (r.data.detail || r.data.non_field_errors)) || 'Error al registrar la apuesta.';
          if (Array.isArray(msg)) msg = msg.join(' ');
          showMsg(msg, 'error');
        }
      })
      .catch(function () { showMsg('Error de conexión. Intenta de nuevo.', 'error'); })
      .finally(function () {
        bsSubmit.disabled = false;
        bsSubmit.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="16" height="16" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> Realizar apuesta';
        updatePayout();
      });
    });
  }

  /* ─── Message helpers ─── */
  function showMsg(text, type) {
    if (!bsMsg) return;
    bsMsg.textContent = text;
    bsMsg.className   = 'betslip-msg is-' + (type || 'success');
  }

  function clearMsg() {
    if (!bsMsg) return;
    bsMsg.textContent = '';
    bsMsg.className   = 'betslip-msg';
  }

})();
