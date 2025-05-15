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
            const cgtNum = document.getElementById('cgt_num');

            if(data.error) {
                cgtNum.innerHTML = `${data.error}`;
            }

            if(data.total_cgt === undefined) {
                cgtNum.innerHTML = `${"$ - "}`;
            }
            else {
                cgtNum.innerHTML = `${"$" + data.total_cgt}`;
            }
        }).catch(error => {
            console.error('Error:', error);
        });

    });
});