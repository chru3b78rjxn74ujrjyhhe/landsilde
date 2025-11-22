const { setRiskBox, pushAndCap } = LS_helpers;

function createMiniChart(ctx) {
    return new Chart(ctx, {
        type: "line",
        data: { labels: [], datasets: [{ data: [], borderWidth: 2 }] },
        options: {
            responsive: true,
            animation: false,
            plugins: { legend: { display: false } },
            scales: { x: { display: false }, y: { display: false } }
        }
    });
}

let miniLS, miniFL, miniCombined;

document.addEventListener("DOMContentLoaded", () => {
    miniLS = createMiniChart(document.getElementById("miniLS"));
    miniFL = createMiniChart(document.getElementById("miniFL"));
    miniCombined = createMiniChart(document.getElementById("miniCombined"));

    fetchUpdate();
    setInterval(fetchUpdate, 1500);
});

async function fetchUpdate() {
    try {
        const resp = await fetch("/api/combined");
        const d = await resp.json();
        if (d.error) return;

        setRiskBox(document.getElementById("landslideRisk"), d.landslide);
        setRiskBox(document.getElementById("floodRisk"), d.flood);
        setRiskBox(document.getElementById("combinedRisk"), d.combined);

        pushAndCap(miniLS.data.labels, d.timestamp);
        pushAndCap(miniLS.data.datasets[0].data, d.landslide);
        miniLS.update();

        pushAndCap(miniFL.data.labels, d.timestamp);
        pushAndCap(miniFL.data.datasets[0].data, d.flood);
        miniFL.update();

        pushAndCap(miniCombined.data.labels, d.timestamp);
        pushAndCap(miniCombined.data.datasets[0].data, d.combined);
        miniCombined.update();

    } catch (e) {
        console.log("ERR:", e);
    }
}
