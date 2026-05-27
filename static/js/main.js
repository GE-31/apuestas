/* Apuesta24/7 — main.js */

(function () {
  'use strict';

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

  /* Cuenta lateral y recarga de fichas */
  const profileButton = document.getElementById('navProfileButton');
  const rechargeButton = document.getElementById('navRechargeButton');
  const accountDrawer = document.getElementById('accountDrawer');
  const accountBackdrop = document.getElementById('accountDrawerBackdrop');
  const accountClose = document.getElementById('accountDrawerClose');
  const accountForm = document.getElementById('accountRechargeForm');
  const accountAmount = document.getElementById('accountRechargeAmount');
  const accountMessage = document.getElementById('accountRechargeMessage');
  const accountQuickAmounts = document.querySelectorAll('[data-account-amount]');

  function openAccountDrawer() {
    if (!accountDrawer || !accountBackdrop) return;
    accountDrawer.classList.add('is-open');
    accountBackdrop.classList.add('is-open');
    accountDrawer.setAttribute('aria-hidden', 'false');
    accountBackdrop.setAttribute('aria-hidden', 'false');
    document.body.classList.add('account-drawer-open');
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

  function normalizeFichas(value) {
    const number = Number.parseFloat(String(value || '').replace(',', '.'));
    if (!Number.isFinite(number) || number <= 0) return null;
    return number.toFixed(4);
  }

  function setAccountMessage(text, type) {
    if (!accountMessage) return;
    accountMessage.textContent = text || '';
    accountMessage.className = 'account-message';
    if (type) accountMessage.classList.add('is-' + type);
  }

  async function submitAccountRecharge(event) {
    event.preventDefault();
    if (!accountDrawer || !accountAmount) return;

    const amount = normalizeFichas(accountAmount.value);
    const userId = accountDrawer.querySelector('.account-card') ? accountDrawer.querySelector('.account-card').dataset.userId : '';
    const submitButton = accountForm ? accountForm.querySelector('button[type="submit"]') : null;

    if (!amount) {
      setAccountMessage('Ingresa una cantidad valida de fichas.', 'error');
      return;
    }

    if (!userId) {
      setAccountMessage('No se encontro el usuario de la cuenta.', 'error');
      return;
    }

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = 'Recargando...';
    }

    try {
      const response = await fetch('/api/billetera/operaciones/recargar/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
          usuario_id: Number(userId),
          amount: amount,
          idempotency_key: 'recarga-header-' + Date.now()
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

      setAccountMessage('Fichas agregadas correctamente. La recarga quedo guardada.', 'success');
    } catch (err) {
      setAccountMessage('No se pudo recargar fichas. ' + (err.message || ''), 'error');
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = 'Recargar fichas';
      }
    }
  }

  if (profileButton) profileButton.addEventListener('click', openAccountDrawer);
  if (rechargeButton) {
    rechargeButton.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      closeAccountDrawer();
      const walletOpenButton = document.getElementById('btnRecarga');
      if (walletOpenButton) {
        walletOpenButton.click();
        return;
      }
      window.location.href = '/billetera/?recargar=1';
    });
  }
  if (accountClose) accountClose.addEventListener('click', closeAccountDrawer);
  if (accountBackdrop) accountBackdrop.addEventListener('click', closeAccountDrawer);
  if (accountForm) accountForm.addEventListener('submit', submitAccountRecharge);
  accountQuickAmounts.forEach(function (button) {
    button.addEventListener('click', function () {
      if (accountAmount) accountAmount.value = button.dataset.accountAmount || '100.0000';
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
    return parseFloat(n).toFixed(2) + ' fic.';
  }

  function updatePreview() {
    if (!previewOdd) return;
    const stake = parseFloat(stakeInput ? stakeInput.value : 0) || 0;

    previewOdd.textContent   = currentOdd   ? '× ' + currentOdd   : '—';
    previewStake.textContent = stake > 0    ? fmt(stake)           : '0.00 fic.';

    if (currentOdd && stake > 0) {
      previewPayout.textContent = fmt(stake * currentOdd);
    } else {
      previewPayout.textContent = '0.00 fic.';
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

})();
