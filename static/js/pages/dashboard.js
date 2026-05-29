/* dashboard.js - Sportsbook Apuesta24/7 */
(function () {
  'use strict';

  var cfg = window.APUESTA_CONFIG || {};
  var userId = cfg.userId || 0;
  var apiBase = cfg.apiBase || '/api/apuestas/operaciones/';
  var csrf = cfg.csrfToken || '';

  var selections = [];
  var activeLeague = null;

  var betSlip = document.getElementById('betSlip');
  var comboSummary = betSlip ? betSlip.querySelector('.betslip-combo-summary') : null;
  if (comboSummary) {
    comboSummary.innerHTML = [
      '<div>',
      '  <span class="betslip-summary-label" id="bsMode">Selecciona una cuota</span>',
      '  <strong class="betslip-summary-total" id="bsTotalOdd">x 0.0000</strong>',
      '</div>',
      '<button class="betslip-clear" id="bsClear" type="button">Limpiar</button>',
    ].join('');

    if (!document.getElementById('bsSelectionsList')) {
      var list = document.createElement('div');
      list.className = 'betslip-selections';
      list.id = 'bsSelectionsList';
      comboSummary.insertAdjacentElement('afterend', list);
    }
  }

  var bsMode = document.getElementById('bsMode');
  var bsTotalOdd = document.getElementById('bsTotalOdd');
  var bsSelectionsList = document.getElementById('bsSelectionsList');
  var bsPayout = document.getElementById('bsPayout');
  var bsStake = document.getElementById('bsStake');
  var bsSubmit = document.getElementById('bsSubmit');
  var bsMsg = document.getElementById('bsMsg');
  var bsClose = document.getElementById('betSlipClose');
  var bsClear = document.getElementById('bsClear');
  var bsCount = betSlip ? betSlip.querySelector('.betslip-count') : null;
  var allGroups = document.querySelectorAll('.sb-group');
  var liveFilterButton = document.querySelector('[data-live-filter]');
  var liveEmpty = document.getElementById('sbLiveEmpty');
  var liveFilterActive = liveFilterButton
    ? liveFilterButton.getAttribute('aria-pressed') === 'true'
    : false;

  document.querySelectorAll('.sb-sport-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var sport = btn.closest('.sb-sport');
      var list = sport ? sport.querySelector('.sb-league-list') : null;
      var isOpen = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
      if (list) list.hidden = isOpen;
    });
  });

  function isLiveMatch(match) {
    return match.classList.contains('sb-match--live') || match.dataset.status === 'en_vivo';
  }

  function applyDashboardFilters() {
    var visibleMatches = 0;

    allGroups.forEach(function (group) {
      var leagueVisible = !activeLeague || group.id === 'liga-' + activeLeague;
      var groupHasVisibleMatch = false;

      group.querySelectorAll('.sb-match').forEach(function (match) {
        var matchVisible = leagueVisible && (!liveFilterActive || isLiveMatch(match));
        match.hidden = !matchVisible;
        if (matchVisible) {
          groupHasVisibleMatch = true;
          visibleMatches += 1;
        }
      });

      group.style.display = groupHasVisibleMatch ? '' : 'none';
    });

    if (liveEmpty) {
      liveEmpty.hidden = !(liveFilterActive && visibleMatches === 0);
    }
  }

  window.applyDashboardFilters = applyDashboardFilters;

  function filterByLeague(ligaKey) {
    activeLeague = ligaKey;
    applyDashboardFilters();
  }

  function clearLeagueFilter() {
    activeLeague = null;
    allGroups.forEach(function (group) { group.style.display = ''; });
    document.querySelectorAll('.sb-league-link').forEach(function (link) {
      link.classList.remove('is-active');
    });
    applyDashboardFilters();
  }

  if (liveFilterButton) {
    liveFilterButton.addEventListener('click', function () {
      liveFilterActive = !liveFilterActive;
      liveFilterButton.classList.toggle('is-active', liveFilterActive);
      liveFilterButton.setAttribute('aria-pressed', liveFilterActive ? 'true' : 'false');

      if (liveFilterActive) {
        activeLeague = null;
        document.querySelectorAll('.sb-league-link').forEach(function (item) {
          item.classList.remove('is-active');
        });
      }

      applyDashboardFilters();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  document.querySelectorAll('.sb-league-link').forEach(function (link) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      var ligaKey = link.dataset.liga;
      var isActive = link.classList.contains('is-active');

      document.querySelectorAll('.sb-league-link').forEach(function (item) {
        item.classList.remove('is-active');
      });

      if (isActive) {
        clearLeagueFilter();
        return;
      }

      link.classList.add('is-active');
      filterByLeague(ligaKey);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  document.addEventListener('click', function (event) {
    var btn = event.target.closest('.sb-odd');
    if (!btn || btn.disabled) return;
    toggleSelection(btn);
  });

  if (bsSelectionsList) {
    bsSelectionsList.addEventListener('click', function (event) {
      var removeBtn = event.target.closest('[data-remove-odd]');
      if (!removeBtn) return;
      removeSelection(removeBtn.dataset.removeOdd);
    });
  }

  function toggleSelection(btn) {
    var oddId = btn.dataset.oddId;
    var eventId = btn.dataset.eventoId;

    if (!oddId) {
      showMsg('Esta cuota no esta disponible.', 'error');
      return;
    }

    if (btn.classList.contains('is-selected')) {
      removeSelection(oddId);
      return;
    }

    selections = selections.filter(function (item) {
      if (
        String(item.eventoId) !== String(eventId) ||
        String(item.mercadoId) !== String(btn.dataset.mercadoId)
      ) {
        return true;
      }
      var oldBtn = document.querySelector('.sb-odd[data-odd-id="' + item.oddId + '"]');
      if (oldBtn) {
        oldBtn.classList.remove('is-selected');
        oldBtn.setAttribute('aria-pressed', 'false');
      }
      return false;
    });

    btn.classList.add('is-selected');
    btn.setAttribute('aria-pressed', 'true');

    selections.push({
      eventoId: btn.dataset.eventoId,
      evento: btn.dataset.evento,
      mercado: btn.dataset.mercado,
      mercadoId: btn.dataset.mercadoId,
      sel: btn.dataset.sel,
      oddId: btn.dataset.oddId,
      odd: parseFloat(btn.dataset.odd) || 0,
    });

    openBetSlip();
    updateBetSlip();
  }

  function removeSelection(oddId) {
    selections = selections.filter(function (item) {
      var remove = String(item.oddId) === String(oddId);
      if (remove) {
        var btn = document.querySelector('.sb-odd[data-odd-id="' + item.oddId + '"]');
        if (btn) {
          btn.classList.remove('is-selected');
          btn.setAttribute('aria-pressed', 'false');
        }
      }
      return !remove;
    });

    if (selections.length === 0) closeBetSlip();
    updateBetSlip();
  }

  function openBetSlip() {
    if (!betSlip) return;
    betSlip.classList.add('is-open');
    betSlip.classList.remove('is-minimized');
    betSlip.setAttribute('aria-hidden', 'false');
  }

  function minimizeBetSlip() {
    if (!betSlip || !betSlip.classList.contains('is-open')) return;
    betSlip.classList.add('is-minimized');
  }

  function expandBetSlip() {
    if (!betSlip) return;
    betSlip.classList.remove('is-minimized');
  }

  function closeBetSlip() {
    if (betSlip) {
      betSlip.classList.remove('is-open', 'is-minimized');
      betSlip.setAttribute('aria-hidden', 'true');
    }
    clearMsg();
  }

  /* Clic en el header cuando está minimizado → expandir */
  if (betSlip) {
    betSlip.querySelector('.betslip-header') &&
    betSlip.querySelector('.betslip-header').addEventListener('click', function (e) {
      if (e.target.closest('#betSlipClose')) return;
      if (betSlip.classList.contains('is-minimized')) expandBetSlip();
    });
  }

  /* Scroll: minimizar al bajar, expandir al subir */
  var lastScrollY = 0;
  window.addEventListener('scroll', function () {
    var currentY = window.scrollY || window.pageYOffset;
    var scrollingDown = currentY > lastScrollY;
    lastScrollY = currentY;
    if (!betSlip || !betSlip.classList.contains('is-open')) return;
    if (scrollingDown && currentY > 120) {
      minimizeBetSlip();
    } else if (!scrollingDown && currentY < 80) {
      expandBetSlip();
    }
  }, { passive: true });

  function deselectAll() {
    document.querySelectorAll('.sb-odd.is-selected').forEach(function (btn) {
      btn.classList.remove('is-selected');
      btn.setAttribute('aria-pressed', 'false');
    });
    selections = [];
  }

  function clearSlip() {
    deselectAll();
    updateBetSlip();
    closeBetSlip();
  }

  if (bsClose) {
    bsClose.addEventListener('click', function (event) {
      event.stopPropagation();
      clearSlip();
    });
  }

  if (bsClear) bsClear.addEventListener('click', clearSlip);

  function getOddsTotal() {
    return selections.reduce(function (total, item) {
      return total * (item.odd || 0);
    }, 1);
  }

  function renderSelections() {
    if (!bsSelectionsList) return;

    if (selections.length === 0) {
      bsSelectionsList.innerHTML = '<div class="betslip-empty">Selecciona cuotas para armar tu boleto.</div>';
      return;
    }

    bsSelectionsList.innerHTML = selections.map(function (item, index) {
      return [
        '<div class="betslip-selection">',
        '  <div class="betslip-selection-main">',
        '    <div class="betslip-selection-top">',
        '      <span class="betslip-selection-index">' + (index + 1) + '</span>',
        '      <span class="betslip-selection-event">' + escapeHtml(item.evento || '') + '</span>',
        '    </div>',
        '    <div class="betslip-selection-market">' + escapeHtml(item.mercado || '') + '</div>',
        '    <div class="betslip-selection-pick">' + escapeHtml(item.sel || '') + '</div>',
        '  </div>',
        '  <div class="betslip-selection-side">',
        '    <strong>x ' + Number(item.odd || 0).toFixed(2) + '</strong>',
        '    <button class="betslip-selection-remove" type="button" data-remove-odd="' + escapeAttr(item.oddId) + '" aria-label="Quitar seleccion">x</button>',
        '  </div>',
        '</div>',
      ].join('');
    }).join('');
  }

  function updateBetSlip() {
    var oddsTotal = selections.length ? getOddsTotal() : 0;

    if (bsCount) bsCount.textContent = String(selections.length);
    if (bsMode) {
      bsMode.textContent = selections.length === 0
        ? 'Selecciona una cuota'
        : selections.length === 1
          ? 'Apuesta simple'
          : 'Apuesta multiple';
    }
    if (bsTotalOdd) bsTotalOdd.textContent = 'x ' + oddsTotal.toFixed(4);

    renderSelections();
    updatePayout();
  }

  function updatePayout() {
    if (!bsStake || !bsPayout) return;

    var stake = parseFloat(bsStake.value) || 0;
    var oddsTotal = selections.length ? getOddsTotal() : 0;
    var payout = stake > 0 && oddsTotal > 0 ? (stake * oddsTotal).toFixed(2) : '0.00';

    bsPayout.textContent = 'S/ ' + payout;

    if (bsSubmit) {
      bsSubmit.disabled = stake <= 0 || selections.length === 0;
      bsSubmit.textContent = selections.length > 1 ? 'Realizar combinada' : 'Realizar apuesta';
    }
  }

  if (bsStake) bsStake.addEventListener('input', updatePayout);

  document.querySelectorAll('.betslip-qa').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (bsStake && btn.dataset.amount) {
        bsStake.value = btn.dataset.amount;
        updatePayout();
      }
    });
  });

  if (bsSubmit) {
    bsSubmit.addEventListener('click', function () {
      if (selections.length === 0) return;

      var stake = parseFloat(bsStake ? bsStake.value : 0);
      if (!stake || stake <= 0) {
        showMsg('Ingresa un monto valido.', 'error');
        return;
      }

      if (selections.some(function (item) { return !item.oddId; })) {
        showMsg('Error: cuota no encontrada.', 'error');
        return;
      }

      bsSubmit.disabled = true;
      bsSubmit.textContent = 'Procesando...';
      clearMsg();

      var isCombinada = selections.length > 1;
      var payload = {
        usuario_id: userId,
        stake: stake.toFixed(4),
        idempotency_key: 'ap247-' + Date.now() + '-' + Math.random().toString(36).slice(2, 7),
      };

      if (isCombinada) {
        payload.odd_ids = selections.map(function (item) {
          return parseInt(item.oddId, 10);
        });
      } else {
        payload.odd_id = parseInt(selections[0].oddId, 10);
      }

      fetch(apiBase + (isCombinada ? 'crear_combinada/' : 'crear_simple/'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
        body: JSON.stringify(payload),
      })
      .then(function (res) {
        return res.json().then(function (data) {
          return { ok: res.ok, data: data };
        });
      })
      .then(function (result) {
        if (result.ok) {
          showMsg((isCombinada ? 'Combinada' : 'Apuesta') + ' registrada. ID #' + result.data.id, 'success');

          // Descontar el stake del saldo visible — el dinero está bloqueado hasta que culmine la apuesta
          if (typeof window.setAccountBalance === 'function') {
            var saldoActual = typeof window.getAccountBalance === 'function' ? window.getAccountBalance() : 0;
            window.setAccountBalance(saldoActual - stake);
          }

          // Actualizar el saldo en el boleto
          var balanceEl = document.querySelector('.betslip-balance strong');
          if (balanceEl) {
            var saldoNum = parseFloat(balanceEl.textContent.replace('S/', '').trim()) || 0;
            balanceEl.textContent = 'S/ ' + Math.max(0, saldoNum - stake).toFixed(2);
          }

          if (bsStake) bsStake.value = '';
          if (bsPayout) bsPayout.textContent = 'S/ 0.00';
          deselectAll();
          updateBetSlip();
          setTimeout(closeBetSlip, 2200);
        } else {
          var msg = (result.data && (result.data.detail || result.data.non_field_errors)) || 'Error al registrar la apuesta.';
          if (Array.isArray(msg)) msg = msg.join(' ');
          showMsg(msg, 'error');
        }
      })
      .catch(function () {
        showMsg('Error de conexion. Intenta de nuevo.', 'error');
      })
      .finally(function () {
        updatePayout();
      });
    });
  }

  function showMsg(text, type) {
    if (!bsMsg) return;
    bsMsg.textContent = text;
    bsMsg.className = 'betslip-msg is-' + (type || 'success');
  }

  function clearMsg() {
    if (!bsMsg) return;
    bsMsg.textContent = '';
    bsMsg.className = 'betslip-msg';
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/`/g, '&#96;');
  }

  function formatLiveCountdown(startValue, periodValue) {
    var start = Date.parse(startValue || '');
    if (!Number.isFinite(start)) return 'Primer tiempo 45:00';

    var elapsedSeconds = Math.max(0, Math.floor((Date.now() - start) / 1000));
    var halfSeconds = 45 * 60;
    var period = Number(periodValue) === 2 ? 2 : 1;
    var label = period === 2 ? 'Segundo tiempo' : 'Primer tiempo';
    var remaining = Math.max(0, halfSeconds - elapsedSeconds);

    var minutes = Math.floor(remaining / 60);
    var seconds = remaining % 60;
    return label + ' ' + String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
  }

  function updateLiveClocks() {
    document.querySelectorAll('.sb-live-clock').forEach(function (clock) {
      clock.textContent = formatLiveCountdown(clock.dataset.liveStart, clock.dataset.livePeriod);
    });
  }

  updateLiveClocks();
  setInterval(updateLiveClocks, 1000);

  updateBetSlip();
})();
