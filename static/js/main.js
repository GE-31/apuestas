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

  /* Cuenta lateral */
  const profileButton = document.getElementById('navProfileButton');
  const rechargeButton = document.getElementById('navRechargeButton');
  const accountDrawer = document.getElementById('accountDrawer');
  const accountBackdrop = document.getElementById('accountDrawerBackdrop');
  const accountClose = document.getElementById('accountDrawerClose');
  const accountWithdrawForm = document.getElementById('accountWithdrawForm');
  const accountWithdrawAmount = document.getElementById('accountWithdrawAmount');
  const accountWithdrawMessage = document.getElementById('accountWithdrawMessage');
  const accountWithdrawQuickAmounts = document.querySelectorAll('[data-withdraw-amount]');
  const accountShowRecharge = document.getElementById('accountShowRecharge');
  const accountShowWithdraw = document.getElementById('accountShowWithdraw');
  const accountBalanceText = document.getElementById('accountDrawerBalance');

  function openAccountDrawer(mode) {
    if (!accountDrawer || !accountBackdrop) return;
    accountDrawer.classList.add('is-open');
    accountBackdrop.classList.add('is-open');
    accountDrawer.setAttribute('aria-hidden', 'false');
    accountBackdrop.setAttribute('aria-hidden', 'false');
    document.body.classList.add('account-drawer-open');
    if (mode === 'withdraw') showAccountPanel('withdraw');
    else showAccountPanel('');
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
    setWalletBalance(nextValue);
  }

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

  function showAccountPanel(panel) {
    if (accountWithdrawForm) accountWithdrawForm.hidden = panel !== 'withdraw';
    setAccountMessage(accountWithdrawMessage, '', '');
  }

  async function submitAccountWithdraw(event) {
    event.preventDefault();
    if (!accountDrawer || !accountWithdrawAmount) return;

    const amount = normalizeAmount(accountWithdrawAmount.value);
    const userId = getAccountUserId();
    const submitButton = accountWithdrawForm ? accountWithdrawForm.querySelector('button[type="submit"]') : null;

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
      setAccountMessage(accountWithdrawMessage, 'Retiro simulado registrado correctamente.', 'success');
    } catch (err) {
      setAccountMessage(accountWithdrawMessage, 'No se pudo retirar dinero. ' + (err.message || ''), 'error');
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = 'Retirar dinero';
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
  if (accountShowWithdraw) accountShowWithdraw.addEventListener('click', function () { showAccountPanel('withdraw'); });
  if (accountClose) accountClose.addEventListener('click', closeAccountDrawer);
  if (accountBackdrop) accountBackdrop.addEventListener('click', closeAccountDrawer);
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

})();
