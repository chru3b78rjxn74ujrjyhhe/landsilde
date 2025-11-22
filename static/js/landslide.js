// landslide.js - landslide charts and UI

let soil1Chart, soil2Chart, tiltChart, vibChart;

function createLine(ctx, label) {
  return new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [{ label: label, data: [], tension: 0.4 }] },
    options: {
      animation: { duration: 350 },
      plugins: { legend: { display: false } },
      scales: { x: { display: true }, y: { beginAtZero: true } }
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  soil1Chart = createLine(document.getElementById("soil1").getContext("2d"), "Soil 1");
  soil2Chart = createLine(document.getElementById("soil2").getContext("2d"), "Soil 2");
  tiltChart = createLine(document.getElementById("tiltGraph").getContext("2d"), "Tilt");
  vibChart = createLine(document.getElementById("vibration").getContext("2d"), "Vibration");

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

    if (soil1Chart.data.labels.length === 0) {
      soil1Chart.data.labels = d.labels.slice();
      soil1Chart.data.datasets[0].data = d.soil1.slice();

      soil2Chart.data.labels = d.labels.slice();
      soil2Chart.data.datasets[0].data = d.soil2.slice();

      tiltChart.data.labels = d.labels.slice();
      tiltChart.data.datasets[0].data = d.tilt.slice();

      vibChart.data.labels = d.labels.slice();
      vibChart.data.datasets[0].data = d.vibration.slice();

      soil1Chart.update();
      soil2Chart.update();
      tiltChart.update();
      vibChart.update();

      window.LS_helpers?.setRiskBox?.(document.getElementById("landslideDanger"), d.landslide_danger || 0);
      document.getElementById("rainStatus") && (document.getElementById("rainStatus").innerText = (d.rain && d.rain[0]) ? "Raining" : "No Rain");
      return;
    }

    // add last points
    window.LS_helpers.pushAndCap(soil1Chart.data.labels, t);
    window.LS_helpers.pushAndCap(soil1Chart.data.datasets[0].data, d.soil1[0]);
    soil1Chart.update();

    window.LS_helpers.pushAndCap(soil2Chart.data.labels, t);
    window.LS_helpers.pushAndCap(soil2Chart.data.datasets[0].data, d.soil2[0]);
    soil2Chart.update();

    window.LS_helpers.pushAndCap(tiltChart.data.labels, t);
    window.LS_helpers.pushAndCap(tiltChart.data.datasets[0].data, d.tilt[0]);
    tiltChart.update();

    window.LS_helpers.pushAndCap(vibChart.data.labels, t);
    window.LS_helpers.pushAndCap(vibChart.data.datasets[0].data, d.vibration[0]);
    vibChart.update();

    window.LS_helpers?.setRiskBox?.(document.getElementById("landslideDanger"), d.landslide_danger || 0);
    document.getElementById("rainStatus") && (document.getElementById("rainStatus").innerText = (d.rain && d.rain[0]) ? "Raining" : "No Rain");

  } catch (e) {
    console.warn("updateLS failed:", e);
  }
}
