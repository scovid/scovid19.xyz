/* Misc JS and event listeners */

// Color theme ('light' or 'dark')
let theme = 'light';

window.addEventListener('load', () => {
	// Enable dark mode if state is stored
	const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
	theme = window.localStorage.getItem('color_theme') || (prefersDark ? 'dark' : 'light');
	setTheme();

	// TODO: Add range limits to pickers
	flatpickr('.datepicker', {});
});

/*
 * Event handlers
 */
// Toggle color theme between light and dark
function toggleDarkMode() {
	theme = theme == 'dark' ? 'light' : 'dark';
	setTheme();
}

// Toggles the extra stat cards
function toggleExtraCards(e) {
	let moreStats = document.getElementById('moreStats');

	e.children[0].classList.toggle('fa-chevron-up');
	e.children[0].classList.toggle('fa-chevron-down');
	moreStats.classList.toggle('closed');
}

function showSettings(type) {
	const settings_id = type.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`) + '_settings';

	document.querySelector(`#${settings_id}`).setAttribute('type', type);
	document.querySelector(`#${settings_id}`).classList.add('is-active');
}

function saveSettings(e) {
	let query = {};

	// Grab all fields which have a data-param attr set
	const type = e.getAttribute('type');
	for (let field of e.querySelectorAll('[data-param')) {
		let key = field.getAttribute('data-param');
		let value = field.value;

		if (key && value) query[key] = value;
	}

	// Reload the chart using our new querystring
	reloadChart(type, query);
	closeSettings(e);

	// Check if this chart has an 'OnSave' function defined
	// If so call it
	const fn = window[`${type}OnSave`];
	if (typeof fn == 'function') fn();
}

function closeSettings(e) {
	e.setAttribute('type', null);
	e.classList.remove('is-active');
}

// Set the color theme
function setTheme() {
	const btn = document.querySelector('#themeToggle');

	// If on then disable and set icon to moon
	if (theme == 'light') {
		btn.classList = ['fas fa-moon fa-2x'];
		document.querySelector('#darkly').disabled = true;

		// If off then enable and set icon to sun
	} else {
		btn.classList = ['fas fa-sun fa-2x'];
		document.querySelector('#darkly').disabled = false;
	}

	// Save in localStorage
	window.localStorage.setItem('color_theme', theme);
}
