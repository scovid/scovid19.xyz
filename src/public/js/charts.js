// All of the charts
let charts = {};

// Chart configuration
let chartConfig = {
	'trendChart': {
		type: 'bar',
		options: { legend: false },
		endpoint: 'trend',
	},

	'breakdownChart': {
		type: 'doughnut',
		endpoint: 'breakdown',
	},
	'totalLocationChart': {
		type: 'bar',
		options: { legend: false },
		endpoint: 'locations/total',
	},
	'newLocationChart': {

		type: 'bar',
		options: { legend: false },
		endpoint: 'locations/new',
	}
};

// Global ChartJS Configuration
Chart.defaults.line.spanGaps = true;

// Draw the charts for the first time
window.onload = () => initCharts();

/*
* Charts
*/
async function initCharts(chartId) {
	// Generate charts
	for (let id of Object.keys(chartConfig)) {
		if (chartId && id != chartId) continue;

		const config = chartConfig[id];

		let data = await getData(config.endpoint, config.query);
		chart = makeChart(id, config, data);
		charts[id] = chart;
	}
}

// Instantiates the Chart()
function makeChart(id, config, data) {
	let context = document.querySelector('#' + id);

	let chart = new Chart(context, {
		type: config.type || 'line',
		data: data,
		options: {
			maintainAspectRatio: false,
			responsive: true,
			...config.options
		}
	});

	chart.key = config.key;

	return chart;
}

// Reloads a charts data
function reloadChart(id, query) {
	charts[id].destroy();
	chartConfig[id].query = query;
	initCharts(id);
}

// Return the appropriate data for this chart
// Automatically generated server side
async function getData(id, query) {
	let queryString = '';
	if (query) {
		queryString = '?' + Object.keys(query).map(k => `${k}=${query[k]}`).join('&');
	}

	let res = await fetch(`/api/${id}${queryString}`);
	let data = await res.json();

	return data;
}
