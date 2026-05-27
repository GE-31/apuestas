/* =============================================================
   login_cliente.js — Comportamiento específico del login cliente
   Apuesta24/7

   - Animación de entrada del panel de formulario
   - Prefill limpio (evita autorellenar usuario de sesiones previas)
   ============================================================= */

(function () {
  'use strict';

  function init() {
    animateFormPanel();
    focusFirstInput();
  }

  /* Animación suave de entrada del panel del formulario */
  function animateFormPanel() {
    var container = document.querySelector('.auth-form-container');
    if (!container) return;

    container.style.opacity = '0';
    container.style.transform = 'translateY(12px)';
    container.style.transition = 'opacity 0.4s ease, transform 0.4s ease';

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        container.style.opacity = '1';
        container.style.transform = 'translateY(0)';
      });
    });
  }

  /* Poner foco en el primer input vacío */
  function focusFirstInput() {
    var form   = document.getElementById('loginClienteForm');
    if (!form) return;
    var inputs = form.querySelectorAll('.form-input');
    for (var i = 0; i < inputs.length; i++) {
      if (!inputs[i].value.trim()) {
        inputs[i].focus();
        break;
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
