/* =============================================================
   password-toggle.js — Mostrar / ocultar contraseña
   Apuesta24/7

   Uso en HTML:
     <input type="password" data-pwd-toggle-target />
     <button type="button" data-pwd-toggle aria-pressed="false">…</button>

   La validación real siempre ocurre en el backend Django.
   Este script sólo cambia el tipo del input para UX visual.
   ============================================================= */

(function () {
  'use strict';

  function init() {
    var toggles = document.querySelectorAll('[data-pwd-toggle]');

    toggles.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var wrapper = btn.closest('.input-wrapper, .admin-input-wrapper, .form-group');
        var input   = wrapper
          ? wrapper.querySelector('[data-pwd-toggle-target]')
          : btn.previousElementSibling;

        if (!input) return;

        var isVisible = input.type === 'text';
        input.type = isVisible ? 'password' : 'text';

        /* Intercambiar íconos eye / eye-off */
        var eyeOn  = btn.querySelector('.icon-eye');
        var eyeOff = btn.querySelector('.icon-eye-off');
        if (eyeOn)  eyeOn.hidden  = !isVisible;
        if (eyeOff) eyeOff.hidden = isVisible;

        /* Actualizar aria-pressed */
        btn.setAttribute('aria-pressed', String(!isVisible));
        btn.setAttribute('aria-label', isVisible ? 'Mostrar contraseña' : 'Ocultar contraseña');
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
