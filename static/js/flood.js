const { setRiskBox, pushAndCap } = LS_helpers;

let waterChart, rainChart, soilChart;

document.addEventListener("DOMContentLoaded", () => {
    waterChart = createLineChart("waterLevel", "Water Level (cm)");
    rainChart = createLineChart("rainIntensity", "Rain Intensity");
    soilChart = createLineChart("soilSat", "Soil Saturation");

    updateFlood();
    setInterval(updateFlood, 1200);
});

function createLineChart(id, label) {
    return new Chart(document.getElementById(id), {
        type: "line",
        data: { labels: [], datasets: [{ label: label, data: [] }] },
        options: { animation: false }
    });
}

async function updateFlood() {
    try {
        const resp = await fetch("/api/flood");
        const d = await resp.json();

        const t = d.labels[d.labels.length - 1];

        pushAndCap(waterChart.data.labels, t);
        pushAndCap(waterChart.data.datasets[0].data, d.water_level.at(-1));
        waterChart.update();

        pushAndCap(rainChart.data.labels, t);
        pushAndCap(rainChart.data.datasets[0].data, d.rain_intensity.at(-1));
        rainChart.update();

        pushAndCap(soilChart.data.labels, t);
        pushAndCap(soilChart.data.datasets[0].data, d.soil_sat.at(-1));
        soilChart.update();

        setRiskBox(document.getElementById("floodDanger"), d.flood_danger);

    } catch (err) {
        console.log("Flood API error:", err);
    }
}
