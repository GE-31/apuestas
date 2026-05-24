/* =============================================================
   form-validation.js — Validación visual client-side
   FairBet Lab

   IMPORTANTE: Solo mejora la UX visual.
   La validación de seguridad real ocurre en Django (backend).
   Nunca confiar en validaciones client-side para autenticación.
   ============================================================= */

(function () {
  'use strict';

  /* Marca un input como con error y muestra mensaje */
  function setError(input, message) {
    input.classList.add('form-input--error');
    input.classList.remove('form-input--success');

    var hint = input.closest('.form-group').querySelector('.form-hint');
    if (hint) {
      hint.textContent = message;
      hint.classList.add('form-hint--error');
    }
  }

  /* Limpia el estado de error de un input */
  function clearError(input) {
    input.classList.remove('form-input--error');
    var hint = input.closest('.form-group');
    if (hint) {
      var hintEl = hint.querySelector('.form-hint--error');
      if (hintEl) hintEl.textContent = '';
    }
  }

  /* Valida que el campo no esté vacío */
  function validateRequired(input) {
    if (!input.value.trim()) {
      setError(input, 'Este campo es obligatorio.');
      return false;
    }
    clearError(input);
    return true;
  }

  /* Valida longitud mínima de contraseña (visual, no de seguridad) */
  function validateMinLength(input, min) {
    if (input.value.length > 0 && input.value.length < min) {
      setError(input, 'Mínimo ' + min + ' caracteres.');
      return false;
    }
    return true;
  }

  /* Habilitar/deshabilitar el botón submit */
  function setSubmitState(form, enabled) {
    var btn = form.querySelector('[type="submit"]');
    if (btn) btn.disabled = !enabled;
  }

  /* Mostrar spinner al enviar el formulario */
  function showLoadingState(form) {
    var btn     = form.querySelector('[type="submit"]');
    var text    = btn && btn.querySelector('.btn-text');
    var spinner = btn && btn.querySelector('.btn-spinner');
    if (btn)     btn.disabled = true;
    if (text)    text.hidden = true;
    if (spinner) spinner.hidden = false;
  }

  /* Inicializar validación en tiempo real para inputs */
  function initRealTimeValidation(form) {
    var inputs = form.querySelectorAll('.form-input, .admin-form-input');
    inputs.forEach(function (input) {
      input.addEventListener('blur', function () {
        validateRequired(input);
      });
      input.addEventListener('input', function () {
        if (input.value.trim()) clearError(input);
      });
    });
  }

  /* Inicializar loading state al submit */
  function initSubmitLoading(form) {
    form.addEventListener('submit', function (e) {
      var valid = true;
      var inputs = form.querySelectorAll('.form-input, .admin-form-input');
      inputs.forEach(function (input) {
        if (!validateRequired(input)) valid = false;
      });
      if (!valid) {
        e.preventDefault();
        return;
      }
      showLoadingState(form);
    });
  }

  function init() {
    var forms = document.querySelectorAll(
      '#loginClienteForm, #loginAdminForm'
    );
    forms.forEach(function (form) {
      initRealTimeValidation(form);
      initSubmitLoading(form);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
