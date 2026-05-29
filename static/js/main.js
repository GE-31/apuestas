/* Apuesta24/7 — main.js */

(function () {
  'use strict';

  /* ── Toast notifications ── */
  function showToast(message, type) {
    var container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.style.cssText = [
        'position:fixed', 'top:80px', 'right:20px', 'z-index:99999',
        'display:flex', 'flex-direction:column', 'gap:10px',
        'pointer-events:none', 'max-width:360px'
      ].join(';');
      document.body.appendChild(container);
    }
 
    var toast = document.createElement('div');
    var isSuccess = type !== 'error';
    toast.style.cssText = [
      'background:' + (isSuccess ? 'linear-gradient(135deg,#065f46,#047857)' : 'linear-gradient(135deg,#7f1d1d,#991b1b)'),
      'color:#fff',
      'padding:14px 18px',
      'border-radius:12px',
      'font-size:0.875rem',
      'font-weight:600',
      'line-height:1.4',
      'box-shadow:0 8px 32px rgba(0,0,0,0.45)',
      'border-left:4px solid ' + (isSuccess ? '#10b981' : '#f87171'),
      'pointer-events:auto',
      'opacity:0',
      'transform:translateX(40px)',
      'transition:opacity 0.3s ease,transform 0.3s ease',
      'display:flex',
      'align-items:flex-start',
      'gap:10px',
      'max-width:360px',
      'word-break:break-word'
    ].join(';');

    var icon = isSuccess
      ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18" style="flex-shrink:0;margin-top:1px"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
      : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18" style="flex-shrink:0;margin-top:1px"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';

    toast.innerHTML = icon + '<span>' + message + '</span>';
    container.appendChild(toast);

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
      });
    });

    setTimeout(function () {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(40px)';
      setTimeout(function () { toast.remove(); }, 350);
    }, 4500);
  }

  /* ── Menú mobile ── */
  const toggle = document.getElementById('navToggle');
  const nav    = document.getElementById('mainNav');

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      const open = nav.classList.toggle('open');
      toggle.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', String(open));
    });

    document.addEventListener('click', function (e) {
      if (!nav.contains(e.target) && !toggle.contains(e.target)) {
        nav.classList.remove('open');
        toggle.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        nav.classList.remove('open');
        toggle.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* Cuenta lateral */
  const profileButton = document.getElementById('navProfileButton');
  const rechargeButton = document.getElementById('navRechargeButton');
  const accountDrawer = document.getElementById('accountDrawer');
  const accountBackdrop = document.getElementById('accountDrawerBackdrop');
  const accountClose = document.getElementById('accountDrawerClose');
  const accountWithdrawModal = document.getElementById('accountWithdrawModal');
  const accountWithdrawClose = document.getElementById('accountWithdrawClose');
  const accountWithdrawForm = document.getElementById('accountWithdrawForm');
  const accountYapeNumber = document.getElementById('accountYapeNumber');
  const accountWithdrawAmount = document.getElementById('accountWithdrawAmount');
  const accountWithdrawMessage = document.getElementById('accountWithdrawMessage');
  const accountWithdrawQuickAmounts = document.querySelectorAll('[data-withdraw-amount]');
  const accountShowRecharge = document.getElementById('accountShowRecharge');
  const accountShowWithdraw = document.getElementById('accountShowWithdraw');
  const accountBalanceText = document.getElementById('accountDrawerBalance');
  const accountWithdrawBalance = document.getElementById('accountWithdrawBalance');
  const navProfileBalance = document.getElementById('navProfileBalance');

  function openAccountDrawer(mode) {
    if (!accountDrawer || !accountBackdrop) return;
    accountDrawer.classList.add('is-open');
    accountBackdrop.classList.add('is-open');
    accountDrawer.setAttribute('aria-hidden', 'false');
    accountBackdrop.setAttribute('aria-hidden', 'false');
    document.body.classList.add('account-drawer-open');
    if (mode === 'withdraw') openWithdrawModal();
    else clearWithdrawPanel();
  }

  function closeAccountDrawer() {
    if (!accountDrawer || !accountBackdrop) return;
    accountDrawer.classList.remove('is-open');
    accountBackdrop.classList.remove('is-open');
    accountDrawer.setAttribute('aria-hidden', 'true');
    accountBackdrop.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('account-drawer-open');
  }

  function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(';') : [];
    for (let i = 0; i < cookies.length; i += 1) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + '=') {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return '';
  }

  function getCsrfToken() {
    const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return (tokenInput && tokenInput.value) || getCookie('csrftoken');
  }

  function normalizeAmount(value) {
    const number = Number.parseFloat(String(value || '').replace(',', '.'));
    if (!Number.isFinite(number) || number <= 0) return null;
    return number.toFixed(4);
  }

  function formatMoney(value) {
    const number = Number.parseFloat(String(value || '').replace(',', '.'));
    return Number.isFinite(number) ? number.toFixed(2) : '0.00';
  }

  function normalizeYapeNumber(value) {
    return String(value || '').replace(/\D/g, '').slice(0, 9);
  }

  function getAccountUserId() {
    const card = accountDrawer ? accountDrawer.querySelector('.account-card') : null;
    return card ? card.dataset.userId : '';
  }

  function getAccountBalance() {
    const card = accountDrawer ? accountDrawer.querySelector('.account-card') : null;
    const number = Number.parseFloat((card && card.dataset.accountBalance) || '0');
    return Number.isFinite(number) ? number : 0;
  }

  function setAccountBalance(value) {
    const card = accountDrawer ? accountDrawer.querySelector('.account-card') : null;
    const nextValue = Math.max(0, Number.parseFloat(value) || 0);
    if (card) card.dataset.accountBalance = nextValue.toFixed(4);
    if (accountBalanceText) accountBalanceText.textContent = 'S/ ' + nextValue.toFixed(2);
    if (accountWithdrawBalance) accountWithdrawBalance.textContent = 'S/ ' + nextValue.toFixed(2);
    if (navProfileBalance) navProfileBalance.textContent = 'S/ ' + nextValue.toFixed(2);
    setWalletBalance(nextValue);
  }

  window.setAccountBalance = setAccountBalance;
  window.getAccountBalance = getAccountBalance;

  function setWalletBalance(value) {
    const nextValue = Math.max(0, Number.parseFloat(value) || 0);
    document.querySelectorAll('[data-wallet-balance]').forEach(function (element) {
      element.dataset.walletBalance = nextValue.toFixed(4);
      element.innerHTML = '<span class="wallet-hero-amount-unit">S/</span>\n          ' + nextValue.toFixed(2);
    });
    const modalSaldo = document.getElementById('modalSaldoActual');
    if (modalSaldo) modalSaldo.textContent = 'S/ ' + nextValue.toFixed(2);
  }

  function openRechargeModal() {
    closeAccountDrawer();
    if (window.apuesta247Wallet && typeof window.apuesta247Wallet.openRechargeModal === 'function') {
      window.apuesta247Wallet.openRechargeModal();
      return;
    }
    window.location.href = '/billetera/?recargar=1';
  }

  function setAccountMessage(target, text, type) {
    if (!target) return;
    target.textContent = text || '';
    target.className = 'account-message';
    if (type) target.classList.add('is-' + type);
  }

  function clearWithdrawPanel() {
    if (accountShowWithdraw) accountShowWithdraw.classList.remove('is-active');
    setAccountMessage(accountWithdrawMessage, '', '');
  }

  function openWithdrawModal() {
    if (!accountWithdrawModal) return;
    closeAccountDrawer();
    if (accountWithdrawBalance) accountWithdrawBalance.textContent = 'S/ ' + getAccountBalance().toFixed(2);
    if (accountShowWithdraw) accountShowWithdraw.classList.add('is-active');
    setAccountMessage(accountWithdrawMessage, '', '');
    accountWithdrawModal.classList.add('is-open');
    accountWithdrawModal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('account-withdraw-open');
    if (accountYapeNumber) accountYapeNumber.focus();
  }

  function closeWithdrawModal() {
    if (!accountWithdrawModal) return;
    accountWithdrawModal.classList.remove('is-open');
    accountWithdrawModal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('account-withdraw-open');
    if (accountShowWithdraw) accountShowWithdraw.classList.remove('is-active');
  }

  async function submitAccountWithdraw(event) {
    event.preventDefault();
    if (!accountDrawer || !accountWithdrawAmount) return;

    const amount = normalizeAmount(accountWithdrawAmount.value);
    const userId = getAccountUserId();
    const submitButton = accountWithdrawForm ? accountWithdrawForm.querySelector('button[type="submit"]') : null;
    const yapeNumber = normalizeYapeNumber(accountYapeNumber ? accountYapeNumber.value : '');

    if (!yapeNumber || !/^9\d{8}$/.test(yapeNumber)) {
      setAccountMessage(accountWithdrawMessage, 'Ingresa un numero Yape valido (9 digitos, empieza con 9).', 'error');
      if (accountYapeNumber) accountYapeNumber.focus();
      return;
    }

    if (!amount) {
      setAccountMessage(accountWithdrawMessage, 'Ingresa un monto valido para retirar.', 'error');
      return;
    }

    if (!userId) {
      setAccountMessage(accountWithdrawMessage, 'No se encontro el usuario de la cuenta.', 'error');
      return;
    }

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = 'Retirando...';
    }

    try {
      const response = await fetch('/api/billetera/operaciones/retirar/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
          usuario_id: Number(userId),
          amount: amount,
          yape_number: yapeNumber,
          idempotency_key: 'retiro-header-' + Date.now()
        })
      });

      let detail = '';
      const contentType = response.headers.get('content-type') || '';
      if (contentType.indexOf('application/json') !== -1) {
        const data = await response.json();
        detail = data.detail || data.error || JSON.stringify(data);
      } else {
        detail = await response.text();
      }

      if (!response.ok) throw new Error(detail || 'Respuesta ' + response.status);

      setAccountBalance(getAccountBalance() - Number.parseFloat(amount));
      var successMsg = 'S/ ' + formatMoney(amount) + ' enviado a tu Yape +51 ' + yapeNumber + ' (simulado).';
      setAccountMessage(accountWithdrawMessage, successMsg, 'success');
      showToast(successMsg, 'success');
      if (accountYapeNumber) accountYapeNumber.value = '';
    } catch (err) {
      setAccountMessage(accountWithdrawMessage, 'No se pudo retirar dinero. ' + (err.message || ''), 'error');
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" width="18" height="18" aria-hidden="true"><path d="M12 21V9"/><path d="m7 14 5-5 5 5"/><path d="M5 3h14"/></svg>Simular retiro a Yape';
      }
    }
  }

  if (profileButton) profileButton.addEventListener('click', function () { openAccountDrawer(); });
  if (rechargeButton) {
    rechargeButton.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      openRechargeModal();
    });
  }
  if (accountShowRecharge) accountShowRecharge.addEventListener('click', openRechargeModal);
  if (accountShowWithdraw) accountShowWithdraw.addEventListener('click', openWithdrawModal);
  if (accountClose) accountClose.addEventListener('click', closeAccountDrawer);
  if (accountBackdrop) accountBackdrop.addEventListener('click', closeAccountDrawer);
  if (accountWithdrawClose) accountWithdrawClose.addEventListener('click', closeWithdrawModal);
  if (accountWithdrawModal) {
    accountWithdrawModal.addEventListener('click', function (event) {
      if (event.target === accountWithdrawModal) closeWithdrawModal();
    });
  }
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && accountWithdrawModal && accountWithdrawModal.classList.contains('is-open')) {
      closeWithdrawModal();
    }
  });
  if (accountWithdrawForm) accountWithdrawForm.addEventListener('submit', submitAccountWithdraw);
  accountWithdrawQuickAmounts.forEach(function (button) {
    button.addEventListener('click', function () {
      if (accountWithdrawAmount) accountWithdrawAmount.value = button.dataset.withdrawAmount || '50.00';
    });
  });

  /* ── Calculadora de apuesta en vivo ── */
  const oddsBtns       = document.querySelectorAll('.odds-btn');
  const stakeInput     = document.getElementById('stakeInput');
  const submitBtn      = document.getElementById('submitBet');
  const selectedLabel  = document.getElementById('selectedLabel');
  const selectedOddBadge = document.getElementById('selectedOddBadge');
  const selectedOddValue = document.getElementById('selectedOddValue');
  const previewOdd     = document.getElementById('previewOdd');
  const previewStake   = document.getElementById('previewStake');
  const previewPayout  = document.getElementById('previewPayout');

  let currentOdd   = null;
  let currentLabel = null;

  function fmt(n) {
    return 'S/ ' + parseFloat(n).toFixed(2);
  }

  function updatePreview() {
    if (!previewOdd) return;
    const stake = parseFloat(stakeInput ? stakeInput.value : 0) || 0;

    previewOdd.textContent   = currentOdd   ? '× ' + currentOdd   : '—';
    previewStake.textContent = stake > 0    ? fmt(stake)           : 'S/ 0.00';

    if (currentOdd && stake > 0) {
      previewPayout.textContent = fmt(stake * currentOdd);
    } else {
      previewPayout.textContent = 'S/ 0.00';
    }
  }

  function checkSubmit() {
    if (!submitBtn) return;
    const stake = parseFloat(stakeInput ? stakeInput.value : 0) || 0;
    submitBtn.disabled = !(currentOdd && stake > 0);
  }

  oddsBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      oddsBtns.forEach(function (b) {
        b.classList.remove('selected');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('selected');
      btn.setAttribute('aria-pressed', 'true');

      currentOdd   = parseFloat(btn.dataset.odd);
      currentLabel = btn.dataset.label;

      if (selectedLabel) {
        selectedLabel.textContent = currentLabel;
        selectedLabel.style.color = '';
      }
      if (selectedOddBadge) selectedOddBadge.classList.remove('badge-hidden');
      if (selectedOddValue) selectedOddValue.textContent   = currentOdd.toFixed(2);

      updatePreview();
      checkSubmit();
      if (stakeInput) stakeInput.focus();
    });
  });

  if (stakeInput) {
    stakeInput.addEventListener('input', function () {
      updatePreview();
      checkSubmit();
    });
  }

  /* ── Submit de demostración ── */
  const betForm = document.getElementById('betForm');
  if (betForm) {
    betForm.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!currentOdd || !stakeInput || !stakeInput.value) return;

      const stake  = parseFloat(stakeInput.value);
      const payout = (stake * currentOdd).toFixed(2);

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = '✓ Apuesta registrada';
        submitBtn.style.background = 'var(--green)';
      }

      console.info('[Apuesta24/7] Apuesta simulada:', {
        seleccion: currentLabel,
        cuota:     currentOdd,
        stake:     stake,
        payout:    payout
      });

      setTimeout(function () {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="16" height="16"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> Realizar apuesta';
          submitBtn.style.background = '';
        }
      }, 2500);
    });
  }

  /* ── WebSocket: saldo + eventos en tiempo real ── */
  (function () {
    var metaEl = document.getElementById('apuesta247Meta');
    if (!metaEl) return;

    var userId = metaEl.dataset.userId;
    if (!userId) return;

    var wsProto = location.protocol === 'https:' ? 'wss' : 'ws';

    function connectWs() {
      var ws = new WebSocket(wsProto + '://' + location.host + '/ws/saldo/');

      ws.onmessage = function (evt) {
        try {
          var data = JSON.parse(evt.data);
          if (data.type === 'balance_update') {
            setAccountBalance(data.saldo);
            if (data.mensaje) showToast(data.mensaje, data.mensaje.startsWith('¡') ? 'success' : 'error');
          } else if (data.type === 'evento_update') {
            handleEventoUpdate(data);
          }
        } catch (e) {}
      };

      ws.onclose = function () { setTimeout(connectWs, 3000); };
    }

    connectWs();
  }());

  function handleEventoUpdate(data) {
    var id      = String(data.evento_id);
    var estado  = data.estado;
    var ml      = data.marcador_local;
    var mv      = data.marcador_visitante;
    var liveStartedAt = data.live_started_at || null;
    var livePeriod = (data.live_period !== null && data.live_period !== undefined)
      ? (Number(data.live_period) === 2 ? 2 : 1)
      : null;
    var cuotasVivo = data.cuotas_vivo || {};

    /* ── Actualizar tarjeta del partido en el dashboard ── */
    var matchEl = document.querySelector('.sb-match[data-evento-id="' + id + '"]');
    if (matchEl) {
      matchEl.dataset.status = estado || '';
      if (estado === 'en_vivo') {
        matchEl.dataset.liveStart = liveStartedAt || matchEl.dataset.liveStart || new Date().toISOString();
        matchEl.dataset.livePeriod = String(livePeriod || Number(matchEl.dataset.livePeriod) || 1);
      }
      matchEl.classList.remove('sb-match--live', 'sb-match--done');
      if (estado === 'en_vivo')    matchEl.classList.add('sb-match--live');
      if (estado === 'finalizado') matchEl.classList.add('sb-match--done');

      var infoEl = matchEl.querySelector('.sb-match-info');
      if (infoEl) {
        /* Pulse rojo */
        var pulse = infoEl.querySelector('.sb-live-pulse');
        if (estado === 'en_vivo' && !pulse) {
          pulse = document.createElement('span');
          pulse.className = 'sb-live-pulse';
          pulse.setAttribute('aria-label', 'En vivo');
          infoEl.insertBefore(pulse, infoEl.firstChild);
        } else if (estado !== 'en_vivo' && pulse) {
          pulse.remove();
        }

        var liveBadge = infoEl.querySelector('.sb-live-badge');
        if (estado === 'en_vivo' && !liveBadge) {
          liveBadge = document.createElement('span');
          liveBadge.className = 'sb-live-badge';
          var liveClock = document.createElement('span');
          liveClock.className = 'sb-live-clock';
          liveClock.dataset.livePeriod = String(livePeriod || Number(matchEl.dataset.livePeriod) || 1);
          liveClock.dataset.liveStart = matchEl.dataset.liveStart || liveStartedAt || new Date().toISOString();
          liveClock.textContent = Number(liveClock.dataset.livePeriod) === 2 ? 'Segundo tiempo 45:00' : 'Primer tiempo 45:00';
          liveBadge.appendChild(document.createTextNode('EN VIVO '));
          liveBadge.appendChild(liveClock);
          infoEl.appendChild(liveBadge);
        } else if (estado === 'en_vivo' && liveBadge) {
          var existingClock = infoEl.querySelector('.sb-live-clock');
          if (existingClock) {
            var oldPeriod = Number(existingClock.dataset.livePeriod) || 1;
            var newPeriod = livePeriod || oldPeriod;
            var periodoCambio = livePeriod && (newPeriod !== oldPeriod);
            /* Solo actualizar el inicio si el período cambió — no en updates de marcador */
            if (liveStartedAt && periodoCambio) {
              existingClock.dataset.liveStart = liveStartedAt;
            }
            if (livePeriod) {
              existingClock.dataset.livePeriod = String(newPeriod);
              /* Solo resetear el texto visible si el período realmente cambió */
              if (periodoCambio) {
                existingClock.textContent = newPeriod === 2 ? 'Segundo tiempo 45:00' : 'Primer tiempo 45:00';
              }
            }
          }
        } else if (estado !== 'en_vivo' && liveBadge) {
          liveBadge.remove();
        }

        /* Marcador */
        var scoreEl = infoEl.querySelector('.sb-score');
        if (ml !== null && ml !== undefined && mv !== null && mv !== undefined) {
          if (!scoreEl) {
            scoreEl = document.createElement('span');
            scoreEl.className = 'sb-score';
            infoEl.appendChild(scoreEl);
          }
          scoreEl.textContent = ml + ' - ' + mv;
        }
      }

      /* Deshabilitar cuotas si el partido finalizó o fue anulado */
      if (estado === 'finalizado' || estado === 'anulado' || estado === 'suspendido') {
        matchEl.querySelectorAll('.sb-odd').forEach(function (btn) { btn.disabled = true; });
      } else if (estado === 'en_vivo') {
        matchEl.querySelectorAll('.sb-odd').forEach(function (btn) { btn.disabled = false; });
      }

      /* Actualizar cuotas dinámicas en vivo */
      if (estado === 'en_vivo' && Object.keys(cuotasVivo).length > 0) {
        matchEl.querySelectorAll('.sb-odd:not(.sb-odd--market)').forEach(function (btn) {
          var tipo = btn.dataset.selTipo || '';           // 'local' | 'empate' | 'visitante'
          var nuevaVal = cuotasVivo[tipo];
          if (nuevaVal === null || nuevaVal === undefined) return;

          var valorNuevo  = parseFloat(nuevaVal);
          var valorActual = parseFloat(btn.dataset.odd || '0');
          btn.dataset.odd = valorNuevo.toFixed(4);
          btn.textContent = valorNuevo.toFixed(2);

          /* Flash verde = sube, rojo = baja */
          var clsUp = 'sb-odd--up', clsDn = 'sb-odd--down';
          btn.classList.remove(clsUp, clsDn);
          if (valorNuevo > valorActual)      btn.classList.add(clsUp);
          else if (valorNuevo < valorActual) btn.classList.add(clsDn);
          setTimeout(function (b) { b.classList.remove('sb-odd--up', 'sb-odd--down'); }.bind(null, btn), 1800);
        });
      }

      /* En vivo: ocultar mercados extra, solo 1X2 */
      var drawer = matchEl.querySelector('.sb-market-drawer');
      if (drawer) {
        if (estado === 'en_vivo') drawer.style.display = 'none';
        else drawer.style.display = '';
      }

      if (typeof window.applyDashboardFilters === 'function') {
        window.applyDashboardFilters();
      }
    }

    /* ── Recalcular contador "En vivo" en métricas ── */
    var liveVal = document.querySelector('.sb-metric--red .sb-metric-val');
    if (liveVal) {
      var liveCount = document.querySelectorAll('.sb-match--live').length;
      liveVal.textContent = String(liveCount);
    }

    /* ── Toast informativo ── */
    var labels = { en_vivo: 'EN VIVO', finalizado: 'Finalizado', suspendido: 'Suspendido', anulado: 'Anulado' };
    var label = labels[estado];
    if (label) {
      var nameEl = matchEl && matchEl.querySelector('.sb-team-name');
      var hint   = nameEl ? nameEl.textContent + '…' : 'Partido #' + id;
      showToast(hint + ' — ' + label, estado === 'en_vivo' ? 'success' : 'info');
    }
  }

})();
