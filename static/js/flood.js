let waterChart, rainChart, soilChart;

// Create chart helper
function createChart(ctx, label) {
    return new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: label,
                data: [],
                borderWidth: 2,
                pointRadius: 3,
                tension: 0.2
            }]
        },
        options: {
            animation: false,
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function updateChart(chart, label, value) {
    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(value);

    // Limit chart to last 50 points
    if (chart.data.labels.length > 50) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }

    chart.update();
}

async function fetchFloodData() {
    try {
        const res = await fetch("/api/flood");
        const data = await res.json();

        if (data.error) return;

        const label = data.labels[0];

        updateChart(waterChart, label, data.water_level[0]);
        updateChart(rainChart, label, data.rain_intensity[0]);
        updateChart(soilChart, label, data.soil_sat[0]);

        document.getElementById("floodDanger").innerText =
            data.flood_danger.toFixed(0) + "%";

    } catch (err) {
        console.log("Fetch error:", err);
    }
}

window.onload = function () {
    waterChart = createChart(
        document.getElementById("waterLevelChart").getContext("2d"),
        "Water level (cm)"
    );

    rainChart = createChart(
        document.getElementById("rainChart").getContext("2d"),
        "Rain Intensity"
    );

    soilChart = createChart(
        document.getElementById("soilChart").getContext("2d"),
        "Soil Saturation"
    );

    // 🔥 Fetch new readings every 1 second
    setInterval(fetchFloodData, 1000);
    fetchFloodData(); // first immediate update
};
