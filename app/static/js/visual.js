function roundToDecimal(number, decimalPlaces) {
    const factor = 10 ** decimalPlaces;
    return Math.round(number * factor) / factor;
}

document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('valueChart').getContext('2d');
    let pnlChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Total Portfolio Profit/Loss ($)',
                data: [],
                borderColor: '#f1c40f',
                backgroundColor: 'rgba(241, 196, 15, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#f1c40f',
                borderWidth: 2
            }]
        },
        options: {
            scales: {
                x: {
                    ticks: { display: false },
                    grid: { color: '#333' },
                    border: { color: '#f1c40f', width: 1 },
                    position: 'center',
                    axis: { y: 0 },
                    crossesAt: 0
                },
                xTitle: {
                    position: 'bottom',
                    display: true,
                    ticks: { color: "#ccc" },
                    grid: { display: false, drawTicks: false },
                    title: {display: true, text: 'Number of Transactions', color: '#f1c40f'}
                },
                y: {
                    ticks: { color: '#ccc', display: false },
                    grid: { color: '#333' },
                    border: { color: '#f1c40f', width: 1 },
                    title: {display: true, text: "$ Profit/Loss (USD)", color: '#f1c40f'},
                    min: -10, 
                    max: 10
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#ccc' }
                }
            }
        }
    });


    document.getElementById('visualise').addEventListener('click', () => {
        const   summaryId = document.getElementById('summary-select').value,
                csrf_token = document.getElementById('csrf_token').value;
        
        if (!summaryId) {
            return;
        }

        fetch('/get_summary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            body: JSON.stringify({ summary_id: summaryId })
        }).then(response => response.json()).then(data => {
            const   cgtNum = document.getElementById('cgt_num'),
                    costNum = document.getElementById('cost_num'),
                    mvNum = document.getElementById('mv_num'),
                    pnlNum = document.getElementById('pnl_num');

            if(data.error) {
                cgtNum.innerHTML = `${"$ - "}`;
                costNum.innerHTML = `${"$ - "}`;
                mvNum.innerHTML = `${"$ - "}`;
                pnlNum.innerHTML = `${"$ - "}`;
                pnlChart.data.labels = [];
                pnlChart.data.datasets[0] = [];
                pnlChart.options.scales.y.ticks.display = false;
                pnlChart.update();
            } else {
                pnlGraphData = JSON.parse(data.pnl_graph);

                pnlChart.data.labels = pnlGraphData.map(pair => pair[0]);
                pnlChart.data.datasets[0].data = pnlGraphData.map(pair => pair[1]);
                
                pnlChart.options.scales.y.ticks.display = true;
                const minY = Math.min(pnlGraphData.map(pair => pair[1]));
                const yMin = Math.floor(minY - Math.abs(minY * 0.1));
                pnlChart.options.scales.y.min = yMin;
                
                pnlChart.update();
            }
            
            if(data.total_cgt === undefined) {
                cgtNum.innerHTML = `${"$ - "}`;
            }
            else {
                cgtNum.innerHTML = `${"$" + data.total_cgt}`;
            }

            if(data.total_cost === undefined) {
                costNum.innerHTML = `${"$ - "}`;
            }
            else {
                costNum.innerHTML = `${"$" + data.total_cost}`;
            }

            if(data.total_mv === undefined) {
                mvNum.innerHTML = `${"$ - "}`;
            }
            else {
                mvNum.innerHTML = `${"$" + data.total_mv}`;
            }

            if(data.total_mv === undefined || data.total_cost === undefined) {
                pnlNum.innerHTML = `${"$ - "}`;
            }
            else {
                const pnl = roundToDecimal(data.total_mv - data.total_cost, 2);
                if (pnl > 0) {
                    pnlNum.style.color = "#4caf50";
                    pnlNum.innerHTML = `${"$" + (pnl)}`;
                }
                else {
                    pnlNum.style.color = "#ff4081";
                    pnlNum.innerHTML = `${"-$" + (pnl * -1)}`;
                }
                
            }
        }).catch(error => {
            console.error('Error:', error);
        });

    });
});