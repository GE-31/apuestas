/* =============================================================
   login_admin.js — Comportamiento específico del login admin
   FairBet Lab

   - Animación de entrada del card
   - Foco en el primer input
   ============================================================= */

(function () {
  'use strict';

  function init() {
    focusFirstInput();
  }

  /* Foco en el primer input vacío del formulario admin */
  function focusFirstInput() {
    var form = document.getElementById('loginAdminForm');
    if (!form) return;
    var inputs = form.querySelectorAll('.admin-form-input');
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
