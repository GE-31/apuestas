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

  /* ── Toggle contraseña ── */
  document.querySelectorAll('[data-pwd-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var field = btn.closest('.reg-field--pwd');
      if (!field) return;
      var input = field.querySelector('[data-pwd-toggle-target]');
      if (!input) return;

      var shown = input.type === 'text';
      input.type = shown ? 'password' : 'text';
      btn.setAttribute('aria-pressed', String(!shown));

      var eyeOn  = btn.querySelector('.icon-eye');
      var eyeOff = btn.querySelector('.icon-eye-off');
      if (eyeOn)  eyeOn.hidden  = !shown;
      if (eyeOff) eyeOff.hidden = shown;
    });
  });

  /* ── Botones "Generar código" ── */
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
      showToast('Código de verificación enviado a ' + emailInput.value.trim() + ' (funcionalidad en integración).');
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
      showToast('Código de verificación enviado al celular ' + telInput.value.trim() + ' (funcionalidad en integración).');
    });
  }

  if (btnPepInfo) {
    btnPepInfo.addEventListener('click', function () {
      showToast('PEP: Persona que desempeña o ha desempeñado funciones públicas prominentes. Esta declaración es parte del proceso de verificación.', 5000);
    });
  }

  /* ── Validación visual en tiempo real ── */
  document.querySelectorAll('.reg-input').forEach(function (input) {
    input.addEventListener('blur', function () {
      var field = input.closest('.reg-field');
      if (!field) return;
      if (input.required && !input.value.trim()) {
        field.classList.add('reg-field--error');
      } else {
        field.classList.remove('reg-field--error');
      }
    });
  });

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

  /* ── Sincronizar label del select cuando cambia valor ── */
  document.querySelectorAll('select.reg-input').forEach(function (sel) {
    sel.addEventListener('change', function () {
      var field = sel.closest('.reg-field');
      if (field) field.classList.toggle('reg-field--has-value', sel.value !== '');
    });
    /* Marcar al cargar si ya tiene valor */
    if (sel.value) {
      var field = sel.closest('.reg-field');
      if (field) field.classList.add('reg-field--has-value');
    }
  });

})();
