// landslide.js - landslide charts and UI

let soil1Chart, soil2Chart, tiltChart, vibChart;

function createLine(ctx, label) {
  return new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [{ label, data: [], tension: 0.4 }] },
    options: {
      animation: { duration: 350 },
      plugins: { legend: { display: false } },
      scales: { x: { display: true }, y: { beginAtZero: true } }
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const s1 = document.getElementById("soil1");
  const s2 = document.getElementById("soil2");
  const t  = document.getElementById("tiltGraph");
  const v  = document.getElementById("vibration");

  if (s1) soil1Chart = createLine(s1.getContext("2d"), "Soil 1");
  if (s2) soil2Chart = createLine(s2.getContext("2d"), "Soil 2");
  if (t)  tiltChart = createLine(t.getContext("2d"), "Tilt");
  if (v)  vibChart  = createLine(v.getContext("2d"), "Vibration");

  updateLS();
  setInterval(updateLS, 1500);
});

async function updateLS() {
  try {
    const resp = await fetch("/api/landslide");
    if (!resp.ok) return;
    const d = await resp.json();
    if (!d || d.error) return;

    const t = (d.labels && d.labels[0]) ? d.labels[0] : new Date().toLocaleTimeString();

    if (soil1Chart) {
      window.LS_helpers.pushAndCap(soil1Chart.data.labels, t);
      window.LS_helpers.pushAndCap(soil1Chart.data.datasets[0].data, d.soil1[0]);
      soil1Chart.update();
    }

    if (soil2Chart) {
      window.LS_helpers.pushAndCap(soil2Chart.data.labels, t);
      window.LS_helpers.pushAndCap(soil2Chart.data.datasets[0].data, d.soil2[0]);
      soil2Chart.update();
    }

    if (tiltChart) {
      window.LS_helpers.pushAndCap(tiltChart.data.labels, t);
      window.LS_helpers.pushAndCap(tiltChart.data.datasets[0].data, d.tilt[0]);
      tiltChart.update();
    }

    if (vibChart) {
      window.LS_helpers.pushAndCap(vibChart.data.labels, t);
      window.LS_helpers.pushAndCap(vibChart.data.datasets[0].data, d.vibration[0]);
      vibChart.update();
    }

    window.LS_helpers?.setRiskBox?.(document.getElementById("landslideDanger"), d.landslide_danger || 0);
    const rainStatusEl = document.getElementById("rainStatus");
    if (rainStatusEl) rainStatusEl.innerText = (d.rain && d.rain[0]) ? "Raining" : "No Rain";
  } catch (e) {
    console.warn("updateLS failed:", e);
  }
}
