// ── dashboard.js — lógica de la página Datos IoT ────────────────────────────

// Página actual de la tabla (paginación)
let paginaActual = 1;

/**
 * Carga los municipios del departamento seleccionado
 * y actualiza el <select> de municipios.
 */
async function cargarMunicipios() {
  const dept = document.getElementById('sel-dept').value;
  const sel  = document.getElementById('sel-mun');

  sel.innerHTML = '<option value="">Todos los municipios</option>';

  if (!dept) {
    cargarDatos();
    return;
  }

  try {
    const res  = await fetch(`/datos/api/municipios?departamento=${encodeURIComponent(dept)}`);
    const data = await res.json();
    data.forEach(m => {
      const opt = document.createElement('option');
      opt.value       = m.nombre;
      opt.textContent = m.nombre;
      sel.appendChild(opt);
    });
  } catch (e) {
    console.error('Error cargando municipios:', e);
  }

  // Al cambiar departamento, volvemos a la página 1 y recargamos
  paginaActual = 1;
  cargarDatos();
}

/**
 * Consulta la API con los filtros activos y actualiza
 * la tabla, los KPIs y la paginación.
 */
async function cargarDatos() {
  const dept   = document.getElementById('sel-dept').value;
  const mun    = document.getElementById('sel-mun').value;
  const estado = document.getElementById('sel-estado').value;

  const params = new URLSearchParams();
  if (dept)   params.set('departamento', dept);
  if (mun)    params.set('municipio', mun);
  if (estado) params.set('estado', estado);
  params.set('pagina', paginaActual);

  const tbody = document.getElementById('tabla-body');
  const count = document.getElementById('tabla-count');
  tbody.innerHTML = '<tr><td colspan="8" class="tabla-loading">Cargando datos…</td></tr>';

  try {
    const res  = await fetch(`/datos/api/lecturas?${params.toString()}`);
    const data = await res.json();

    renderTabla(data.lecturas);
    renderKPIs(data.kpis);
    renderPaginacion(data.paginacion);
    renderContadorIdeam(data.paginacion, data.mediciones_crudas);

    const total = data.paginacion ? data.paginacion.total_lecturas : data.lecturas.length;
    count.textContent = `${total.toLocaleString('es-CO')} registro${total !== 1 ? 's' : ''}`;
  } catch (e) {
    tbody.innerHTML = '<tr><td colspan="8" class="tabla-loading">Error al cargar datos.</td></tr>';
    console.error('Error cargando datos:', e);
  }
}

/**
 * Renderiza las filas de la tabla.
 */
function renderTabla(lecturas) {

  const tbody = document.getElementById('tabla-body');

  if (!lecturas.length) {

    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="tabla-loading">
          Sin datos para estos filtros.
        </td>
      </tr>
    `;

    return;
  }

  tbody.innerHTML = lecturas.map(l => `
    <tr>
      <td><strong>${l.departamento}</strong></td>

      <td>${l.municipio}</td>

      <td>
        ${l.temperatura != null
          ? l.temperatura.toFixed(1)
          : '-'}
      </td>

      <td>
        ${l.humedad_suelo != null
          ? l.humedad_suelo + '%'
          : '-'}
      </td>

      <td>
        ${l.precipitacion != null
          ? l.precipitacion + ' mm'
          : '-'}
      </td>

      <td>
        ${l.ph_suelo != null
          ? l.ph_suelo
          : '-'}
      </td>

      <td>${badgeHTML(l.estado)}</td>

      <td>${l.fecha}</td>
    </tr>
  `).join('');
}

/**
 * Actualiza los KPIs del encabezado.
 */
function renderKPIs(kpis) {
  if (!kpis || !Object.keys(kpis).length) return;
  document.getElementById('kpi-temp').textContent   = `${kpis.temp_prom}°C`;
  document.getElementById('kpi-hum').textContent    = `${kpis.hum_prom}%`;
  document.getElementById('kpi-lluvia').textContent = `${kpis.lluvia_prom} mm`;
  document.getElementById('kpi-total').textContent  = kpis.total_sensores.toLocaleString('es-CO');
}

/**
 * Dibuja los controles de paginación (Anterior / página X de Y / Siguiente).
 */
function renderPaginacion(pag) {
  const cont = document.getElementById('paginacion');
  if (!cont || !pag) return;

  if (pag.total_paginas <= 1) {
    cont.innerHTML = '';
    return;
  }

  cont.innerHTML = `
    <button class="pag-btn" id="pag-prev" ${pag.pagina <= 1 ? 'disabled' : ''}>
      ‹ Anterior
    </button>
    <span class="pag-info">
      Página ${pag.pagina} de ${pag.total_paginas}
    </span>
    <button class="pag-btn" id="pag-next" ${pag.pagina >= pag.total_paginas ? 'disabled' : ''}>
      Siguiente ›
    </button>
  `;

  const prev = document.getElementById('pag-prev');
  const next = document.getElementById('pag-next');

  if (prev) prev.onclick = () => {
    if (paginaActual > 1) {
      paginaActual--;
      cargarDatos();
      scrollTablaArriba();
    }
  };

  if (next) next.onclick = () => {
    if (paginaActual < pag.total_paginas) {
      paginaActual++;
      cargarDatos();
      scrollTablaArriba();
    }
  };
}

/**
 * Muestra el contador de origen de datos del IDEAM.
 */
function renderContadorIdeam(pag, crudas) {
  const el = document.getElementById('contador-ideam');
  if (!el) return;

  const lecturas = pag ? pag.total_lecturas : 0;
  const crudasTxt = (crudas || 0).toLocaleString('es-CO');
  const lecturasTxt = lecturas.toLocaleString('es-CO');

  el.innerHTML = `
    <strong>${lecturasTxt}</strong> lecturas agrupadas, derivadas de
    <strong>${crudasTxt}</strong> mediciones reales del IDEAM
  `;
}

/**
 * Lleva la vista al inicio de la tabla al cambiar de página.
 */
function scrollTablaArriba() {
  const t = document.getElementById('tabla-datos');
  if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Devuelve el HTML del badge según el estado.
 */
function badgeHTML(estado) {
  const clases = {
    'Óptimo':          'badge badge-ok',
    'Riego requerido': 'badge badge-wa',
    'Crítico':         'badge badge-lo',
  };
  const cls = clases[estado] || 'badge';
  return `<span class="${cls}">${estado}</span>`;
}

/**
 * Aplica filtros: vuelve a la página 1 y recarga.
 */
function aplicarFiltros() {
  paginaActual = 1;
  cargarDatos();
}

/**
 * Limpia todos los filtros y recarga.
 */
function limpiarFiltros() {
  document.getElementById('sel-dept').value   = '';
  document.getElementById('sel-mun').innerHTML = '<option value="">Todos los municipios</option>';
  document.getElementById('sel-estado').value = '';
  paginaActual = 1;
  cargarDatos();
}