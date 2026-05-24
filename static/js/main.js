/* FairBet Lab — main.js */

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

      console.info('[FairBet Lab] Apuesta simulada:', {
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
