/* JS for the table */
window.addEventListener('load', () => loadTable());

const tableBody = document.querySelector('#tableBody');

async function loadTable(limit = 5) {
	if (limit < 5) limit = 5;

	let res = await fetch(`/api/prevalence?limit=${limit}`);
	let data = await res.json();

	tableBody.innerHTML = '';

	for (let item of data) {
		let row = tableBody.insertRow();

		['council', 'per_100k', 'population', 'cases', 'level'].forEach(field => {
			let cell = row.insertCell();
			cell.appendChild(document.createTextNode(item[field]));
		});
	}

	document.querySelector('#tableProgress').classList.add('is-hidden');
}

async function tableLess(e) {
	await loadTable(tableBody.rows.length - 5);
	document.querySelector('#tableMore').disabled = false;

	console.log(tableBody.rows.length);
	if (tableBody.rows.length <= 5) {
		e.disabled = true;
	}
}

async function tableMore(e) {
	let rowsBefore = tableBody.rows.length;
	await loadTable(tableBody.rows.length + 5);
	document.querySelector('#tableLess').disabled = false;

	if (tableBody.rows.length < rowsBefore + 5) {
		e.disabled = true;
	}
}

async function tableAll(e) {
	let rowsBefore = tableBody.rows.length;
	await loadTable(50); // There are less than 50 councils so
	document.querySelector('#tableLess').disabled = false;
}
