/* Apuesta24/7 — events.js */
(function () {
  'use strict';

  /* ================================================================
     1. FILTROS Y BÚSQUEDA (lógica existente — sin cambios)
     ================================================================ */
  var grid        = document.getElementById('eventsGrid');
  var emptyMsg    = document.getElementById('eventsEmpty');
  var filterBtns  = document.querySelectorAll('.filter-tab');
  var searchInput = document.getElementById('eventSearch');

  if (grid) {
    var cards        = Array.from(grid.querySelectorAll('.event-card-full'));
    var activeFilter = 'all';
    var searchQuery  = '';

    function applyFilters() {
      var visible = 0;
      cards.forEach(function (card) {
        var sport  = card.dataset.sport  || '';
        var status = card.dataset.status || '';
        var text   = card.textContent.toLowerCase();

        var matchFilter =
          activeFilter === 'all' ||
          activeFilter === sport ||
          (activeFilter === 'live' && status === 'en_vivo');

        var matchSearch = searchQuery === '' || text.indexOf(searchQuery) !== -1;

        var show = matchFilter && matchSearch;
        card.hidden = !show;
        if (show) visible++;
      });
      if (emptyMsg) emptyMsg.hidden = visible > 0;
    }

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

    if (searchInput) {
      searchInput.addEventListener('input', function () {
        searchQuery = searchInput.value.trim().toLowerCase();
        applyFilters();
      });
    }
  }

  /* ================================================================
     2. UTILIDADES
     ================================================================ */

  function getCsrf() {
    var meta = document.getElementById('apuesta247Meta');
    if (meta && meta.dataset.csrf) return meta.dataset.csrf;
    /* fallback: leer cookie csrftoken */
    var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  function getUserId() {
    var meta = document.getElementById('apuesta247Meta');
    return meta ? (parseInt(meta.dataset.userId, 10) || 1) : 1;
  }

  function makeKey() {
    return 'web-' + Date.now() + '-' + Math.random().toString(36).slice(2, 9);
  }

  function fmt(n) {
    return parseFloat(n).toFixed(4);
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function cardOf(eventId) {
    return document.querySelector('.event-card-full[data-event-id="' + eventId + '"]');
  }

  /* ================================================================
     3. DELEGACIÓN DE EVENTOS (un solo listener en document)
     ================================================================ */

  document.addEventListener('click', function (e) {

    /* — Botón de cuota (odd) — */
    var oddBtn = e.target.closest('button.event-item-odd');
    if (oddBtn) { handleOddClick(oddBtn); return; }

    /* — Botón "Apostar ahora" — */
    var betBtn = e.target.closest('button[data-action="open-slip"]');
    if (betBtn) {
      var card = betBtn.closest('.event-card-full');
      if (card) toggleSlip(card, betBtn);
      return;
    }

    /* — Botón "Confirmar apuesta" — */
    var submitBtn = e.target.closest('.bet-slip-submit');
    if (submitBtn) {
      submitBet(submitBtn.dataset.eventId);
      return;
    }

    /* — Botón "Nueva apuesta" — */
    var resetBtn = e.target.closest('.bet-slip-reset');
    if (resetBtn) {
      resetSlip(resetBtn.dataset.eventId);
      return;
    }
  });

  /* Pago potencial en tiempo real */
  document.addEventListener('input', function (e) {
    if (!e.target.classList.contains('bet-slip-stake-input')) return;
    var eventId = e.target.id.replace('stake-', '');
    var card    = cardOf(eventId);
    if (!card) return;
    var selOdd  = card.querySelector('button.event-item-odd[aria-pressed="true"]');
    if (!selOdd) return;
    var stake  = parseFloat(e.target.value) || 0;
    var oddVal = parseFloat(selOdd.dataset.oddVal) || 0;
    updatePayout(eventId, stake, oddVal);
  });

  /* ================================================================
     4. SELECCIÓN DE CUOTA
     ================================================================ */

  function handleOddClick(oddBtn) {
    var card = oddBtn.closest('.event-card-full');
    if (!card) return;

    /* Deseleccionar todas las cuotas de esta tarjeta */
    card.querySelectorAll('button.event-item-odd').forEach(function (b) {
      b.setAttribute('aria-pressed', 'false');
    });
    /* Seleccionar la elegida */
    oddBtn.setAttribute('aria-pressed', 'true');

    var eventId  = card.dataset.eventId;
    var selName  = oddBtn.dataset.seleccion || '—';
    var oddVal   = oddBtn.dataset.oddVal    || '0';
    var mercado  = oddBtn.dataset.mercado   || '';

    /* Actualizar panel de selección */
    var nameEl   = document.getElementById('slip-name-'   + eventId);
    var mktEl    = document.getElementById('slip-mkt-'    + eventId);
    var oddvalEl = document.getElementById('slip-oddval-' + eventId);
    var formEl   = document.getElementById('slip-form-'   + eventId);
    var hintEl   = document.getElementById('slip-hint-'   + eventId);
    var slip     = document.getElementById('slip-'        + eventId);

    if (nameEl)   nameEl.textContent   = selName;
    if (mktEl)    mktEl.textContent    = mercado;
    if (oddvalEl) oddvalEl.textContent = fmt(oddVal);
    if (formEl)   formEl.hidden        = false;
    if (hintEl)   hintEl.hidden        = true;

    /* Abrir slip si estaba cerrado */
    if (slip && slip.hidden) {
      slip.hidden = false;
      setOpenSlipBtn(card, true);
    }

    /* Recalcular pago si ya hay stake */
    var stakeInput = document.getElementById('stake-' + eventId);
    if (stakeInput && stakeInput.value) {
      updatePayout(eventId, parseFloat(stakeInput.value), parseFloat(oddVal));
    }
    /* Focus al input de stake */
    if (stakeInput) {
      setTimeout(function () { stakeInput.focus(); }, 60);
    }
  }

  /* ================================================================
     5. TOGGLE DEL SLIP (botón "Apostar ahora")
     ================================================================ */

  function toggleSlip(card, betBtn) {
    var eventId = card.dataset.eventId;
    var slip    = document.getElementById('slip-' + eventId);
    if (!slip) return;

    var okPanel = document.getElementById('slip-ok-' + eventId);
    var isOpen  = !slip.hidden;

    if (isOpen) {
      /* No cerrar si se está mostrando éxito */
      if (okPanel && !okPanel.hidden) return;
      slip.hidden = true;
      setOpenSlipBtn(card, false);
    } else {
      slip.hidden = false;
      setOpenSlipBtn(card, true);
      /* Si ya hay una cuota seleccionada, hacer focus al stake */
      var selOdd = card.querySelector('button.event-item-odd[aria-pressed="true"]');
      if (selOdd) {
        var stakeInput = document.getElementById('stake-' + eventId);
        if (stakeInput) setTimeout(function () { stakeInput.focus(); }, 60);
      }
    }
  }

  function setOpenSlipBtn(card, open) {
    var btn = card.querySelector('button[data-action="open-slip"]');
    if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  /* ================================================================
     6. CÁLCULO DE PAGO
     ================================================================ */

  function updatePayout(eventId, stake, oddVal) {
    var el = document.getElementById('slip-payout-' + eventId);
    if (!el) return;
    var payout = (stake > 0 && oddVal > 0) ? stake * oddVal : 0;
    el.textContent = 'S/ ' + parseFloat(payout).toFixed(2);
    el.style.color = payout > 0 ? 'var(--green)' : 'var(--text-muted)';
  }

  /* ================================================================
     7. MENSAJES INLINE
     ================================================================ */

  function showMsg(eventId, text, type) {
    var el = document.getElementById('slip-msg-' + eventId);
    if (!el) return;
    el.textContent = text;
    el.className   = 'bet-slip-msg bet-slip-msg-' + type;
    el.hidden      = false;
  }

  function hideMsg(eventId) {
    var el = document.getElementById('slip-msg-' + eventId);
    if (el) el.hidden = true;
  }

  /* ================================================================
     8. ESTADO LOADING DEL BOTÓN
     ================================================================ */

  function setLoading(eventId, loading) {
    var btn = document.getElementById('slip-btn-' + eventId);
    if (!btn) return;
    if (loading) {
      btn.disabled  = true;
      btn.innerHTML =
        '<span class="bet-slip-spinner" aria-hidden="true"></span> Procesando...';
    } else {
      btn.disabled  = false;
      btn.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"' +
        ' width="14" height="14" aria-hidden="true">' +
        '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>' +
        ' Confirmar apuesta';
    }
  }

  /* ================================================================
     9. SUBMIT — POST a /api/apuestas/operaciones/crear_simple/
     ================================================================ */

  function submitBet(eventId) {
    var card = cardOf(eventId);
    if (!card) return;

    var selOdd     = card.querySelector('button.event-item-odd[aria-pressed="true"]');
    var stakeInput = document.getElementById('stake-' + eventId);

    hideMsg(eventId);

    /* Validaciones previas al envío */
    if (!selOdd) {
      showMsg(eventId, 'Selecciona una cuota antes de confirmar.', 'error');
      return;
    }

    var stake = parseFloat(stakeInput ? stakeInput.value : '');
    if (!stake || stake <= 0) {
      showMsg(eventId, 'Ingresa un monto de apuesta válido (mayor a 0).', 'error');
      if (stakeInput) stakeInput.focus();
      return;
    }

    var oddId     = parseInt(selOdd.dataset.oddId, 10);
    var oddVal    = parseFloat(selOdd.dataset.oddVal) || 0;
    var selName   = selOdd.dataset.seleccion || '—';
    var mercado   = selOdd.dataset.mercado   || '—';
    var eventName = card.dataset.eventName   || '—';

    var payload = {
      usuario_id:      getUserId(),
      odd_id:          oddId,
      stake:           fmt(stake),
      idempotency_key: makeKey(),
      ip_origen:       '127.0.0.1'
    };

    setLoading(eventId, true);

    fetch('/api/apuestas/operaciones/crear_simple/', {
      method:  'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken':  getCsrf(),
        'Accept':       'application/json'
      },
      body: JSON.stringify(payload)
    })
    .then(function (res) {
      return res.json().then(function (data) {
        return { ok: res.ok, status: res.status, data: data };
      });
    })
    .then(function (result) {
      setLoading(eventId, false);
      if (result.ok) {
        showSuccess(eventId, eventName, selName, mercado, stake, oddVal);
      } else {
        var msg = extractError(result.data) ||
                  ('Error al crear la apuesta (estado HTTP ' + result.status + ').');
        showMsg(eventId, msg, 'error');
      }
    })
    .catch(function (err) {
      setLoading(eventId, false);
      showMsg(eventId, 'Error de red. Verifica tu conexión e intenta de nuevo.', 'error');
      console.error('[Apuesta24/7] Error al enviar apuesta:', err);
    });
  }

  /* Extrae el primer mensaje de error de una respuesta DRF */
  function extractError(data) {
    if (!data || typeof data !== 'object') return '';
    if (typeof data === 'string') return data;
    if (data.detail)  return String(data.detail);
    if (data.message) return String(data.message);
    if (data.error)   return String(data.error);
    /* Errores de validación por campo */
    var keys = Object.keys(data);
    if (keys.length > 0) {
      var val = data[keys[0]];
      if (Array.isArray(val) && val.length > 0) return keys[0] + ': ' + val[0];
      if (typeof val === 'string') return keys[0] + ': ' + val;
    }
    return 'Error desconocido.';
  }

  /* ================================================================
     10. PANEL DE ÉXITO
     ================================================================ */

  function showSuccess(eventId, eventName, selName, mercado, stake, oddVal) {
    var formEl    = document.getElementById('slip-form-' + eventId);
    var hintEl    = document.getElementById('slip-hint-' + eventId);
    var okPanel   = document.getElementById('slip-ok-'   + eventId);
    var summaryEl = document.getElementById('slip-summary-' + eventId);

    if (formEl)  formEl.hidden  = true;
    if (hintEl)  hintEl.hidden  = true;

    if (summaryEl) {
      var payout = stake * oddVal;
      summaryEl.innerHTML = [
        makeRow('Evento',          escHtml(eventName)),
        makeRow('Selección',       escHtml(selName)),
        makeRow('Mercado',         escHtml(mercado)),
        makeRow('Stake',           escHtml('S/ ' + parseFloat(stake).toFixed(2))),
        makeRow('Cuota',           escHtml(fmt(oddVal))),
        makeRow('Pago potencial',  escHtml('S/ ' + parseFloat(payout).toFixed(2)), 'green'),
        makeRowBadge('Estado', 'Aceptada')
      ].join('');
    }

    if (okPanel) okPanel.hidden = false;
  }

  function makeRow(key, val, colorClass) {
    var cls = colorClass ? ' bet-slip-summary-val-' + colorClass : '';
    return '<div class="bet-slip-summary-row">'
      + '<span class="bet-slip-summary-key">'  + key + '</span>'
      + '<span class="bet-slip-summary-val'    + cls + '">' + val + '</span>'
      + '</div>';
  }

  function makeRowBadge(key, label) {
    return '<div class="bet-slip-summary-row">'
      + '<span class="bet-slip-summary-key">' + escHtml(key) + '</span>'
      + '<span class="bet-slip-summary-badge">'
      + '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"'
      + ' width="10" height="10" aria-hidden="true">'
      + '<polyline points="20 6 9 17 4 12"/></svg>'
      + escHtml(label)
      + '</span></div>';
  }

  /* ================================================================
     11. RESET — "Nueva apuesta en este evento"
     ================================================================ */

  function resetSlip(eventId) {
    var card    = cardOf(eventId);
    var slip    = document.getElementById('slip-'        + eventId);
    var formEl  = document.getElementById('slip-form-'   + eventId);
    var okPanel = document.getElementById('slip-ok-'     + eventId);
    var hintEl  = document.getElementById('slip-hint-'   + eventId);
    var stakeEl = document.getElementById('stake-'       + eventId);
    var payEl   = document.getElementById('slip-payout-' + eventId);

    /* Deseleccionar cuotas */
    if (card) {
      card.querySelectorAll('button.event-item-odd[aria-pressed="true"]').forEach(function (b) {
        b.setAttribute('aria-pressed', 'false');
      });
    }

    /* Limpiar campos */
    if (stakeEl) stakeEl.value       = '';
    if (payEl)   payEl.textContent   = 'S/ 0.00';
    hideMsg(eventId);

    /* Mostrar hint, ocultar form y éxito */
    if (hintEl)  hintEl.hidden  = false;
    if (formEl)  formEl.hidden  = true;
    if (okPanel) okPanel.hidden = true;
    if (slip)    slip.hidden    = false;
  }

})();
