// ── main.js — utilidades globales ────────────────────────────────────────────

// Auto-cerrar flash messages después de 5s
document.querySelectorAll('.flash').forEach(flash => {
  setTimeout(() => flash.remove(), 5000);
});

// Marcar enlace activo en la navbar según la URL actual
(function () {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === path) link.classList.add('active');
  });
})();
