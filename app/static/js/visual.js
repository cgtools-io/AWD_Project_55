function roundToDecimal(number, decimalPlaces) {
    const factor = 10 ** decimalPlaces;
    return Math.round(number * factor) / factor;
}

document.addEventListener('DOMContentLoaded', () => {
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
                cgtNum.innerHTML = `${data.error}`;
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