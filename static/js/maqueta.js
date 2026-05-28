// ── maqueta.js — gráficos y polling en tiempo real ───────────────────────────

const COLOR_TEMP  = '#e74c3c';
const COLOR_HUM   = '#3498db';
const COLOR_SUELO = '#5c8a3c';
const COLOR_LUZ   = '#f39c12';

let chartTemp, chartHum, chartSuelo, chartLuz;

function crearGrafico(id, label, color) {
  const ctx = document.getElementById(id).getContext('2d');
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: label,
        data: [],
        borderColor: color,
        backgroundColor: color + '18',
        borderWidth: 2,
        pointRadius: 2,
        tension: 0.3,
        fill: true,
      }]
    },
    options: {
      responsive: true,
      animation: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { maxTicksLimit: 8, font: { size: 10 } }, grid: { color: '#f0e8d8' } },
        y: { ticks: { font: { size: 10 } }, grid: { color: '#f0e8d8' } }
      }
    }
  });
}

function actualizarGrafico(chart, datos, campo) {
  chart.data.labels = datos.map(d => d.timestamp.slice(11, 19));
  chart.data.datasets[0].data = datos.map(d => d[campo]);
  chart.update('none');
}

function renderTabla(datos) {
  const tbody = document.getElementById('tabla-mediciones');
  if (!datos.length) {
    tbody.innerHTML = '<tr><td colspan="8" class="tabla-loading">Sin datos</td></tr>';
    return;
  }
  const recientes = [...datos].reverse().slice(0, 200);
  tbody.innerHTML = recientes.map(d => `
    <tr>
      <td>${d.timestamp}</td>
      <td>${d.temp}</td>
      <td>${d.hum}</td>
      <td>${d.suelo}</td>
      <td>${d.pres}</td>
      <td>${d.luz}</td>
      <td>${d.bomba ? '<span class="badge badge-ok">ON</span>' : '<span class="badge">OFF</span>'}</td>
      <td>${d.manual ? '<span class="badge badge-wa">Manual</span>' : '—'}</td>
    </tr>`).join('');
}

function actualizarKPIs(ultima) {
  document.getElementById('live-temp').textContent  = ultima.temp + '°C';
  document.getElementById('live-hum').textContent   = ultima.hum + '%';
  document.getElementById('live-suelo').textContent = ultima.suelo + '%';
  document.getElementById('live-luz').textContent   = ultima.luz + ' lux';
  document.getElementById('live-pres').textContent  = ultima.pres + ' hPa';
  document.getElementById('live-bomba').textContent = ultima.bomba ? '🟢 ON' : '⚪ OFF';
}

async function cargarDatos() {
  const desde = document.getElementById('filtro-desde')?.value || '';
  const hasta = document.getElementById('filtro-hasta')?.value || '';

  let url = '/maqueta/api/mediciones?limit=500';
  if (desde) url += `&desde=${desde}`;
  if (hasta) url += `&hasta=${hasta}`;

  try {
    const res   = await fetch(url);
    const datos = await res.json();
    if (!datos.length) return;

    actualizarGrafico(chartTemp,  datos, 'temp');
    actualizarGrafico(chartHum,   datos, 'hum');
    actualizarGrafico(chartSuelo, datos, 'suelo');
    actualizarGrafico(chartLuz,   datos, 'luz');
    renderTabla(datos);
    actualizarKPIs(datos[datos.length - 1]);
  } catch (e) {
    console.warn('Error cargando mediciones:', e);
  }
}

function limpiarFiltrosMaqueta() {
  document.getElementById('filtro-desde').value = '';
  document.getElementById('filtro-hasta').value = '';
  cargarDatos();
}

function copiarCodigo() {
  const txt = document.getElementById('cod-esp').innerText;
  navigator.clipboard.writeText(txt).then(() => {
    const btn = document.querySelector('.code-copy');
    btn.textContent = '¡Copiado!';
    setTimeout(() => btn.textContent = 'Copiar', 2000);
  });
}

// Inicializar
document.addEventListener('DOMContentLoaded', function () {
  chartTemp  = crearGrafico('chart-temp',  'Temperatura',    COLOR_TEMP);
  chartHum   = crearGrafico('chart-hum',   'Humedad aire',   COLOR_HUM);
  chartSuelo = crearGrafico('chart-suelo', 'Humedad suelo',  COLOR_SUELO);
  chartLuz   = crearGrafico('chart-luz',   'Luz',            COLOR_LUZ);

  cargarDatos();
  setInterval(cargarDatos, 5000);
});