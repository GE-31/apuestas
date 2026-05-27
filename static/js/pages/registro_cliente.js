/* registro_cliente.js — Apuesta24/7 */
(function () {
  'use strict';

  /* ── Toast ── */
  function showToast(msg, duration) {
    var existing = document.getElementById('regToast');
    if (existing) existing.remove();

    var el = document.createElement('div');
    el.id = 'regToast';
    el.className = 'reg-toast';
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
    el.textContent = msg;
    document.body.appendChild(el);

    requestAnimationFrame(function () {
      el.classList.add('reg-toast--show');
    });

    setTimeout(function () {
      el.classList.remove('reg-toast--show');
      setTimeout(function () { el.remove(); }, 220);
    }, duration || 3400);
  }

  /* ── Botones "Enviar código" ── */
  var btnEmail   = document.getElementById('btnCodigoEmail');
  var btnCelular = document.getElementById('btnCodigoCelular');
  var btnPepInfo = document.getElementById('btnPepInfo');

  if (btnEmail) {
    btnEmail.addEventListener('click', function () {
      var emailInput = document.getElementById('id_email');
      if (!emailInput || !emailInput.value.trim()) {
        showToast('Ingresa tu correo electrónico primero.');
        emailInput && emailInput.focus();
        return;
      }
      showToast('Código enviado a ' + emailInput.value.trim() + ' (integración en proceso).');
    });
  }

  if (btnCelular) {
    btnCelular.addEventListener('click', function () {
      var telInput = document.getElementById('id_telefono');
      if (!telInput || !telInput.value.trim()) {
        showToast('Ingresa tu número de celular primero.');
        telInput && telInput.focus();
        return;
      }
      showToast('Código enviado al ' + telInput.value.trim() + ' (integración en proceso).');
    });
  }

  if (btnPepInfo) {
    btnPepInfo.addEventListener('click', function () {
      showToast(
        'PEP: Persona que desempeña o ha desempeñado funciones públicas prominentes. Esta declaración es parte del proceso de verificación.',
        5000
      );
    });
  }

  /* ── Loading state al enviar ── */
  var form      = document.getElementById('regForm');
  var submitBtn = document.getElementById('regSubmitBtn');

  if (form && submitBtn) {
    form.addEventListener('submit', function () {
      submitBtn.disabled = true;
      var textEl    = submitBtn.querySelector('.reg-submit-text');
      var spinnerEl = submitBtn.querySelector('.reg-submit-spinner');
      if (textEl)    textEl.textContent = 'Registrando...';
      if (spinnerEl) spinnerEl.hidden   = false;
    });
  }

  /* ── Consulta DNI automática (API Peru proxy) ── */
  (function () {
    var dniInput = document.getElementById('id_dni');
    var tipoDoc  = document.getElementById('id_tipo_documento');
    var nomInput = document.getElementById('id_nombres');
    var apInput  = document.getElementById('id_apellidos');
    if (!dniInput || !nomInput || !apInput) return;

    /* Badge de estado junto al campo DNI */
    var badge = document.createElement('span');
    badge.id = 'dniBadge';
    badge.style.cssText = [
      'display:none', 'align-items:center', 'gap:5px',
      'font-size:.72rem', 'font-weight:700', 'margin-top:4px',
      'padding:4px 10px', 'border-radius:8px',
    ].join(';');
    dniInput.closest('.form-group').appendChild(badge);

    function setBadge(type, msg) {
      var colors = {
        loading: 'background:rgba(59,130,246,.12);color:#93c5fd;border:1px solid rgba(59,130,246,.25)',
        ok:      'background:rgba(34,197,94,.1);color:#86efac;border:1px solid rgba(34,197,94,.25)',
        error:   'background:rgba(239,68,68,.1);color:#fca5a5;border:1px solid rgba(239,68,68,.25)',
      };
      badge.style.cssText += ';' + (colors[type] || '');
      badge.style.display = 'inline-flex';
      badge.textContent   = msg;
    }

    function hideBadge() { badge.style.display = 'none'; }

    var timer     = null;
    var abortCtrl = null;

    dniInput.addEventListener('input', function () {
      clearTimeout(timer);

      /* Cancelar cualquier fetch en vuelo */
      if (abortCtrl) { abortCtrl.abort(); abortCtrl = null; }

      var val  = dniInput.value.trim();
      var tipo = tipoDoc ? tipoDoc.value : 'DNI';

      /* Limpiar nombres autocompletados al editar el DNI */
      if (nomInput.dataset.dniAuto === 'true') {
        nomInput.value = '';
        delete nomInput.dataset.dniAuto;
      }
      if (apInput.dataset.dniAuto === 'true') {
        apInput.value = '';
        delete apInput.dataset.dniAuto;
      }

      if (tipo !== 'DNI' || val.length !== 8 || !/^\d{8}$/.test(val)) {
        hideBadge();
        return;
      }

      setBadge('loading', 'Verificando...');

      timer = setTimeout(function () {
        abortCtrl = new AbortController();
        var signal = abortCtrl.signal;

        /* Primero: ¿ya existe este DNI en BD? */
        fetch('/verificar-dni/' + val + '/', { signal: signal })
          .then(function (r) { return r.json(); })
          .then(function (check) {
            if (check.duplicate) {
              setBadge('error', '✗ Ya existe una cuenta registrada con este número de documento');
              return;
            }
            /* No es duplicado: consultar nombre en API Peru */
            setBadge('loading', 'Consultando RENIEC...');
            return fetch('/consultar-dni/' + val + '/', { signal: signal })
              .then(function (r) { return r.json(); })
              .then(function (data) {
                if (data.error) {
                  setBadge('error', '✗ ' + data.error);
                  return;
                }
                if (!nomInput.value || nomInput.dataset.dniAuto === 'true') {
                  nomInput.value = data.nombres;
                  nomInput.dataset.dniAuto = 'true';
                  nomInput.dispatchEvent(new Event('input'));
                }
                if (!apInput.value || apInput.dataset.dniAuto === 'true') {
                  apInput.value = data.apellidos;
                  apInput.dataset.dniAuto = 'true';
                  apInput.dispatchEvent(new Event('input'));
                }
                setBadge('ok', '✓ ' + data.nombres + ' ' + data.apellidos);
              });
          })
          .catch(function (err) {
            if (err.name === 'AbortError') return; /* cancelado intencionalmente */
            setBadge('error', '✗ Error al verificar documento');
          });
      }, 500);
    });

    if (tipoDoc) {
      tipoDoc.addEventListener('change', function () { hideBadge(); });
    }

    [nomInput, apInput].forEach(function (inp) {
      inp.addEventListener('input', function () {
        if (inp.dataset.dniAuto) delete inp.dataset.dniAuto;
      });
    });
  })();

})();
