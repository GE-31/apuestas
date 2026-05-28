/* Apuesta24/7 - Billetera */
(function () {
  'use strict';

  /* ── Modal ── */
  var modal          = document.getElementById('walletRechargeModal');
  var openBtn        = document.getElementById('btnRecarga');
  var closeBtn       = document.getElementById('walletModalClose');
  var resultCloseBtn = document.getElementById('walletResultClose');
  var methodButtons  = document.querySelectorAll('.wallet-method-card');
  var views          = document.querySelectorAll('[data-wallet-view]');
  var backButtons    = document.querySelectorAll('[data-wallet-back]');

  /* Amount view */
  var amountLogo     = document.getElementById('walletAmountLogo');
  var amountTitle    = document.getElementById('walletAmountTitle');
  var amountText     = document.getElementById('walletAmountText');
  var amountInput    = document.getElementById('walletAmountInput');
  var operationInput = document.getElementById('walletOperationInput');
  var applyPromoBtn  = document.getElementById('walletApplyPromo');
  var generateQrBtn  = document.getElementById('walletGenerateQr');

  /* QR view */
  var qrLogo         = document.getElementById('walletQrLogo');
  var qrTitle        = document.getElementById('walletQrTitle');
  var qrMethodLabel  = document.getElementById('walletQrMethodLabel');
  var qrAmount       = document.getElementById('walletQrAmount');
  var qrMethod       = document.getElementById('walletQrMethod');
  var messageBox     = document.getElementById('walletRechargeMessage');
  var confirmBtn     = document.getElementById('walletConfirmRecharge');

  /* Result view */
  var resultCard   = document.getElementById('walletResultCard');
  var resultTitle  = document.getElementById('walletResultTitle');
  var resultMethod = document.getElementById('walletResultMethod');
  var resultAmount = document.getElementById('walletResultAmount');
  var resultStatus = document.getElementById('walletResultStatus');
  var errorDetail  = document.getElementById('walletErrorDetail');

  /* Header balance */
  var modalSaldo = document.getElementById('modalSaldoActual');

  var selectedMethod = 'Yape';
  var selectedLogo   = '';
  var selectedAmount = '';
  var lastFocused    = null;

  function getUserId() {
    var meta = document.getElementById('apuesta247Meta') || document.getElementById('fairbetMeta');
    return parseInt((meta && meta.dataset.userId) || '0', 10);
  }

  function syncBalance() {
    if (!modalSaldo) return;
    var balEl = document.querySelector('[data-wallet-balance]');
    if (balEl) {
      var val = parseFloat(balEl.dataset.walletBalance || '0').toFixed(2);
      modalSaldo.textContent = 'S/ ' + val;
    }
  }

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
    syncBalance();
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
    selectedLogo   = '';
    selectedAmount = '';
    if (amountInput) amountInput.value = '';
    if (operationInput) operationInput.value = '';
    if (applyPromoBtn) {
      applyPromoBtn.textContent = 'APLICAR';
      applyPromoBtn.removeAttribute('style');
    }
    if (confirmBtn) {
      confirmBtn.disabled = false;
      confirmBtn.textContent = 'Simular recarga exitosa';
    }
    clearMessage();
    setResultState(false, '', 'Yape', '');
    setView('methods');
  }

  function normalizeAmount(value) {
    var raw = String(value || '').trim().replace(',', '.');
    var number = Number.parseFloat(raw);
    if (!Number.isFinite(number) || number <= 0) return null;
    return number.toFixed(2);
  }

  function updateAmountView(method, logo) {
    selectedMethod = method;
    selectedLogo   = logo || '';
    if (amountLogo) {
      amountLogo.src = logo || '';
      amountLogo.alt = method;
    }
    if (amountTitle) {
      amountTitle.textContent = 'Recarga en ' + method.toUpperCase() + ' desde S/ 5 hasta S/ 500.';
    }
    if (amountText) {
      amountText.textContent = 'Ingresa el monto a recargar. Si tienes un código promocional, escríbelo y presiona "APLICAR" para hacerlo efectivo. Luego genera tu código QR.';
    }
    if (amountInput) {
      amountInput.value = '';
      amountInput.focus();
    }
  }

  function updateQrView(method, logo, amount) {
    selectedMethod = method;
    selectedLogo   = logo || '';
    selectedAmount = amount;
    if (qrLogo)        { qrLogo.src = logo || ''; qrLogo.alt = method; }
    if (qrTitle)       qrTitle.textContent = 'Carga con ' + method;
    if (qrMethodLabel) qrMethodLabel.textContent = method.toUpperCase();
    if (qrAmount)      qrAmount.textContent = 'S/ ' + amount;
    if (qrMethod)      qrMethod.textContent = method;
    if (confirmBtn) {
      confirmBtn.disabled = false;
      confirmBtn.textContent = 'Simular recarga exitosa';
    }
    var qrCanvas = document.getElementById('walletQrCanvas');
    if (qrCanvas) {
      qrCanvas.innerHTML = '';
      var ref = 'AP' + Date.now().toString(36).toUpperCase().slice(-6);
      var qrText = 'APUESTA247://' + method.toLowerCase() + '?monto=' + amount + '&ref=' + ref;
      if (typeof QRCode !== 'undefined') {
        new QRCode(qrCanvas, {
          text: qrText,
          width: 180,
          height: 180,
          colorDark: '#1e1b4b',
          colorLight: '#ffffff',
          correctLevel: QRCode.CorrectLevel.M
        });
      }
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
    messageBox.textContent = detail
      ? 'No se pudo cargar saldo. ' + detail
      : 'No se pudo cargar saldo.';
  }

  function extractBackendDetail(data) {
    if (!data) return '';
    if (typeof data === 'string') return data;
    if (data.detail) return String(data.detail);
    if (data.error) return String(data.error);
    if (data.non_field_errors) return String(data.non_field_errors);
    try { return JSON.stringify(data); } catch (e) { return ''; }
  }

  function getCookie(name) {
    var cookies = document.cookie ? document.cookie.split(';') : [];
    for (var i = 0; i < cookies.length; i++) {
      var c = cookies[i].trim();
      if (c.substring(0, name.length + 1) === name + '=') {
        return decodeURIComponent(c.substring(name.length + 1));
      }
    }
    return '';
  }

  function getCsrfToken() {
    var input = modal ? modal.querySelector('input[name="csrfmiddlewaretoken"]') : null;
    return (input && input.value) || getCookie('csrftoken');
  }

  function setResultState(isError, detail, method, amount) {
    if (!resultCard) return;
    resultCard.classList.toggle('is-error', isError);
    if (resultTitle) {
      resultTitle.textContent = isError
        ? 'No se pudo cargar saldo.'
        : 'Carga realizada correctamente.';
    }
    if (resultMethod) resultMethod.textContent = method || selectedMethod;
    if (resultAmount) resultAmount.textContent = 'S/ ' + (amount || selectedAmount || '0.00');
    if (resultStatus) resultStatus.textContent = isError ? 'error' : 'completado';
    if (errorDetail) {
      errorDetail.textContent = detail ? 'Detalle: ' + detail : '';
      errorDetail.classList.toggle('is-visible', Boolean(isError && detail));
    }
  }

  function confirmRecharge() {
    var amount = normalizeAmount(selectedAmount);
    if (!amount) {
      showErrorMessage('Ingresa un monto válido entre S/ 5 y S/ 500.');
      return;
    }
    var userId = getUserId();
    if (!userId) {
      showErrorMessage('No se encontró información de usuario.');
      return;
    }
    if (confirmBtn) {
      confirmBtn.disabled = true;
      confirmBtn.textContent = 'Procesando...';
    }
    clearMessage();

    var payload = {
      usuario_id: userId,
      amount: amount,
      idempotency_key: 'recarga-web-' + Date.now() + '-' + Math.random().toString(36).slice(2, 8)
    };

    fetch('/api/billetera/operaciones/recargar/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify(payload)
    }).then(function (response) {
      var ct = response.headers.get('content-type') || '';
      var bodyPromise = ct.indexOf('application/json') !== -1
        ? response.json()
        : response.text();
      return bodyPromise.then(function (data) {
        if (!response.ok) {
          throw new Error(extractBackendDetail(data) || 'Respuesta ' + response.status);
        }
        return data;
      });
    }).then(function () {
      setResultState(false, '', selectedMethod, selectedAmount);
      setView('result');
    }).catch(function (err) {
      var detail = err && err.message ? err.message : '';
      showErrorMessage(detail);
      setResultState(true, detail, selectedMethod, selectedAmount);
    }).finally(function () {
      if (confirmBtn) {
        confirmBtn.disabled = false;
        confirmBtn.textContent = 'Simular recarga exitosa';
      }
    });
  }

  /* ── Event bindings ── */
  if (openBtn)        openBtn.addEventListener('click', openModal);
  if (closeBtn)       closeBtn.addEventListener('click', closeModal);
  if (resultCloseBtn) resultCloseBtn.addEventListener('click', closeModal);

  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) closeModal();
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && modal && modal.classList.contains('is-open')) closeModal();
  });

  methodButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var method = btn.dataset.method || 'Yape';
      var logo   = btn.dataset.logo   || '';
      updateAmountView(method, logo);
      setView('amount');
    });
  });

  backButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      setView('methods');
    });
  });

  if (amountInput) {
    amountInput.addEventListener('input', function () {
      var normalized = normalizeAmount(amountInput.value);
      if (normalized) selectedAmount = normalized;
    });
  }

  if (applyPromoBtn) {
    applyPromoBtn.addEventListener('click', function () {
      var code = operationInput ? operationInput.value.trim() : '';
      if (!code) {
        if (operationInput) operationInput.focus();
        return;
      }
      applyPromoBtn.textContent = 'Aplicado';
      applyPromoBtn.style.background = '#dcfce7';
      applyPromoBtn.style.borderColor = '#16a34a';
      applyPromoBtn.style.color = '#15803d';
      setTimeout(function () {
        applyPromoBtn.textContent = 'APLICAR';
        applyPromoBtn.removeAttribute('style');
      }, 2500);
    });
  }

  if (generateQrBtn) {
    generateQrBtn.addEventListener('click', function () {
      var amount = normalizeAmount(amountInput ? amountInput.value : '');
      if (!amount) {
        if (amountInput) {
          amountInput.focus();
          amountInput.style.outline = '3px solid #dc2626';
          setTimeout(function () { amountInput.style.outline = ''; }, 1800);
        }
        return;
      }
      selectedAmount = amount;
      updateQrView(selectedMethod, selectedLogo, amount);
      setView('qr');
    });
  }

  if (confirmBtn) {
    confirmBtn.addEventListener('click', confirmRecharge);
  }

  if (window.location.search.indexOf('recargar=1') !== -1) {
    openModal();
  }

})();
