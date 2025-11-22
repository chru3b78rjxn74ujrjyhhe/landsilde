// flood.js - handles flood page charts and UI

let waterChart, rainChart, soilSatChart;

function createLineChart(ctx, label) {
  return new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [{ label: label, data: [], tension: 0.4 }] },
    options: {
      animation: { duration: 300 },
      plugins: { legend: { display: false } },
      scales: {
        x: { display: true },
        y: { beginAtZero: true }
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const w = document.getElementById("waterLevel");
  const r = document.getElementById("rainIntensity");
  const s = document.getElementById("soilSat");

  if (w) waterChart = createLineChart(w.getContext("2d"), "Water level");
  if (r) rainChart = createLineChart(r.getContext("2d"), "Rain intensity");
  if (s) soilSatChart = createLineChart(s.getContext("2d"), "Soil saturation");

  // initial fetch + continuous polling
  fetchAndUpdate();
  setInterval(fetchAndUpdate, 1000);
});

async function fetchAndUpdate() {
  try {
    const resp = await fetch("/api/flood");
    if (!resp.ok) return;
    const d = await resp.json();
    if (!d || d.error) return;

    const t = (d.labels && d.labels[0]) ? d.labels[0] : new Date().toLocaleTimeString();

    // Always push latest point (prevents freeze)
    if (waterChart) {
      window.LS_helpers.pushAndCap(waterChart.data.labels, t);
      window.LS_helpers.pushAndCap(waterChart.data.datasets[0].data, d.water_level[0]);
      waterChart.update();
    }

    if (rainChart) {
      window.LS_helpers.pushAndCap(rainChart.data.labels, t);
      window.LS_helpers.pushAndCap(rainChart.data.datasets[0].data, d.rain_intensity[0]);
      rainChart.update();
    }

    if (soilSatChart) {
      window.LS_helpers.pushAndCap(soilSatChart.data.labels, t);
      window.LS_helpers.pushAndCap(soilSatChart.data.datasets[0].data, d.soil_sat[0]);
      soilSatChart.update();
    }

    window.LS_helpers?.setRiskBox?.(document.getElementById("floodDanger"), d.flood_danger || 0);
  } catch (e) {
    console.warn("fetchAndUpdate (flood) failed:", e);
  }
}
