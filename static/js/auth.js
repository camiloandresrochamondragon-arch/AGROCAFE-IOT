// ── auth.js — lógica de login/registro ──────────────────────────────────────

/**
 * Muestra el formulario del tab indicado y oculta los demás.
 * @param {string} tab - 'login' | 'register' | 'forgot'
 */
function showTab(tab) {
  const forms = ['login', 'register', 'forgot'];

  forms.forEach(f => {
    const form = document.getElementById(`form-${f}`);
    if (form) form.style.display = f === tab ? 'block' : 'none';
  });

  // Actualizar estilos de los tabs principales (login / register)
  document.querySelectorAll('.auth-tab').forEach(btn => {
    const isActive = btn.getAttribute('onclick').includes(`'${tab}'`);
    btn.classList.toggle('active', isActive);
  });
}

/**
 * Alterna la visibilidad de un campo de contraseña.
 * @param {string} inputId - ID del <input type="password">
 * @param {HTMLElement} btn - botón ojo
 */
function togglePwd(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  const isPassword = input.type === 'password';
  input.type = isPassword ? 'text' : 'password';
  btn.textContent = isPassword ? '🙈' : '👁';
  btn.style.opacity = isPassword ? '.9' : '.5';
}
