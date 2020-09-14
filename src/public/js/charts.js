// All of the charts
let charts = {};

// Chart configuration
let chartConfig = [
	{
		id: 'trendChart',
		type: 'bar',
		// options: { legend: false },
		endpoint: 'trend',
		// query: {
			// startDate: '2020-08-01',
			// endDate: '2020-08-08'
		// }
	},
	{
		id: 'breakdownChart',
		type: 'doughnut',
		endpoint: 'breakdown',
	},
	{
		id: 'totalLocationChart',
		type: 'bar',
		options: { legend: false },
		endpoint: 'locations/total',
	},
	{
		id: 'newLocationChart',
		type: 'bar',
		options: { legend: false },
		endpoint: 'locations/new',
	},
];

// Global ChartJS Configuration
Chart.defaults.line.spanGaps = true;

// Draw the charts for the first time
window.onload = () => initCharts();

/*
* Charts
*/
async function initCharts(chartId) {
	// Generate charts
	for (let config of chartConfig) {
		if (chartId && config.id != chartId) continue;

		let data = await getData(config.endpoint, config.query);
		chart = makeChart(config, data);
		charts[config.id] = chart;
	}
}

// Instantiates the Chart()
function makeChart(config, data) {
	let context = document.querySelector('#' + config.id);

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
function reloadChart(id) {
	charts[id].destroy();
	initCharts(id);
}

// Return the appropriate data for this chart
// Automatically generated server side
async function getData(id, query) {
	let queryString = '';
	if (query) {
		queryString = '?' + Object.keys(query).map(k => `${k}=${query[k]}`).join(';');
	}

	let res = await fetch(`/api/${id}${queryString}`);
	let data = await res.json();

	return data;
}
