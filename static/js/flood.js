let waterChart, rainChart, soilSatChart;

document.addEventListener("DOMContentLoaded", () => {

    function createLine(ctx, label) {
        return new Chart(ctx, {
            type: "line",
            data: {
                labels: [],
                datasets: [{
                    label: label,
                    data: [],
                    borderWidth: 2,
                    tension: 0.25
                }]
            },
            options: {
                animation: { duration: 250, easing: "easeInOutQuart" },
                scales: {
                    x: { ticks: { color: "#aaa" } },
                    y: { ticks: { color: "#aaa" } }
                }
            }
        });
    }

    waterChart = createLine(
        document.getElementById("waterLevel").getContext("2d"),
        "Water level (cm)"
    );

    rainChart = createLine(
        document.getElementById("rainIntensity").getContext("2d"),
        "Rain Intensity"
    );

    soilSatChart = createLine(
        document.getElementById("soilSat").getContext("2d"),
        "Soil Saturation"
    );

    setInterval(fetchAndUpdate, 1000);
});


async function fetchAndUpdate() {
    try {
        const resp = await fetch("/api/flood");
        const d = await resp.json();

        if (!d || d.error) return;

        const t = d.labels[0];

        // Always update charts (never freeze)
        pushAndCap(waterChart.data.labels, t);
        pushAndCap(waterChart.data.datasets[0].data, d.water_level[0]);
        waterChart.update();

        pushAndCap(rainChart.data.labels, t);
        pushAndCap(rainChart.data.datasets[0].data, d.rain_intensity[0]);
        rainChart.update();

        pushAndCap(soilSatChart.data.labels, t);
        pushAndCap(soilSatChart.data.datasets[0].data, d.soil_sat[0]);
        soilSatChart.update();

        // danger box
        setRiskBox(document.getElementById("floodDanger"), d.flood_danger);

    } catch (e) {
        console.warn("Flood update error:", e);
    }
}
