/* =============================================================
   helpers.js — Utilidades DOM compartidas
   FairBet Lab
   ============================================================= */

'use strict';

var FairBet = window.FairBet || {};

FairBet.helpers = {

  /* Selector único con fallback null */
  qs: function (selector, root) {
    return (root || document).querySelector(selector);
  },

  /* Selector múltiple como Array */
  qsa: function (selector, root) {
    return Array.from((root || document).querySelectorAll(selector));
  },

  /* Añadir listener con guard null */
  on: function (el, event, handler) {
    if (el) el.addEventListener(event, handler);
  },

  /* Debounce */
  debounce: function (fn, wait) {
    var timer;
    return function () {
      var args = arguments;
      var ctx  = this;
      clearTimeout(timer);
      timer = setTimeout(function () { fn.apply(ctx, args); }, wait);
    };
  },

  /* Formatear número decimal con separador #,## */
  formatDecimal: function (n, decimals) {
    return parseFloat(n).toFixed(decimals !== undefined ? decimals : 2);
  },

};

window.FairBet = FairBet;
