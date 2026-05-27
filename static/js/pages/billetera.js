/* FairBet Lab - Billetera */
(function () {
  'use strict';

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
      tabs.forEach(function (item) {
        item.classList.remove('active');
        item.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      applyMovFilter(tab.dataset.filter || 'all');
    });
  });

  const btnMovs = document.getElementById('btnMovimientos');
  if (btnMovs) {
    btnMovs.addEventListener('click', function () {
      const card = document.getElementById('movementsCard');
      if (card) card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  const modal = document.getElementById('walletRechargeModal');
  const openBtn = document.getElementById('btnRecarga');
  const closeBtn = document.getElementById('walletModalClose');
  const resultCloseBtn = document.getElementById('walletResultClose');
  const methodButtons = document.querySelectorAll('.wallet-method-card');
  const views = document.querySelectorAll('[data-wallet-view]');
  const backButtons = document.querySelectorAll('[data-wallet-back]');
  const amountTitle = document.getElementById('walletAmountTitle');
  const amountText = document.getElementById('walletAmountText');
  const amountInput = document.getElementById('walletAmountInput');
  const operationInput = document.getElementById('walletOperationInput');
  const quickAmounts = document.querySelectorAll('[data-amount]');
  const generateQrBtn = document.getElementById('walletGenerateQr');
  const confirmBtn = document.getElementById('walletConfirmRecharge');
  const qrTitle = document.getElementById('walletQrTitle');
  const qrAmount = document.getElementById('walletQrAmount');
  const qrMethod = document.getElementById('walletQrMethod');
  const messageBox = document.getElementById('walletRechargeMessage');
  const resultCard = document.getElementById('walletResultCard');
  const resultTitle = document.getElementById('walletResultTitle');
  const resultMethod = document.getElementById('walletResultMethod');
  const resultAmount = document.getElementById('walletResultAmount');
  const resultStatus = document.getElementById('walletResultStatus');
  const errorDetail = document.getElementById('walletErrorDetail');

  let selectedMethod = 'Yape';
  let selectedAmount = '100.0000';
  let lastFocused = null;

  function setView(name) {
    views.forEach(function (view) {
      view.classList.toggle('is-active', view.dataset.walletView === name);
    });
    clearMessage();
  }

  function openModal() {
    if (!modal) return;
    lastFocused = document.activeElement;
    resetFlow();
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('wallet-modal-open');
    if (closeBtn) closeBtn.focus();
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('wallet-modal-open');
    if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
  }

  function resetFlow() {
    selectedMethod = 'Yape';
    selectedAmount = '100.0000';
    if (amountInput) amountInput.value = selectedAmount;
    if (operationInput) operationInput.value = '';
    quickAmounts.forEach(function (button) {
      button.classList.toggle('is-selected', button.dataset.amount === selectedAmount);
    });
    if (confirmBtn) {
      confirmBtn.disabled = false;
      confirmBtn.textContent = 'Confirmar carga';
    }
    clearMessage();
    setResultState(false, '', selectedMethod, selectedAmount);
    setView('methods');
  }

  function normalizeAmount(value) {
    const raw = String(value || '').trim().replace(',', '.');
    const number = Number.parseFloat(raw);
    if (!Number.isFinite(number) || number <= 0) return null;
    return number.toFixed(4);
  }

  function updateAmountView(method) {
    selectedMethod = method;
    if (amountTitle) amountTitle.textContent = 'Carga con ' + method;
    if (amountText) {
      amountText.textContent = method === 'C\u00f3digo manual'
        ? 'Ingresa la cantidad de fichas y registra un c\u00f3digo opcional para demo.'
        : 'Elige la cantidad de fichas y genera un QR demostrativo.';
    }
    if (amountInput) amountInput.focus();
  }

  function updateQrView(method, amount) {
    selectedMethod = method;
    selectedAmount = amount;
    if (qrTitle) qrTitle.textContent = method === 'QR demostrativo' ? 'QR demostrativo' : 'Carga con ' + method;
    if (qrAmount) qrAmount.textContent = amount + ' FV';
    if (qrMethod) qrMethod.textContent = method;
    if (confirmBtn) {
      confirmBtn.disabled = false;
      confirmBtn.textContent = 'Confirmar carga';
    }
  }

  function clearMessage() {
    if (!messageBox) return;
    messageBox.className = 'wallet-message';
    messageBox.textContent = '';
  }

  function showErrorMessage(detail) {
    if (!messageBox) return;
    messageBox.className = 'wallet-message is-error';
    messageBox.textContent = detail ? 'No se pudo cargar fichas. ' + detail : 'No se pudo cargar fichas.';
  }

  function extractBackendDetail(data) {
    if (!data) return '';
    if (typeof data === 'string') return data;
    if (data.detail) return String(data.detail);
    if (data.error) return String(data.error);
    if (data.non_field_errors) return String(data.non_field_errors);

    try {
      return JSON.stringify(data);
    } catch (err) {
      return '';
    }
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
    const input = modal ? modal.querySelector('input[name="csrfmiddlewaretoken"]') : null;
    return (input && input.value) || getCookie('csrftoken');
  }

  async function confirmRecharge() {
    const amount = normalizeAmount(selectedAmount);
    if (!amount) {
      showErrorMessage('Ingresa una cantidad valida de fichas.');
      return;
    }

    if (confirmBtn) {
      confirmBtn.disabled = true;
      confirmBtn.textContent = 'Confirmando...';
    }

    clearMessage();

    const payload = {
      usuario_id: 1,
      amount: amount,
      idempotency_key: 'recarga-web-' + Date.now()
    };

    try {
      const response = await fetch('/api/billetera/operaciones/recargar/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(payload)
      });

      let data = null;
      const contentType = response.headers.get('content-type') || '';
      if (contentType.indexOf('application/json') !== -1) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        throw new Error(extractBackendDetail(data) || 'Respuesta ' + response.status);
      }

      setResultState(false, '', selectedMethod, amount);
      setView('result');
    } catch (err) {
      const detail = err && err.message ? err.message : '';
      showErrorMessage(detail);
      setResultState(true, detail, selectedMethod, amount);
    } finally {
      if (confirmBtn) {
        confirmBtn.disabled = false;
        confirmBtn.textContent = 'Confirmar carga';
      }
    }
  }

  function setResultState(isError, detail, method, amount) {
    if (!resultCard) return;
    resultCard.classList.toggle('is-error', isError);

    if (resultTitle) {
      resultTitle.textContent = isError
        ? 'No se pudo cargar fichas.'
        : 'Fichas agregadas correctamente.';
    }
    if (resultMethod) resultMethod.textContent = method || selectedMethod;
    if (resultAmount) resultAmount.textContent = (amount || selectedAmount) + ' FV';
    if (resultStatus) resultStatus.textContent = isError ? 'error' : 'completado';

    if (errorDetail) {
      errorDetail.textContent = detail ? 'Detalle del backend: ' + detail : '';
      errorDetail.classList.toggle('is-visible', Boolean(isError && detail));
    }
  }

  if (openBtn) openBtn.addEventListener('click', openModal);
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (resultCloseBtn) resultCloseBtn.addEventListener('click', closeModal);

  if (modal) {
    modal.addEventListener('click', function (event) {
      if (event.target === modal) closeModal();
    });
  }

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && modal && modal.classList.contains('is-open')) {
      closeModal();
    }
  });

  methodButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      const method = button.dataset.method || 'Yape';
      if (button.dataset.directQr === 'true') {
        updateQrView(method, '100.0000');
        setView('qr');
        return;
      }

      updateAmountView(method);
      setView('amount');
    });
  });

  backButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      setView('methods');
    });
  });

  quickAmounts.forEach(function (button) {
    button.addEventListener('click', function () {
      selectedAmount = button.dataset.amount || '100.0000';
      if (amountInput) amountInput.value = selectedAmount;
      quickAmounts.forEach(function (item) {
        item.classList.toggle('is-selected', item === button);
      });
    });
  });

  if (amountInput) {
    amountInput.addEventListener('input', function () {
      const normalized = normalizeAmount(amountInput.value);
      if (normalized) selectedAmount = normalized;
      quickAmounts.forEach(function (button) {
        button.classList.toggle('is-selected', button.dataset.amount === normalized);
      });
    });
  }

  if (generateQrBtn) {
    generateQrBtn.addEventListener('click', function () {
      const amount = normalizeAmount(amountInput ? amountInput.value : selectedAmount);
      if (!amount) {
        showErrorMessage('Ingresa una cantidad valida de fichas.');
        return;
      }
      updateQrView(selectedMethod, amount);
      setView('qr');
    });
  }

  if (confirmBtn) {
    confirmBtn.addEventListener('click', confirmRecharge);
  }
})();
