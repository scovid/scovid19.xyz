// All of the charts
let charts = {};

// Global ChartJS Configuration
Chart.defaults.line.spanGaps = true;

// Draw the charts for the first time
initCharts();

/*
* Event handlers
*/
// Toggles the extra stat cards
function toggleExtraCards(e) {
	let moreStats = document.getElementById('moreStats');

	e.children[0].classList.toggle('fa-chevron-up');
	e.children[0].classList.toggle('fa-chevron-down');
	moreStats.classList.toggle('closed');
}

/*
* Charts
*/
async function initCharts() {
	let chartConfig = [
		{
			key: 'trend',
			selector: '#trendChart',
			type: 'bar',
			options: { legend: false },
		},
		{
			key: 'breakdown',
			selector: '#breakdownChart',
			type: 'doughnut',
		},
		{
			key: 'locations',
			selector: '#locationChart',
			type: 'bar',
			options: { legend: false },
		},
	];

	// Generate charts
	for (let config of chartConfig) {
		let data = await getData(config.key);
		chart = makeChart(config, data);
		charts[config.key] = chart;
	}
}

// Instantiates the Chart()
function makeChart(config, data) {
	let context = document.querySelector(config.selector);

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

// Return the appropriate data for this chart
// Automatically generated server side
async function getData(key) {
	let res = await fetch(`/api/${key}`);
	let data = await res.json();

	return data;
}
