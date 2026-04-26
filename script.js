let processes = [];

function addProcess() {
    const pid = document.getElementById('pid').value;
    const arrival = document.getElementById('arrival').value;
    const burst = document.getElementById('burst').value;

    processes.push({
        pid: Number(pid),
        arrival: Number(arrival),
        burst: Number(burst)
    });

    updateTable();
}

function updateTable() {
    const table = document.getElementById('table');
    table.innerHTML = `
        <tr>
            <th>PID</th>
            <th>Arrival</th>
            <th>Burst</th>
        </tr>
    `;

    processes.forEach(p => {
        table.innerHTML += `
            <tr>
                <td>${p.pid}</td>
                <td>${p.arrival}</td>
                <td>${p.burst}</td>
            </tr>
        `;
    });
}

async function runSimulation() {
    const res = await fetch('/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ processes })
    });

    const data = await res.json();

    document.getElementById('output').innerText =
        JSON.stringify(data, null, 2);
}
