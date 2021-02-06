/* All of the chart logic lives here */
let charts = {};

Chart.defaults.global.tooltips.mode = "single";
Chart.defaults.global.tooltips.enabled = true;
Chart.defaults.global.tooltips.callbacks.label = (item, data) => {
	// Line charts have a yLabel property
	if (item && item.yLabel) {
		return item.yLabel.toLocaleString("en")
	}

	// Pie/dougnuts do not have the yLable property so figure it out from the $data
	return data.datasets[0].data[item.index].toLocaleString("en")
};

// Need to copy the defaults into the dougnut due to a bug
// https://github.com/chartjs/Chart.js/issues/5539
Chart.defaults.doughnut.tooltips = Chart.defaults.global.tooltips;

// Change the default color to look decent in both dark mode and light mode
Chart.defaults.global.defaultFontColor = 'grey'

// Global ChartJS Configuration
Chart.defaults.line.spanGaps = true;

/*
* Charts
*/
async function initCharts(chartConfig) {
	Promise.all(
		Object.keys(chartConfig).map(async chartId => {
			const config = chartConfig[chartId];
			let data = await getData(config.endpoint, config.query);

			if (data.error) {
				// TODO: This could be improved
				console.error(`Error response from ${config.endpoint}`);
				const err = document.createElement('p');
				err.innerHTML = 'Failed to load data';
				err.style = 'text-align: center; margin-top: 15px';
				err.classList.add('is-family-monospace');
				document.querySelector('#' + chartId).parentElement.prepend(err);
			} else {
				chart = makeChart(chartId, config, data);
				charts[chartId] = chart;
			}
		})
	);
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
