/* ascensus.js – Verhalten von Kopf- und Fußzeile auf ascensus.fit (Menü, Scroll-Linie, Jahreszahl).
   Einbinden: <script src="ascensus.js" defer></script> */
(function () {
  function init() {
    document.querySelectorAll('[data-asc-header]').forEach(function (hdr) {
      var btn = hdr.querySelector('.asc-menu-btn');
      function setOpen(o) {
        hdr.classList.toggle('is-open', o);
        if (btn) { btn.setAttribute('aria-expanded', o ? 'true' : 'false'); btn.setAttribute('aria-label', o ? 'Menü schließen' : 'Menü öffnen'); }
      }
      if (btn) btn.addEventListener('click', function () { setOpen(!hdr.classList.contains('is-open')); });
      hdr.querySelectorAll('.asc-header-nav a').forEach(function (a) { a.addEventListener('click', function () { setOpen(false); }); });
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
      function onScroll() { hdr.classList.toggle('is-scrolled', window.scrollY > 10); }
      onScroll(); window.addEventListener('scroll', onScroll, { passive: true });
    });
    // Zweiter „Ausloggen“-Button im Handy-Menü löst den Haupt-Button (#logoutBtn) aus
    document.querySelectorAll('[data-asc-logout]').forEach(function (b) {
      b.addEventListener('click', function () { var main = document.getElementById('logoutBtn'); if (main && main !== b) main.click(); });
    });
    // „Datenschutzeinstellungen“: Klaro-Dialog, falls Klaro auf der Seite geladen ist – sonst normale Verlinkung
    document.querySelectorAll('[data-asc-consent]').forEach(function (a) {
      a.addEventListener('click', function (e) { if (window.klaro && typeof window.klaro.show === 'function') { e.preventDefault(); window.klaro.show(); } });
    });
    document.querySelectorAll('[data-asc-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
