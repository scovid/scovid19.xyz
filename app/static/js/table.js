/*
TODO:
- Support pagination or load more/load less
- Display sort arrows on headers
- Support search filtering
- Use JS doc comments
- Add a way to set the default sorting
*/

class SimpleTable {
	/*
	selector: The DOM selector for the table
	headers: Map of header string and key for the row object
	rows: Array of objects of the table rows (or a function that returns this - async supported)
	rowLimit: Max number of rows to load at once, pass -1 to disable (Default = -1)
	*/
	constructor(selector, headers, rows) {
		this.selector = selector;
		this.headers = headers;
		this.rows = rows;

		this.table = {};
		this.state = {};
	}

	async init() {
		const container = document.querySelector(this.selector);
		if (!container) {
			console.error(`SimpleTable Error: '${this.selector}' not found`);
			return;
		}

		let table = document.createElement('table');
		table.classList = 'table is-striped is-hoverable is-fullwidth slider closed';
		this.table.table = table;

		// Progress bar
		let progress = document.createElement('progress');
		progress.classList = 'progress';

		container.appendChild(table);
		container.appendChild(progress);

		// Head
		let tableHead = table.createTHead();
		let headerRow = tableHead.insertRow();
		this.table.head = tableHead;

		for (let [header, rowKey] of this.headers) {
			let cell = document.createElement('th');
			cell.appendChild(document.createTextNode(header));
			cell.setAttribute('row-key', rowKey);

			// Sort by header on click
			cell.addEventListener('click', () => {
				if (!Array.isArray(this.rows) || this.rows.length == 0) return;

				const parseNum = num => Number(num.toString().replace(',', ''));

				// Sort data
				const isNumeric = Number.isFinite(parseNum(this.rows[0][rowKey]));
				if (isNumeric) {
					this.rows = this.rows.sort((a, b) => parseNum(b[rowKey]) - parseNum(a[rowKey]));
				} else {
					this.rows = this.rows.sort((a, b) => a[rowKey] > b[rowKey]);
				}

				// Store state and handle reversing
				if (this.state.sorted === rowKey) {
					this.rows = this.rows.reverse();
					this.state.sorted = `${rowKey}_reversed`;
				} else {
					this.state.sorted = rowKey;
				}

				// Reload data
				this.buildRows();
			});
			headerRow.appendChild(cell);
		}

		// Body
		let tableBody = document.createElement('tbody');
		this.table.body = tableBody;

		// Load rows
		if (typeof this.rows === 'function') {
			let isAsync = this.rows[Symbol.toStringTag] === 'AsyncFunction';
			this.rows = isAsync ? await this.rows() : this.rows();
		}

		table.appendChild(tableBody);
		this.buildRows();

		// document.querySelector(this.selector).classList.add('is-hidden');
		progress.classList.add('is-hidden');
	}

	buildRows() {
		this.table.body.innerHTML = '';

		// Add the sort arrow indicator when sorting
		if (this.state && this.state.sorted) {
			let sortedOn = this.state.sorted;
			let reversed = false;

			if (sortedOn.endsWith("_reversed")) {
				reversed = true;
				sortedOn = sortedOn.replace("_reversed", "");
			}

			// Delete all sort indicators
			document.querySelectorAll(".sort-indicator").forEach(indicator => indicator.parentNode.removeChild(indicator));

			// Add a sort indicator on the current column
			const indicator = reversed ? `<i class="fas fa-arrow-up"></i>` : `<i class="fas fa-arrow-down"></i>`;
			document.querySelector(`[row-key="${sortedOn}"]`).innerHTML += `<span class="sort-indicator" style="margin-left: 10px;">${indicator}</span>`;
		}

		// Build rows
		for (let row of this.rows) {
			let newRow = this.table.body.insertRow();
			for (let [_, rowKey] of this.headers) {
				let cell = newRow.insertCell();
				cell.appendChild(document.createTextNode(row[rowKey]));
			}
		}
	}
}

/* EXAMPLE
let headers = new Map();
headers.set('Council', 'council');
headers.set('Cases per 100k', 'per_100k');
headers.set('Population', 'population');
headers.set('Cases', 'cases');
headers.set('Estimated Level', 'level');

const dataLoader = async () => {
	let res = await fetch(`/api/prevalence`);
	return await res.json();
};

new SimpleTable('#statsTable', headers, dataLoader).init();
*/
