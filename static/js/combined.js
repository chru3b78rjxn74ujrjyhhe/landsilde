// combined.js - small summary charts on the Home dashboard

function createMiniChart(ctx) {
  return new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [{ label: '', data: [], tension: 0.4 }] },
    options: {
      animation: { duration: 400 },
      plugins: { legend: { display: false } },
      scales: {
        x: { display: false },
        y: { display: false }
      }
    }
  });
}

let miniLSChart, miniFLChart, miniCombinedChart;

document.addEventListener("DOMContentLoaded", () => {
  const c1 = document.getElementById("miniLS");
  const c2 = document.getElementById("miniFL");
  const c3 = document.getElementById("miniCombined");

  if (c1) miniLSChart = createMiniChart(c1.getContext("2d"));
  if (c2) miniFLChart = createMiniChart(c2.getContext("2d"));
  if (c3) miniCombinedChart = createMiniChart(c3.getContext("2d"));

  updateCombined();
  setInterval(updateCombined, 1500);
});

async function updateCombined() {
  try {
    const resp = await fetch("/api/combined");
    if (!resp.ok) return;
    const dC = await resp.json();

    if (!dC) return;

    // Update risk boxes
    window.LS_helpers?.setRiskBox?.(document.getElementById("landslideRisk"), dC.landslide || 0);
    window.LS_helpers?.setRiskBox?.(document.getElementById("floodRisk"), dC.flood || 0);
    window.LS_helpers?.setRiskBox?.(document.getElementById("combinedRisk"), dC.combined || 0);

    const t = dC.timestamp || new Date().toLocaleTimeString();

    // push & cap LS
    if (miniLSChart) {
      window.LS_helpers.pushAndCap(miniLSChart.data.labels, t);
      window.LS_helpers.pushAndCap(miniLSChart.data.datasets[0].data, Number(dC.landslide || 0));
      miniLSChart.update();
    }

    if (miniFLChart) {
      window.LS_helpers.pushAndCap(miniFLChart.data.labels, t);
      window.LS_helpers.pushAndCap(miniFLChart.data.datasets[0].data, Number(dC.flood || 0));
      miniFLChart.update();
    }

    if (miniCombinedChart) {
      window.LS_helpers.pushAndCap(miniCombinedChart.data.labels, t);
      window.LS_helpers.pushAndCap(miniCombinedChart.data.datasets[0].data, Number(dC.combined || 0));
      miniCombinedChart.update();
    }

  } catch (e) {
    // silent fail; will retry on next interval
    console.warn("updateCombined failed:", e);
  }
}
