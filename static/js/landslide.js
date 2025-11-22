const { setRiskBox, pushAndCap } = LS_helpers;

let soil1Chart, soil2Chart, tiltChart, vibChart;

document.addEventListener("DOMContentLoaded", () => {
    soil1Chart = createChart("soil1", "Soil Moisture 1");
    soil2Chart = createChart("soil2", "Soil Moisture 2");
    tiltChart = createChart("tiltGraph", "Tilt");
    vibChart = createChart("vibration", "Vibration");

    updateLS();
    setInterval(updateLS, 1500);
});

function createChart(id, label) {
    return new Chart(document.getElementById(id), {
        type: "line",
        data: { labels: [], datasets: [{ label, data: [] }] },
        options: { animation: false }
    });
}

async function updateLS() {
    try {
        const resp = await fetch("/api/landslide");
        const d = await resp.json();
        if (d.error) return;

        const t = d.labels.at(-1);

        pushAndCap(soil1Chart.data.labels, t);
        pushAndCap(soil1Chart.data.datasets[0].data, d.soil1.at(-1));
        soil1Chart.update();

        pushAndCap(soil2Chart.data.labels, t);
        pushAndCap(soil2Chart.data.datasets[0].data, d.soil2.at(-1));
        soil2Chart.update();

        pushAndCap(tiltChart.data.labels, t);
        pushAndCap(tiltChart.data.datasets[0].data, d.tilt.at(-1));
        tiltChart.update();

        pushAndCap(vibChart.data.labels, t);
        pushAndCap(vibChart.data.datasets[0].data, d.vibration.at(-1));
        vibChart.update();

        setRiskBox(document.getElementById("landslideDanger"), d.landslide_danger);
        document.getElementById("rainStatus").innerText =
            d.rain.at(-1) ? "Raining" : "No Rain";

    } catch (err) {
        console.log("Landslide API error:", err);
    }
}
