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

  document.querySelectorAll('.sb-sport-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var sport = btn.closest('.sb-sport');
      var list = sport ? sport.querySelector('.sb-league-list') : null;
      var isOpen = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
      if (list) list.hidden = isOpen;
    });
  });

  function filterByLeague(ligaKey) {
    activeLeague = ligaKey;
    allGroups.forEach(function (group) {
      group.style.display = (!ligaKey || group.id === 'liga-' + ligaKey) ? '' : 'none';
    });
  }

  function clearLeagueFilter() {
    activeLeague = null;
    allGroups.forEach(function (group) { group.style.display = ''; });
    document.querySelectorAll('.sb-league-link').forEach(function (link) {
      link.classList.remove('is-active');
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

      var main = document.querySelector('.sb-main');
      if (main) main.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
    betSlip.setAttribute('aria-hidden', 'false');
  }

  function closeBetSlip() {
    if (betSlip) {
      betSlip.classList.remove('is-open');
      betSlip.setAttribute('aria-hidden', 'true');
    }
    clearMsg();
  }

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

  updateBetSlip();
})();
