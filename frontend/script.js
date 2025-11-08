const input = document.getElementById('nl-input');
const runBtn = document.getElementById('run-btn');
const sqlPreview = document.getElementById('sql-preview');
const resultsTable = document.getElementById('results-table');

async function runQuery() {
  const natural_language = input.value.trim();
  if (!natural_language) return;

  runBtn.disabled = true;
  sqlPreview.textContent = 'Generating SQL...';
  resultsTable.innerHTML = '';

  try {
    const response = await fetch('http://127.0.0.1:8000/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ natural_language }),
    });

    if (!response.ok) {
      const problem = await response.json();
      throw new Error(problem.detail || 'Request failed');
    }

    const data = await response.json();
    sqlPreview.textContent = data.sql;
    renderTable(data.columns, data.rows);
  } catch (error) {
    sqlPreview.textContent = error.message;
  } finally {
    runBtn.disabled = false;
  }
}

function renderTable(columns, rows) {
  if (!columns.length) {
    resultsTable.innerHTML = '<caption>No rows returned.</caption>';
    return;
  }

  const thead = document.createElement('thead');
  const headRow = document.createElement('tr');
  columns.forEach((col) => {
    const th = document.createElement('th');
    th.textContent = col;
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);

  const tbody = document.createElement('tbody');
  rows.forEach((row) => {
    const tr = document.createElement('tr');
    row.forEach((value) => {
      const td = document.createElement('td');
      td.textContent = value;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  resultsTable.innerHTML = '';
  resultsTable.appendChild(thead);
  resultsTable.appendChild(tbody);
}

runBtn.addEventListener('click', runQuery);
input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
    runQuery();
  }
});
